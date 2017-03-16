import os
import tensorflow as tf

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' # Disable Tensorflow debugging logs
x = tf.Variable([1.0, 2.0])

init = tf.global_variables_initializer()

sess = tf.InteractiveSession()
sess.run(init)

print(sess.run(x))
x = x + 1
print(sess.run(x))  
