# Provides the split of training and validation data


def test_data():
    pass


def train_data():
    [image_batch, label_batch] = tf.train.batch(
        [image, label],
        batch_size = batch_size,
        num_threads = num_preprocess_threads,
        )
