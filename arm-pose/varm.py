# Provides the split of training and validation data
import json, glob # The label is stored as a json file
import tensorflow as tf
from base import Dataset
import numpy as np
import skimage.io, skimage.transform

FLAGS = tf.app.flags.FLAGS  # Define global variables
tf.app.flags.DEFINE_integer('batch_size', 30, 'Batch size')
# What if I have a duplicate definition for FLAGS?


class VarmDataset(Dataset):
    def __init__(self):
        self.cursor = 0
        self.images = glob.glob('data/img/*.png')
        self.labels = glob.glob('data/label/*.json')
        self.num_image = len(self.images)
        self.w = 256
        self.h = 256

    def _read_image(self, id):
        id = id % self.num_image
        im  = skimage.io.imread(self.images[id])
        resize_im = skimage.transform.resize(im, [self.h, self.w, 3]) / 256.0
        return resize_im


    def _read_label(self, id):
        id = id % self.num_image
        with open(self.labels[id]) as f:
            d = json.load(f)
            label = np.array([d['base'], d['upper'], d['lower'], d['dist'], d['elevation'], d['azimuth']])
        return label

    def next_train_batch(self, size):
        image_batch = np.zeros((size, self.w, self.h, 3))
        label_batch = np.zeros((size, 6))
        for i in range(size):
            image = self._read_image(self.cursor + i)
            label = self._read_label(self.cursor + i)

            image_batch[i,:,:,:] = image
            label_batch[i,:] = label

        self.cursor += size
        return image_batch, label_batch

    def test_set(self):
        pass


class RandomDataset(Dataset):
    def next_train_batch(self, size):
        image = np.random.normal(size=[size,256,256,3])
        label = np.random.normal(size=[size,6])
        return [image, label]

    def test_set(self):
        pass


class LSPDataset(Dataset):
    def next_train_batch(self, size):
        # Read image from hard disk and shuffle them

        img_filename_queue = tf.train.string_input_producer(
            tf.train.match_filenames_once("lsp_dataset/images/*.jpg"), name="filename_queue")

        image_reader = tf.WholeFileReader(name="image_reader")
        image_name, image_file = image_reader.read(img_filename_queue)
        image = tf.image.decode_jpeg(image_file, channels=3)

        #resize the image
        image = tf.image.resize_image_with_crop_or_pad(image, 128, 128)
        image = tf.cast(image, tf.float32)

        # image.set_shape((128, 128, 3))

        # label = tf.FIFOQueue(99, [tf.float32, tf.float32, tf.float32, tf.float32, tf.float32, tf.float32], shapes=None)
        # q.enqueue([0, 0, 0, 0, 0, 0]).run()
        # label.close()

        label_filename_queue = tf.train.string_input_producer(["lsp_dataset/testpos.csv"])
        reader = tf.TextLineReader()
        key, value = reader.read(label_filename_queue)
        record_defaults = [[0.0], [0.0], [0.0], [0.0], [0.0], [0.0]]
        c1, c2, c3, c4, c5, c6 = tf.decode_csv(value, record_defaults=record_defaults)
        label = tf.stack([c1, c2, c3, c4, c5, c6])

        # Generate batch
        num_preprocess_threads = 1
        min_queue_examples = 10
        image_batch, label_batch = tf.train.shuffle_batch(
            [image, label],
            batch_size = FLAGS.batch_size,
            num_threads=num_preprocess_threads,
            capacity=min_queue_examples + 3 * FLAGS.batch_size,
            min_after_dequeue=min_queue_examples,
            name="images")

        return image_batch, label_batch

def random_training_batch():
    # Convert the rendered data
    # return varm.load_data()

    # image, label are before batch
    image = tf.truncated_normal([480, 480, 3], dtype = tf.float32)# Generate a random image
    # [height, width, depth], see cifar10_input.py
    label = tf.truncated_normal([6], dtype = tf.float32) # Generate a random 6 number vector

    # Train batch is a tf op
    image_batch, label_batch = tf.train.shuffle_batch([image, label],
        batch_size = FLAGS.batch_size,
        capacity = 10000,
        min_after_dequeue = 500,
        num_threads = 8,
    )
    return image_batch, label_batch

def test_training_batch():
    # [image_batch, label_batch] = random_training_batch()
    with tf.Session() as sess:
        [image_batch, label_batch] = lsp_training_batch()
