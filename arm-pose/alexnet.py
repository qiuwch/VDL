import tensorflow as tf
import numpy as np
from base import Net

w = 256
h = 256


class LinearToy(Net):
    def input_graph(self):
        image_batch = tf.placeholder(tf.float32, shape=[None, w, h, 3])
        label_batch = tf.placeholder(tf.float32, shape=[None, 6])
        return [image_batch, label_batch]

    def inference_graph(self, image):
        flat_image = tf.reshape(image, [-1, w * h * 3])
        W = tf.Variable(tf.zeros([w * h * 3, 6]), name = 'weights')
        b = tf.Variable(tf.zeros([6]), name = 'biases')

        prediction = tf.matmul(flat_image, W) + b
        return prediction

    def loss_graph(self, prediction, label):
        # cross_entropy = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels = label, logits = prediction))
        diff = tf.subtract(prediction, label)
        objective = tf.nn.l2_loss(diff)
        return objective

    def train_step(self, loss):
        learning_rate = 1e-4
        # learning_rate = 0.1
        optimizer = tf.train.AdamOptimizer(learning_rate = learning_rate)
        step_op = optimizer.minimize(loss)
        grad_step = optimizer.compute_gradients(loss)
        return [step_op, grad_step]
        # return [tf.train.GradientDescentOptimizer(0.5).minimize(loss), None]
        # GradientDescent will overshoot

    def accuracy_graph(self, prediction, label):
        correct_prediction = tf.equal(tf.argmax(prediction, 1), tf.argmax(label, 1))
        return tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

class AlexNet(Net):
    def input_graph(self):
        image_batch = tf.placeholder(tf.float32, shape=[None, w, h, 3])
        label_batch = tf.placeholder(tf.float32, shape=[None, 6])
        return [image_batch, label_batch]

    def loss_graph(self, fc, labels):
        # diff = tf.subtract(fc, labels)
        # objective = tf.nn.l2_loss(fc - labels)
        objective = tf.reduce_sum(tf.pow(fc - labels, 2))
        return objective

    def train_step(self, loss):
        # Compute and apply gradient
        learning_rate = 1e-4
        # learning_rate = 0.1
        optimizer = tf.train.AdamOptimizer(learning_rate = learning_rate)
        step_op = optimizer.minimize(loss)
        grad_step = optimizer.compute_gradients(loss)
        # step_op = tf.train.GradientDescentOptimizer(0.5).minimize(loss)
        return [step_op, grad_step]

    # This alexnet structure is defined in
    def inference_graph(self, images):
        with tf.name_scope('conv1') as sc:
            init_w = tf.truncated_normal([11, 11, 3, 64], dtype = tf.float32, stddev = 1e-1)
            k = tf.Variable(init_w, name = 'weights')
            conv = tf.nn.conv2d(images, k, [1, 4, 4, 1], padding='SAME')
            biases = tf.Variable(tf.constant(0.0, shape=[64], dtype=tf.float32),
                 name = 'biases') # trainable by default
            with_bias = tf.nn.bias_add(conv, biases)
            conv1 = tf.nn.relu(with_bias, name=sc)

        pool1 = tf.nn.max_pool(conv1, ksize = [1,3,3,1], strides=[1,2,2,1],
            padding = 'VALID', name = 'pool1')

        with tf.name_scope('conv2') as sc:
            init_w = tf.truncated_normal([5, 5, 64, 192], dtype = tf.float32, stddev = 1e-1)
            k = tf.Variable(init_w, name = 'weights')
            conv = tf.nn.conv2d(pool1, k, [1, 1, 1, 1], padding='SAME')
            biases = tf.Variable(tf.constant(0.0, shape=[192],          dtype=tf.float32), name = 'biases')
            with_bias = tf.nn.bias_add(conv, biases)
            conv2 = tf.nn.relu(with_bias, name=sc)

        pool2 = tf.nn.max_pool(conv2, ksize = [1,3,3,1], strides=[1,2,2,1],
            padding = 'VALID', name = 'pool2')

        with tf.name_scope('conv3') as sc:
            init_w = tf.truncated_normal([3, 3, 192, 384], dtype = tf.float32, stddev = 1e-1)
            k = tf.Variable(init_w, name = 'weights')
            conv = tf.nn.conv2d(pool2, k, [1, 1, 1, 1], padding='SAME')
            biases = tf.Variable(tf.constant(0.0, shape=[384], dtype=tf.float32), name = 'biases')
            with_bias = tf.nn.bias_add(conv, biases)
            conv3 = tf.nn.relu(with_bias, name=sc)

        with tf.name_scope('conv4') as sc:
            init_w = tf.truncated_normal([3, 3, 384, 256], dtype = tf.float32, stddev = 1e-1)
            k = tf.Variable(init_w, name = 'weights')
            conv = tf.nn.conv2d(conv3, k, [1, 1, 1, 1], padding='SAME')
            biases = tf.Variable(tf.constant(0.0, shape=[256], dtype=tf.float32), name = 'biases')
            with_bias = tf.nn.bias_add(conv, biases)
            conv4 = tf.nn.relu(with_bias, name=sc)

        with tf.name_scope('conv5') as sc:
            init_w = tf.truncated_normal([3, 3, 256, 256], dtype = tf.float32, stddev = 1e-1)
            k = tf.Variable(init_w, name = 'weights')
            conv = tf.nn.conv2d(conv4, k, [1, 1, 1, 1], padding='SAME')
            biases = tf.Variable(tf.constant(0.0, shape=[256], dtype=tf.float32), name = 'biases')
            with_bias = tf.nn.bias_add(conv, biases)
            conv5 = tf.nn.relu(with_bias, name=sc)

        pool5 = tf.nn.max_pool(conv5,
            ksize = [1, 3, 3, 1], strides = [1, 2, 2, 1],
            padding = 'VALID', name = 'pool5')

        pool5_reshape = tf.reshape(pool5, [-1, int(np.prod(pool5.get_shape()[1:]))])
        # reshape = tf.reshape(pool5, [FLAGS.batch_size, -1])
        dim = pool5_reshape.get_shape()[1].value

        with tf.name_scope('fc6'):
            init_w = tf.truncated_normal([dim, 4096], dtype = tf.float32, stddev = 1e-1)
            init_b = tf.constant(0.0, shape=[4096], dtype=tf.float32)
            fc6w = tf.Variable(init_w, name = 'weights')
            fc6b = tf.Variable(init_b, name = 'biases')
            # fc6 = tf.nn.relu_layer(tf.reshape(pool5, [-1, int(np.prod(pool5.get_shape()[1:]))]), fc6w, fc6b)
            fc6 = tf.nn.relu_layer(pool5_reshape, fc6w, fc6b)

        with tf.name_scope('fc7'):
            init_w = tf.truncated_normal([4096, 4096], dtype = tf.float32, stddev = 1e-1)
            init_b = tf.constant(0.0, shape=[4096], dtype=tf.float32)
            fc7w = tf.Variable(init_w, name = 'weights')
            fc7b = tf.Variable(init_b, name = 'biases')
            fc7 = tf.nn.relu_layer(fc6, fc7w, fc7b)

        with tf.name_scope('fc8'):
            init_w = tf.truncated_normal([4096, 6], dtype = tf.float32, stddev = 1e-1)
            init_b = tf.constant(0.0, shape=[6], dtype=tf.float32)
            fc8w = tf.Variable(init_w, name = 'weights')
            fc8b = tf.Variable(init_b, name = 'biases')
            fc8 = tf.nn.relu_layer(fc7, fc8w, fc8b)

        # No fc layer is contained
        return fc8
        # return pool5

def test_alexnet():
    # FLAGS = tf.app.flags.FLAGS  # Define global variables
    # tf.app.flags.DEFINE_integer('batch_size', 30, 'Batch size')
    import varm
    image_batch, label_batch = varm.random_training_batch()
    net = AlexNet()
    fc = net.inference_graph(image_batch) # Use a fc layer to do regression
    loss = net.loss_graph(fc, label_batch)
