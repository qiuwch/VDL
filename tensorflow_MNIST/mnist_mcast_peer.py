"""A very simple MNIST classifier.
See extensive documentation at
http://tensorflow.org/tutorials/mnist/beginners/index.md
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import argparse
import sys

import input_data
import tensorflow as tf
import numpy as np
import cPickle as pickle
import time

import Queue
import threading

import params
import socket_util

class SockListenThread(threading.Thread):
    """
    Thread class that listens for socket message receiving. It terminates when stop() is called.
    """

    def __init__(self, sock, self_IP, inc_msg_q, num_peers, ret_val):
        super(SockListenThread, self).__init__()
        self.sock = sock
        self.self_IP = self_IP
        self.inc_msg_q = inc_msg_q
        self.num_peers = num_peers
        self.ret_val = ret_val
        self.rcv_msg_num = 0
        self._stop = threading.Event()

    def run(self):
        while not self.stopped():
            self.rcv_msg_num = socket_util.socket_recv_chucked_data(self.sock, self.self_IP, self.inc_msg_q, self.num_peers, self.rcv_msg_num)
        # thread terminating
        time.sleep(1)
        self.rcv_msg_num = socket_util.socket_recv_chucked_data(self.sock, self.self_IP, self.inc_msg_q, self.num_peers, self.rcv_msg_num)
        self.ret_val.put(self.rcv_msg_num)
    
    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()


os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' # Disable Tensorflow debugging logs
np.set_printoptions(threshold=np.nan)
FLAGS = None

def main(_):
  '''
  Main function running a MNIST Tensorflow multicast peer program
  '''
  
  num_peers, my_peer_ID, batch_size, num_rounds = parse_cmd_args()
  # Import data
  mnist = input_data.read_data_sets(FLAGS.data_dir, one_hot=True)

  tf_model_objects = create_model()
  sess = tf.InteractiveSession()
  tf.global_variables_initializer().run()

  sock, self_IP, mcast_destination = socket_util.set_up_UDP_mcast_peer()
  socket_util.await_start_mcast(sock)
  
  t0 = time.time()
  msg_sent, rcv_msg_num = train(sess, mnist, sock, self_IP, mcast_destination, num_peers, my_peer_ID, batch_size, num_rounds, tf_model_objects)
  
  t1 = time.time()
  socket_util.close_UDP_mcast_peer(sock)
  accuracy = test_model(sess, mnist, tf_model_objects)
  
  t2 = time.time()
  print_results(accuracy, t0, t1, t2, num_peers, batch_size, num_rounds, msg_sent, rcv_msg_num)


def parse_cmd_args():
  '''
  Parse command line arguments
  @return (Number of peers, My peer ID, Batch size, Number of rounds per machine)
  '''  
  num_peers = int(sys.argv[1])
  my_peer_ID = int(sys.argv[2]) - 1
  batch_size = int(sys.argv[3])
  num_rounds = int(sys.argv[4])
  
  return (num_peers, my_peer_ID, batch_size, num_rounds)
  
def create_model():
  '''
  Create the Tensorflow model for MNIST task
  @return (x, W, b, y, y_, train_step) as in the Tensorflow model
  '''
   
  x = tf.placeholder(tf.float32, [None, 784])
  W = tf.Variable(tf.zeros([784, 10]))
  b = tf.Variable(tf.zeros([10]))
  y = tf.matmul(x, W) + b

  # Define loss and optimizer
  y_ = tf.placeholder(tf.float32, [None, 10])

  # The raw formulation of cross-entropy,
  #
  #   tf.reduce_mean(-tf.reduce_sum(y_ * tf.log(tf.nn.softmax(y)),
  #                                 reduction_indices=[1]))
  #
  # can be numerically unstable.
  #
  # So here we use tf.nn.softmax_cross_entropy_with_logits on the raw
  # outputs of 'y', and then average across the batch.
  cross_entropy = tf.reduce_mean(
      tf.nn.softmax_cross_entropy_with_logits(labels=y_, logits=y))
  train_step = tf.train.GradientDescentOptimizer(0.5).minimize(cross_entropy)
  
  return (x, W, b, y, y_, train_step)

def train(sess, mnist, sock, self_IP, mcast_destination, num_peers, my_peer_ID, batch_size, num_rounds, tf_model_objects):
  '''
  Train the Tensorflow MNIST model
  @param sess Tensorflow session
  @param mnist MNIST data
  @params sock The socket to use
  @param self_IP The IP address of self
  @param mcast_destination Destination multicast address
  @param num_peers Number of peers
  @param my_peer_ID My peer ID
  @param batch_size Batch size
  @param num_rounds Number of rounds per machine
  @param tf_model_objects Tensorflow model objects
  @return (Total number of messages sent, Total number of messages received from other peers)
  '''
  
  x, W, b, y, y_, train_step = tf_model_objects
  
  inc_msg_q = Queue.Queue()
  ret_val = Queue.Queue()
  msg_sent = 0
  sock_listen_thread = create_sock_listen_thread(sock, self_IP, inc_msg_q, num_peers, ret_val)
  
  for _ in range(num_rounds):    
    # Run one training step, training on only every <num_peers> batch
    W_old = sess.run(W)
    b_old = sess.run(b)
    for i in xrange(num_peers):
        if i == my_peer_ID:
            batch_xs, batch_ys = mnist.train.next_batch(batch_size)
        else: # skip this batch
            mnist.train.next_batch(batch_size)   
    sess.run(train_step, feed_dict={x: batch_xs, y_: batch_ys})
    
    # Find delta_W, delta_b
    W_new = sess.run(W)
    b_new = sess.run(b)
    delta_W = W_new - W_old
    delta_b = b_new - b_old
    
    # Send delta_W, delta_b to other peers
    deltas = delta_W, delta_b
    deltas_data = pickle.dumps(deltas, -1)
    msg_sent = socket_util.socket_send_data_chucks(sock, deltas_data, mcast_destination, msg_sent)
    
    # Handle each message in the socket queue
    while not inc_msg_q.empty():
        # Process received delta_W, delta_b from other peers
        other_deltas_data = inc_msg_q.get(False)
        other_deltas = pickle.loads(other_deltas_data)
        other_delta_W, other_delta_b = other_deltas
    
        # Update own model based on delta_W, delta_b from other peers
        W.assign(W + other_delta_W).eval()
        b.assign(b + other_delta_b).eval()
  
  sock_listen_thread.stop()
  rcv_msg_num = ret_val.get()
  # Handle last remaining message in the socket queue
  while not inc_msg_q.empty():
    # Process received delta_W, delta_b from other peers
    other_deltas_data = inc_msg_q.get(False)
    other_deltas = pickle.loads(other_deltas_data)
    other_delta_W, other_delta_b = other_deltas

    # Update own model based on delta_W, delta_b from other peers
    W.assign(W + other_delta_W).eval()
    b.assign(b + other_delta_b).eval()
    
  return (msg_sent, rcv_msg_num)

def create_sock_listen_thread(sock, self_IP, inc_msg_q, num_peers, ret_val):
  '''
  Create a SockListenThread and run it
  @params sock The socket to use
  @param self_IP The IP address of self
  @param inc_msg_q Incoming message queue storing messages from other peers
  @param num_peers Number of peers
  @param ret_val The queue to store the return value of rcv_msg_num
  @return The thread
  '''
  sock_listen_thread = SockListenThread(sock, self_IP, inc_msg_q, num_peers, ret_val)
  sock_listen_thread.start()
  return sock_listen_thread
    
def test_model(sess, mnist, tf_model_objects):
  '''
  Test trained model
  @param sess Tensorflow session
  @param mnist MNIST data
  @param tf_model_objects Tensorflow model objects
  @return Accuracy of the model
  '''
  
  x, y, y_ = tf_model_objects[0], tf_model_objects[3], tf_model_objects[4]
  
  correct_prediction = tf.equal(tf.argmax(y, 1), tf.argmax(y_, 1))
  accuracy_calc = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
  accuracy = sess.run(accuracy_calc, feed_dict={x: mnist.test.images,
                                      y_: mnist.test.labels})
  return accuracy                                      

def print_results(accuracy, train_starttime, test_starttime, test_endtime, num_peers, batch_size, num_rounds, msg_sent, rcv_msg_num):
  '''
  Print the results of the model training + testing
  @param accuracy Accuracy of the model
  @param train_starttime Start time of training
  @param test_starttime Start time of testing
  @param test_endtime End time of testing
  @param num_peers Number of peers
  @param batch_size Batch size
  @param num_rounds Number of rounds per machine
  @param msg_sent Total number of messages sent
  @param rcv_msg_num Total number of messages received from other peers
  '''
  
  print("Batch size: ", batch_size)
  print("Number of rounds per machine: ", num_rounds)
  print("Total number of rounds: ", num_rounds * num_peers)
  exp_msg_num = msg_sent * (num_peers - 1);
  print("CARE: Msg rcv/expected and loss rate are broken when multithreading!")
  print("Msg received = ", rcv_msg_num, "; Msg expected = ", exp_msg_num, "; lost rate = ", 1 - (rcv_msg_num * 1.0 / exp_msg_num) )
  print("Accuracy: ", accuracy)
  print("Train time: ", test_starttime - train_starttime, "; Test time: ", test_endtime - test_starttime)
  
if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--data_dir', type=str, default='./input_data', # /tmp/tensorflow/mnist/input_data
                      help='Directory for storing input data')
  FLAGS, unparsed = parser.parse_known_args()
  tf.app.run(main=main, argv=[sys.argv[0]] + unparsed)