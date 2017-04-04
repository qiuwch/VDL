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

import params
import socket_util


os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' # Disable Tensorflow debugging logs
np.set_printoptions(threshold=np.nan)
FLAGS = None


def main(_):
  global mnist, sess
  global sock, self_IP, mcast_destination
  global t0, t1, t2, t3

  t0 = time.time()
  parse_cmd_args()
  # Import data
  mnist = input_data.read_data_sets(FLAGS.data_dir, one_hot=True)
  
  create_model()
  sess = tf.InteractiveSession()
  tf.global_variables_initializer().run()

  t1 = time.time()
  sock, self_IP, mcast_destination = socket_util.set_up_UDP_mcast_peer()
  
  t2 = time.time()
  train()
  
  socket_util.close_UDP_mcast_peer(sock)
  test_model()
  
  t3 = time.time()
  print_results()
                                  

def parse_cmd_args():
  "Parse command line arguments"
  global batch_size, num_rounds
  
  batch_size = int(sys.argv[1]);
  num_rounds = int(sys.argv[2]);

def create_model():
  "Create the Tensorflow model for MNIST task"
  global x, W, b, y, y_, train_step
  
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
  
def train():
  "Train the Tensorflow MNIST model"
  
  for _ in range(num_rounds):
    #print('Round', _)
    
    # Skip one batch
    mnist.train.next_batch(batch_size)
    
    # Run one training step
    W_old = sess.run(W)
    b_old = sess.run(b)
    batch_xs, batch_ys = mnist.train.next_batch(batch_size)
    sess.run(train_step, feed_dict={x: batch_xs, y_: batch_ys})
    
    # Find delta_W, delta_b
    W_new = sess.run(W)
    b_new = sess.run(b)
    delta_W = W_new - W_old
    delta_b = b_new - b_old
    
    # Receive delta_W, delta_b from the other side
    #print ('Receiving data...')
    other_deltas_data_len_pkt, addr = sock.recvfrom(params.MAX_PACKET_SIZE)
    #print ('H1', other_deltas_data_len_pkt[0:3], addr)
    while other_deltas_data_len_pkt[0 : params.LEN_IMAGE_SIZE_PACKET_TAG] != params.IMAGE_SIZE_PACKET_TAG \
        or addr[0] == self_IP:
        other_deltas_data_len_pkt, addr = sock.recvfrom(params.MAX_PACKET_SIZE)
        #print ('H2', other_deltas_data_len_pkt[0:3], addr)
    other_deltas_data_len = int(other_deltas_data_len_pkt[params.LEN_IMAGE_SIZE_PACKET_TAG :])
    other_deltas_data = socket_util.socket_recv_chucked_data(sock, other_deltas_data_len, self_IP)
    if other_deltas_data == None:
        other_deltas = (tf.zeros([784, 10]), tf.zeros([10]))
    else:
        other_deltas = pickle.loads(other_deltas_data)
    other_delta_W, other_delta_b = other_deltas
    #print ('Receiving done.')
    
    # Send delta_W, delta_b to the other side
    #print ('Sending data...')
    deltas = delta_W, delta_b
    deltas_data = pickle.dumps(deltas, -1)
    socket_util.socket_send_data_chucks(sock, deltas_data, mcast_destination)
    #print ('Sending done.')
  
    # Update own model based on delta_W, delta_b from the other side
    W.assign(W + other_delta_W).eval()
    b.assign(b + other_delta_b).eval()
  
def test_model():
  "Test trained model"
  global accuracy
  
  correct_prediction = tf.equal(tf.argmax(y, 1), tf.argmax(y_, 1))
  accuracy_calc = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
  accuracy = sess.run(accuracy_calc, feed_dict={x: mnist.test.images,
                                      y_: mnist.test.labels})

def print_results():
  "Print the results of the model training + testing"
  
  print("Batch size: ", batch_size)
  print("Number of rounds per machine: ", num_rounds)
  print("Msg received = ", "; lost rate = ")
  num_machines = 2 # TODO variable
  print("Total number of rounds: ", num_rounds * num_machines)
  print("Accuracy: ", accuracy)
  print("Timestamps: ", t1-t0, t2-t1, t3-t2, t3-t0)
  
if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--data_dir', type=str, default='./input_data', # /tmp/tensorflow/mnist/input_data
                      help='Directory for storing input data')
  FLAGS, unparsed = parser.parse_known_args()
  tf.app.run(main=main, argv=[sys.argv[0]] + unparsed)