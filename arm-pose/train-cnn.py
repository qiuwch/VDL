# An CNN model with a L2 output layer to do regression on the arm parameters.
# This network is modified from https://github.com/tensorflow/models/blob/master/tutorials/image/cifar10/cifar10_train.py
import alexnet # Load alexnet network structure
import tensorflow as tf
import varm # Load synthetic training images
import argparse

def load_data():
    # Convert the rendered data
    return varm.load_data()

def load_batch(batch_size = 50):
    # return a batch  for training from the synthetic images
    pass

def inference_graph():
    return alexnet.inference_graph()

def loss_op(fc, labels):
    objective = tf.nn.l2_loss(fc)

    # Compute and apply gradient

def compare(prediction, gt):
    pass

G.checkpoint_dir = 'tmp'

def test(image, gt = None): # Apply the model to predict on an image
    with tf.Session() as sess:
        ckpt = tf.train.get_checkpoint_state(G.checkpoint_dir)
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

        pass

def eval():
    # Evaluation on testing data
    # Create an evaluation op and use session to run this op
    pass

def train_step(loss):
    train_op = tf.train.AdamOptimizer(1e-4).minimize(loss)
    return train_op

def train():
    images, labels = load_data()
    # labels are 6 numbers, camera pos (3), arm configuration (3)
    # images are with random lighting and random texture color

    # Build the inference graph
    fc = inference_graph(images)

    # Build the training graph
    loss = loss_op(fc, labels)

    train_op = train_step(loss)

    # with tf.train.MonitoredTrainingSession() as sess:
    #     sess.run(train_op)

    # Run this within a session
    for i in range(20000):
        batch_data = load_batch(50)
        train_op.run(feed_dict = {image: batch_data[0], label: batch_data[1]})

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--train', type=bool, help='Do training')
    parser.add_argument('--test', type=bool, help='Do testing')

    args = parser.parse_args()

    if args.train():
        # Prepare dataset
        train()

    if args.test():
        test()

def test_load_batch():
    pass


if __name__ == '__main__':
    main()
