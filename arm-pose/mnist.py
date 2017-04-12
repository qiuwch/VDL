from base import Dataset, Net
import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data

class MNIST(Dataset):
    def __init__(self):
        self._data = input_data.read_data_sets('MNIST_data', one_hot = True)

    def next_train_batch(self, size=100):
        return self._data.train.next_batch(size)

    def test_set(self):
        test_set = self._data.test
        return test_set.images, test_set.labels

class MNIST_CNN(Net):
    def _weight_variable(self, shape):
        initial = tf.truncated_normal(shape, stddev = 0.1)
        return tf.Variable(initial)

    def _bias_variable(self, shape):
        initial = tf.constant(0.1, shape = shape)
        return tf.Variable(initial)

    def _conv2d(self, x, W):
        return tf.nn.conv2d(x, W, strides = [1,1,1,1], padding = 'SAME')

    def _max_pool_2x2(self, x):
        return tf.nn.max_pool(x, ksize = [1,2,2,1],
                strides = [1,2,2,1], padding = 'SAME')

    def input_graph(self):
        image = tf.placeholder(tf.float32, shape = [None, 784], name = 'image')
        label = tf.placeholder(tf.float32, shape = [None, 10], name = 'label')
        return image, label

    def inference_graph(self, img):
        img_reshape = tf.reshape(img, [-1, 28, 28, 1])

        W_conv1 = self._weight_variable([5, 5, 1, 32])
        b_conv1 = self._bias_variable([32])

        h_conv1 = tf.nn.relu(self._conv2d(img_reshape, W_conv1) + b_conv1)
        h_pool1 = self._max_pool_2x2(h_conv1)

        W_conv2 = self._weight_variable([5, 5, 32, 64])
        b_conv2 = self._bias_variable([64])

        h_conv2 = tf.nn.relu(self._conv2d(h_pool1, W_conv2) + b_conv2)
        h_pool2 = self._max_pool_2x2(h_conv2)

        W_fc1 = self._weight_variable([7 * 7 * 64, 1024])
        b_fc1 = self._bias_variable([1024])

        h_pool2_flat = tf.reshape(h_pool2, [-1, 7 * 7 * 64])
        h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1) + b_fc1)

        keep_prob = tf.placeholder(tf.float32, name = 'keep_prob')
        h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)

        W_fc2 = self._weight_variable([1024, 10])
        b_fc2 = self._bias_variable([10])

        y_conv = tf.matmul(h_fc1_drop, W_fc2) + b_fc2
        return [y_conv, keep_prob]

    def _l2_loss(self, prediction, label):
        print('Use L2 loss')
        diff = tf.subtract(prediction, label)
        objective = tf.nn.l2_loss(diff)
        return objective

    def _cross_entropy(self, prediction, label):
        print('Use cross entropy')
        cross_entropy = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels = label, logits = prediction))
        return cross_entropy

    def loss_graph(self, prediction, label):
        return self._cross_entropy(prediction, label)

    def accuracy_graph(self, prediction, label):
        correct_prediction = tf.equal(tf.argmax(prediction, 1), tf.argmax(label, 1))
        return tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

    def train_step(self, loss):
        return tf.train.AdamOptimizer(1e-4).minimize(loss)

class MNIST_Linear(Net):
    def input_graph(self):
        image = tf.placeholder(tf.float32, shape = [None, 784])
        label = tf.placeholder(tf.float32, shape = [None, 10])
        return image, label

    def inference_graph(self, image):
        W = tf.Variable(tf.zeros([784, 10]))
        b = tf.Variable(tf.zeros([10]))

        prediction = tf.matmul(image, W) + b
        return prediction

    def loss_graph(self, prediction, label):
        cross_entropy = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels = label, logits = prediction))
        return cross_entropy

    def train_step(self, loss):
        return tf.train.GradientDescentOptimizer(0.5).minimize(loss)

    def accuracy_graph(self, prediction, label):
        correct_prediction = tf.equal(tf.argmax(prediction, 1), tf.argmax(label, 1))
        return tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

def test_mnist():
    data = MNIST()
    net = MNIST_CNN()

def train_mnist():
    # net = MNIST_Linear()
    net = MNIST_CNN()
    data = MNIST()

    # Use place holder for data
    [image_batch, label_batch] = net.input_graph()
    # Build the inference graph
    [prediction, keep_prob] = net.inference_graph(image_batch)
    loss = net.loss_graph(prediction, label_batch)
    train_op = net.train_step(loss)
    accuracy = net.accuracy_graph(prediction, label_batch)

    [test_image, test_label] = data.test_set()
    grad_step = tf.train.AdamOptimizer(learning_rate = 1e-4).compute_gradients(loss)

    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        for i in range(10000):
            batch = data.next_train_batch(100)
            # train_op.run(feed_dict={image_batch: batch[0], label_batch: batch[1], keep_prob: 0.5})
            train_op.run(feed_dict={image_batch: batch[0], label_batch: batch[1], keep_prob: 1})
            if i % 100 == 0:
                tf.Print(loss, [loss], 'Iter %d, Loss=' % i).eval(feed_dict = {image_batch: batch[0], label_batch: batch[1], keep_prob: 0.5})
                print accuracy.eval(feed_dict = {image_batch: test_image, label_batch: test_label, keep_prob: 1})

            # grad_vals = sess.run([tf.reduce_sum(grad) for grad, _ in grad_step], feed_dict={image_batch: batch[0], label_batch: batch[1], keep_prob: 1})
            #
            # var_to_grad = {}
            # for grad_val, (_, var) in zip(grad_vals, grad_step):
            #     var_to_grad[var.name] = grad_val
            #     # print var.name
            #     print var.name, grad_val



if __name__ == '__main__':
    train_mnist()
