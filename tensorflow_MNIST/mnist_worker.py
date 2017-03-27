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


os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' # Disable Tensorflow debugging logs
np.set_printoptions(threshold=np.nan)
FLAGS = None


def main(_):
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

  # Set up TCP server side
  serverPort = 12000
  serverSocket = socket(AF_INET,SOCK_STREAM)
  serverSocket.bind(('',serverPort))
  serverSocket.listen(1)
  connectionSocket, addr = serverSocket.accept()
  
  # Train
  for _ in range(6):
    print('Round', _)
    
    # Receive the delta_W from the other side, and update own model
    #other_delta_W_data = connectionSocket.recv(32000)
    f = connectionSocket.makefile("r")
    #other_delta_W = pickle.loads(other_delta_W_data)
    other_delta_W = pickle.load(f)
    #W = W + other_delta_W
    mnist.train.next_batch(100) # skip this batch
    
    # Run one training step
    W_old = sess.run(W)
    batch_xs, batch_ys = mnist.train.next_batch(100)
    sess.run(train_step, feed_dict={x: batch_xs, y_: batch_ys})
    
    # Find delta_W
    W_new = sess.run(W)
    delta_W = W_new - W_old
    
    # Send the delta_W to the other side
    delta_W_data = pickle.dumps(delta_W, -1)
    print(len(delta_W_data))
    connectionSocket.sendall(delta_W_data)
  
  connectionSocket.close()
  # Test trained model
  correct_prediction = tf.equal(tf.argmax(y, 1), tf.argmax(y_, 1))
  accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
  print(sess.run(accuracy, feed_dict={x: mnist.test.images,
                                      y_: mnist.test.labels}))
  
if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--data_dir', type=str, default='./input_data', # /tmp/tensorflow/mnist/input_data
                      help='Directory for storing input data')
  FLAGS, unparsed = parser.parse_known_args()
  tf.app.run(main=main, argv=[sys.argv[0]] + unparsed)