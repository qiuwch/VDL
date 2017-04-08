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
    net = MNIST_Linear()
    data = MNIST()

    # Use place holder for data
    [image_batch, label_batch] = net.input_graph()
    # Build the inference graph
    prediction = net.inference_graph(image_batch)
    loss = net.loss_graph(prediction, label_batch)
    train_op = net.train_step(loss)
    accuracy = net.accuracy_graph(prediction, label_batch)

    [test_image, test_label] = data.test_set()

    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        for i in range(1000):
            batch = data.next_train_batch(100)
            train_op.run(feed_dict={image_batch: batch[0], label_batch: batch[1]})
            if i % 100 == 0:
                tf.Print(loss, [loss], 'Iter %d, Loss=' % i).eval(feed_dict = {image_batch: batch[0], label_batch: batch[1]})
                print accuracy.eval(feed_dict = {image_batch: test_image, label_batch: test_label})



if __name__ == '__main__':
    train_mnist()
