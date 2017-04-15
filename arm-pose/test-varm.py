import alexnet
import varm

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
