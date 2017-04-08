# An CNN model with a L2 output layer to do regression on the arm parameters.
# This network is modified from https://github.com/tensorflow/models/blob/master/tutorials/image/cifar10/cifar10_train.py
import alexnet # Load alexnet network structure
import tensorflow as tf
import varm # Load synthetic training images
import argparse
import numpy as np

FLAGS = tf.app.flags.FLAGS  # Define global variables
tf.app.flags.DEFINE_string('checkpoint_dir', 'tmp', 'Checkpoint directory')
# tf.app.flags.DEFINE_integer('batch_size', 30, 'Batch size')

def training_batch():
    # return varm.random_training_batch()
    return varm.lsp_training_batch()


def test(image, gt = None): # Apply the model to predict on an image
    with tf.Session() as sess:
        ckpt = tf.train.get_checkpoint_state(FLAGS.checkpoint_dir)
        if ckpt and ckpt.model_checkpoint_path:
            saver.restore(sess, ckpt.model_checkpoint_path)
        else:
            print('No checkpoint file found')

        # Run the testing on an image and output the estimation for this image
        # Should be used for debug, demo

        # Output the arm pose
        inference_op = inference_graph()
        # prediction = run(inference_op, image)
        prediction = sess.run([inference_op])

        # Apply inference op to the input image
        if gt:
            # Compare the prediction with gt
            print compare(prediction, gt)

def eval():
    # Evaluation on testing data
    # Create an evaluation op and use session to run this op
    pass

def train():
    # labels are 6 numbers, camera pos (3), arm configuration (3)
    # images are with random lighting and random texture color
    net = alexnet.AlexNet()
    data = varm.RandomDataset()

    [image_batch, label_batch] = net.input_graph()
    fc = net.inference_graph(image_batch) # Use a fc layer to do regression
    loss = net.loss_graph(fc, label_batch)
    train_op = net.train_step(loss)

    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        for i in range(2000):
            batch = data.next_train_batch(100)
            train_op.run(feed_dict = {image_batch: batch[0], label_batch: batch[1]})
            tf.Print(loss, [loss], 'Iter %d, Loss=' % i).eval(feed_dict = {image_batch: batch[0], label_batch: batch[1]})

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--train', action='store_true', default=True, help='Do training')
    parser.add_argument('--test', action='store_true', help='Do testing')

    args = parser.parse_args()

    if args.test:
        test()

    if args.train:
        # Prepare dataset
        train()


if __name__ == '__main__':
    main()
