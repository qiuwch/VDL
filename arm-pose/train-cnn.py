# An CNN model with a L2 output layer to do regression on the arm parameters.
# This network is modified from https://github.com/tensorflow/models/blob/master/tutorials/image/cifar10/cifar10_train.py
import alexnet
import tensorflow as tf
import varm


def load_data():
    # Convert the rendered data
    return varm.load_data()

def inference_graph():
    return alexnet.inference_graph()

def loss_op(fc, labels):
    objective = tf.nn.l2_loss(fc)

    # Compute and apply gradient

def train():
    images, labels = load_data()
    # labels are 6 numbers, camera pos (3), arm configuration (3)
    # images are with random lighting and random texture color

    # Build the inference graph
    fc = inference_graph(images)

    # Build the training graph
    loss = loss_op(fc, labels)

    train_op = train_step(loss)

    with tf.train.MonitoredTrainingSession() as sess:
        sess.run(train_op)


def main():
    # Prepare dataset
    train()


if __name__ == '__main__':
    main()
