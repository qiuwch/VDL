# An CNN model with a L2 output layer to do regression on the arm parameters.
# This network is modified from https://github.com/tensorflow/models/blob/master/tutorials/image/cifar10/cifar10_train.py
import alexnet # Load alexnet network structure
import tensorflow as tf
import varm # Load synthetic training images
import argparse, random
import numpy as np
import ipdb
try:
    import matplotlib.pyplot as plt
except:
    pass

FLAGS = tf.app.flags.FLAGS  # Define global variables
tf.app.flags.DEFINE_string('checkpoint_dir', 'tmp', 'Checkpoint directory')
# tf.app.flags.DEFINE_integer('batch_size', 30, 'Batch size')

def training_batch():
    # return varm.random_training_batch()
    return varm.lsp_training_batch()

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

def eval():
    # Evaluation on testing data
    # Create an evaluation op and use session to run this op
    pass

def train():
    # labels are 6 numbers, camera pos (3), arm configuration (3)
    # images are with random lighting and random texture color
    net = alexnet.AlexNet()
    # net = alexnet.LinearToy()
    # data = varm.RandomDataset()
    data = varm.VarmDataset()

    [image_batch, label_batch] = net.input_graph()
    prediction = net.inference_graph(image_batch) # Use a fc layer to do regression
    loss = net.loss_graph(prediction, label_batch)
    [train_op, grad_step] = net.train_step(loss)

    # grad_step = tf.train.AdamOptimizer(learning_rate = 1e-4).compute_gradients(loss)

    def format_array(arr):
        return ', '.join(['%7.3f' % v for v in arr])

    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        for i in range(2000):
            # pdb.set_trace()
            batch = data.next_train_batch(10)
            sess.run(train_op, feed_dict = {image_batch: batch[0], label_batch: batch[1]})
            # if i % 100 == 0:
            tf.Print(loss, [loss], 'Iter %d, Loss=' % i).eval(feed_dict = {image_batch: batch[0], label_batch: batch[1]})

            if True:
                test_id = random.randrange(1000)
                test_img = np.zeros((1, 256, 256, 3))
                raw_im = data._read_image(test_id)
                # plt.imshow(raw_im)
                # plt.show()

                test_img[0,:,:,:] = raw_im
                test_label = data._read_label(test_id)
                predicted = prediction.eval(feed_dict = {image_batch: test_img})
                print 'Iter: %d' % i
                print 'Prediction: ', format_array(predicted[0])
                # ipdb.set_trace()
                print 'GT:         ', format_array(test_label)


            if True:
                grad_vals = sess.run([tf.reduce_sum(tf.abs(grad)) for grad, _ in grad_step], feed_dict={image_batch: batch[0], label_batch: batch[1]})

                var_to_grad = {}
                for grad_val, (_, var) in zip(grad_vals, grad_step):
                    var_to_grad[var.name] = grad_val
                    # print var.name
                    print var.name, grad_val


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--train', action='store_true', default=True, help='Do training')
    parser.add_argument('--test', action='store_true', help='Do testing')

    args = parser.parse_args()

    if args.test:
        test()

    if args.train:
        train()

if __name__ == '__main__':
    main()
