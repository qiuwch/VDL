# Provides the split of training and validation data
import json # The label is stored as a json file
import cv2 # Read images


# Split data into training, val and test
def test_data():
    pass

def train_data():
    # Read image from hard disk and shuffle them

    [image_batch, label_batch] = tf.train.batch(
        [image, label],
        batch_size = batch_size,
        num_threads = num_preprocess_threads,
        )
