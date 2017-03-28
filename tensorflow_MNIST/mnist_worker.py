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
from socket import *
import pickle
import time


os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' # Disable Tensorflow debugging logs
np.set_printoptions(threshold=np.nan)
FLAGS = None


def main(_):
  t0 = time.time()
  # Import data
  mnist = input_data.read_data_sets(FLAGS.data_dir, one_hot=True)

  # Create the model
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
  
  sess = tf.InteractiveSession()
  tf.global_variables_initializer().run()

  t1 = time.time()
  # Set up TCP server side
  serverPort = 12000
  serverSocket = socket(AF_INET,SOCK_STREAM)
  serverSocket.bind(('',serverPort))
  serverSocket.listen(1)
  connectionSocket, addr = serverSocket.accept()
  
  t2 = time.time()
  # Train
  batch_size = int(sys.argv[1]);
  num_rounds = int(sys.argv[2]);
  for _ in range(num_rounds):
    #print('Round', _)
    
    # Receive delta_W, delta_b from the other side, and update own model
    #TODO other_delta_W_data = connectionSocket.recv(32000)
    f = connectionSocket.makefile("r")
    #other_delta_W = pickle.loads(other_delta_W_data)
    other_delta_W = pickle.load(f)
    f = connectionSocket.makefile("r")
    other_delta_b = pickle.load(f)
    W.assign(W + other_delta_W).eval()
    b.assign(b + other_delta_b).eval()
    mnist.train.next_batch(batch_size) # skip this batch
    
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
    
    # Send delta_W, delta_b to the other side
    delta_W_data = pickle.dumps(delta_W, -1)
    delta_b_data = pickle.dumps(delta_b, -1)
    connectionSocket.sendall(delta_W_data)
    connectionSocket.sendall(delta_b_data)
    #print(len(delta_W_data), len(delta_b_data))
  
  f.close()
  connectionSocket.close()
  serverSocket.close() #TODO find better way
  #print(sess.run(W)) #TODODO rm
  # Test trained model
  correct_prediction = tf.equal(tf.argmax(y, 1), tf.argmax(y_, 1))
  accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
  t3 = time.time()
  
  print("Batch size: ", batch_size)
  print("Number of rounds per machine: ", num_rounds)
  num_machines = 2 # TODO variable
  print("Total number of rounds: ", num_rounds * num_machines)
  print("Accuracy: ", sess.run(accuracy, feed_dict={x: mnist.test.images,
                                      y_: mnist.test.labels}))
  print("Timestamps: ", t1-t0, t2-t1, t3-t2, t3-t0)                                     
  
if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--data_dir', type=str, default='./input_data', # /tmp/tensorflow/mnist/input_data
                      help='Directory for storing input data')
  FLAGS, unparsed = parser.parse_known_args()
  tf.app.run(main=main, argv=[sys.argv[0]] + unparsed)