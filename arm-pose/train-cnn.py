# An CNN model with a L2 output layer to do regression on the arm parameters.
# This network is modified from https://github.com/tensorflow/models/blob/master/tutorials/image/cifar10/cifar10_train.py
import alexnet # Load alexnet network structure
import tensorflow as tf
import varm # Load synthetic training images
import argparse

FLAGS = tf.app.flags.FLAGS  # Define global variables
tf.app.flags.DEFINE_string('checkpoint_dir', 'tmp', 'Checkpoint directory')
# tf.app.flags.DEFINE_integer('batch_size', 30, 'Batch size')

def training_batch():
    # return varm.random_training_batch()
    return varm.lsp_training_batch()

def testing_batch():
    return varm.lsp_testing_batch()

def inference_graph(images):
    return alexnet.inference_graph(images)

def loss_graph(fc, labels):
    return alexnet.loss_graph(fc, labels)

def compare(prediction, gt):
    pass

def test(): # Apply the model to predict on an image
    print 'Start testing'
    with tf.Session() as sess:
        ckpt = tf.train.get_checkpoint_state(FLAGS.checkpoint_dir)
        if ckpt and ckpt.model_checkpoint_path:
            saver.restore(sess, ckpt.model_checkpoint_path)
        else:
            print('No checkpoint file found')

        # images and labels are tensorflow variables, not the actual value
        image_batch = testing_batch()
        # labels are 6 numbers, camera pos (3), arm configuration (3)
        # images are with random lighting and random texture color

        # Build the inference graph
        fc = inference_graph(image_batch) # Use a fc layer to do regression

        with tf.Session() as sess:
            sess.run(fc)

        # Run the testing on an image and output the estimation for this image
        # Should be used for debug, demo
        # prediction = run(inference_op, image)
        # prediction = sess.run([inference_op])

        # Apply inference op to the input image
        # if gt:
        #     # Compare the prediction with gt
        #     print compare(prediction, gt)

def demo():
    # Evaluation on testing data
    # Create an evaluation op and use session to run this op
    pass

def train_step(loss):
    # Compute and apply gradient
    step_op = tf.train.AdamOptimizer(1e-4).minimize(loss)
    return step_op

def train():
    # images and labels are tensorflow variables, not the actual value
    image_batch, label_batch = training_batch()
    # labels are 6 numbers, camera pos (3), arm configuration (3)
    # images are with random lighting and random texture color

    # Build the inference graph
    fc = inference_graph(image_batch) # Use a fc layer to do regression

    # Build the training graph
    loss = loss_graph(fc, label_batch)

    train_op = train_step(loss)
    print 'Start session'

    # with tf.train.MonitoredTrainingSession() as sess:
    #     sess.run(train_op)
    with tf.Session() as sess:
        train_op.run()

    # with tf.Session() as sess:
    #     # Run this within a session
    #     for i in range(20000):
    #         print i
    #         # batch_data = load_batch(50)
    #         # train_op.run(feed_dict = {image: batch_data[0], label: batch_data[1]})
    #         train_op.run()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--train', action='store_true', default=True, help='Do training')
    parser.add_argument('--test', action='store_true', help='Do testing')

    args = parser.parse_args()

    if args.test:
        test()
        return

    if args.train:
        train()


def test_load_batch():
    pass


if __name__ == '__main__':
    main()
