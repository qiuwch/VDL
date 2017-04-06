# Provides the split of training and validation data
import json # The label is stored as a json file
import cv2 # Read images
import tensorflow as tf

FLAGS = tf.app.flags.FLAGS  # Define global variables
tf.app.flags.DEFINE_integer('batch_size', 30, 'Batch size')
# What if I have a duplicate definition for FLAGS?

# Split data into training, val and test
def test_data():
    pass

def synthetic_training_batch():
    # Read image from hard disk and shuffle them

    [image_batch, label_batch] = tf.train.batch(
        [image, label],
        batch_size = batch_size,
        num_threads = num_preprocess_threads,
        )

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
    [image_batch, label_batch] = random_training_batch()
