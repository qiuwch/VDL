import tensorflow as tf

def inference_graph(images):
    with tf.name_scope('conv1') as sc:
        init_w = tf.truncated_normal([11, 11, 3, 64], dtype = tf.float32, stddev = 1e-1)
        k = tf.Variable(init_w, name = 'weights')
        conv = tf.nn.conv2d(images, k, [1, 4, 4, 1], padding='SAME')
        biases = tf.Variable(tf.constant(0.0, shape=[64], dtype=tf.float32),
            trainable = True, name = 'biases')
        with_bias = tf.nn.bias_add(conv, biases)
        conv1 = tf.nn.relu(with_bias, name=sc)

    pool1 = tf.nn.max_pool(conv1, ksize = [1,3,3,1], strides=[1,2,2,1],
        padding = 'VALID', name = 'pool1')

    with tf.name_scope('conv2') as sc:
        init_w = tf.truncated_normal([5, 5, 64, 192], dtype = tf.float32, stddev = 1e-1)
        k = tf.Variable(init_w, name = 'weights')
        conv = tf.nn.conv2d(pool1, k, [1, 1, 1, 1], padding='SAME')
        biases = tf.Variable(tf.constant(0.0, shape=[64], dtype=tf.float32),
            trainable = True, name = 'biases')
        with_bias = tf.nn.bias_add(conv, biases)
        conv2 = tf.nn.relu(with_bias, name=sc)

    pool2 = tf.nn.max_pool(conv2, ksize = [1,3,3,1], strides=[1,2,2,1],
        padding = 'VALID', name = 'pool2')

    with tf.name_scope('conv3') as sc:
        init_w = tf.truncated_normal([3, 3, 192, 384], dtype = tf.float32, stddev = 1e-1)
        k = tf.Variable(init_w, name = 'weights')
        conv = tf.nn.conv2d(pool2, k, [1, 1, 1, 1], padding='SAME')
        biases = tf.Variable(tf.constant(0.0, shape=[64], dtype=tf.float32),
            trainable = True, name = 'biases')
        with_bias = tf.nn.bias_add(conv, biases)
        conv3 = tf.nn.relu(with_bias, name=sc)

    with tf.name_scope('conv4') as sc:
        init_w = tf.truncated_normal([3, 3, 384, 256], dtype = tf.float32, stddev = 1e-1)
        k = tf.Variable(init_w, name = 'weights')
        conv = tf.nn.conv2d(conv3, k, [1, 1, 1, 1], padding='SAME')
        biases = tf.Variable(tf.constant(0.0, shape=[64], dtype=tf.float32),
            trainable = True, name = 'biases')
        with_bias = tf.nn.bias_add(conv, biases)
        conv4 = tf.nn.relu(with_bias, name=sc)

    with tf.name_scope('conv5') as sc:
        init_w = tf.truncated_normal([3, 3, 256, 256], dtype = tf.float32, stddev = 1e-1)
        k = tf.Variable(init_w, name = 'weights')
        conv = tf.nn.conv2d(conv3, k, [1, 1, 1, 1], padding='SAME')
        biases = tf.Variable(tf.constant(0.0, shape=[64], dtype=tf.float32),
            trainable = True, name = 'biases')
        with_bias = tf.nn.bias_add(conv, biases)
        conv5 = tf.nn.relu(with_bias, name=sc)

    pool5 = tf.nn.max_pool(conv5,
        ksize = [1, 3, 3, 1], strides = [1, 2, 2, 1],
        padding = 'VALID', name = 'pool5')

    # No fc layer is contained
    return pool5
