from __future__ import print_function
from collections import namedtuple
import numpy as np
import tensorflow as tf
from model import LSTMPolicy
import six.moves.queue as queue
import scipy.signal
import threading
import distutils.version

import socket_util
import Queue
import cPickle as pickle
use_tf12_api = distutils.version.LooseVersion(tf.VERSION) >= distutils.version.LooseVersion('0.12.0')
sock_listen_thread = None

import pdb, sys
import params
import time
from pprint import pprint


def discount(x, gamma):
    return scipy.signal.lfilter([1], [1, -gamma], x[::-1], axis=0)[::-1]

def process_rollout(rollout, gamma, lambda_=1.0):
    """
given a rollout, compute its returns and the advantage
"""
    batch_si = np.asarray(rollout.states)
    batch_a = np.asarray(rollout.actions)
    rewards = np.asarray(rollout.rewards)
    vpred_t = np.asarray(rollout.values + [rollout.r])

    rewards_plus_v = np.asarray(rollout.rewards + [rollout.r])
    batch_r = discount(rewards_plus_v, gamma)[:-1]
    delta_t = rewards + gamma * vpred_t[1:] - vpred_t[:-1]
    # this formula for the advantage comes "Generalized Advantage Estimation":
    # https://arxiv.org/abs/1506.02438
    batch_adv = discount(delta_t, gamma * lambda_)

    features = rollout.features[0]
    return Batch(batch_si, batch_a, batch_adv, batch_r, rollout.terminal, features)

Batch = namedtuple("Batch", ["si", "a", "adv", "r", "terminal", "features"])

class PartialRollout(object):
    """
a piece of a complete rollout.  We run our agent, and process its experience
once it has processed enough steps.
"""
    def __init__(self):
        self.states = []
        self.actions = []
        self.rewards = []
        self.values = []
        self.r = 0.0
        self.terminal = False
        self.features = []

    def add(self, state, action, reward, value, terminal, features):
        self.states += [state]
        self.actions += [action]
        self.rewards += [reward]
        self.values += [value]
        self.terminal = terminal
        self.features += [features]

    def extend(self, other):
        assert not self.terminal
        self.states.extend(other.states)
        self.actions.extend(other.actions)
        self.rewards.extend(other.rewards)
        self.values.extend(other.values)
        self.r = other.r
        self.terminal = other.terminal
        self.features.extend(other.features)

class RunnerThread(threading.Thread):
    """
One of the key distinctions between a normal environment and a universe environment
is that a universe environment is _real time_.  This means that there should be a thread
that would constantly interact with the environment and tell it what to do.  This thread is here.
"""
    def __init__(self, env, policy, num_local_steps, visualise):
        threading.Thread.__init__(self)
        self.queue = queue.Queue(5)
        self.num_local_steps = num_local_steps
        self.env = env
        self.last_features = None
        self.policy = policy
        self.daemon = True
        self.sess = None
        self.summary_writer = None
        self.visualise = visualise

    def start_runner(self, sess, summary_writer):
        self.sess = sess
        self.summary_writer = summary_writer
        self.start()

    def run(self):
        with self.sess.as_default():
            self._run()

    def _run(self):
        rollout_provider = env_runner(self.env, self.policy, self.num_local_steps, self.summary_writer, self.visualise)
        while True:
            # the timeout variable exists because apparently, if one worker dies, the other workers
            # won't die with it, unless the timeout is set to some large number.  This is an empirical
            # observation.

            self.queue.put(next(rollout_provider), timeout=600.0)

def env_runner(env, policy, num_local_steps, summary_writer, render):
    """
The logic of the thread runner.  In brief, it constantly keeps on running
the policy, and as long as the rollout exceeds a certain length, the thread
runner appends the policy to the queue.
"""
    last_state = env.reset()
    last_features = policy.get_initial_features()
    length = 0
    rewards = 0

    while True:
        terminal_end = False
        rollout = PartialRollout()

        for _ in range(num_local_steps):
            # TODO: @qiuwch, Replace policy.act to action from learner
            fetched = policy.act(last_state, *last_features)
            action, value_, features = fetched[0], fetched[1], fetched[2:]
            # argmax to convert from one-hot
            state, reward, terminal, info = env.step(action.argmax())
            if render:
                env.render()

            # collect the experience
            # TODO: @qiuwch, Replace rollout.add to a function sending message back to the learner
            rollout.add(last_state, action, reward, value_, terminal, last_features)
            length += 1
            rewards += reward

            last_state = state
            last_features = features

            if info:
                summary = tf.Summary()
                for k, v in info.items():
                    summary.value.add(tag=k, simple_value=float(v))
                summary_writer.add_summary(summary, policy.global_step.eval())
                summary_writer.flush()

            timestep_limit = env.spec.tags.get('wrapper_config.TimeLimit.max_episode_steps')
            if terminal or length >= timestep_limit:
                terminal_end = True
                if length >= timestep_limit or not env.metadata.get('semantics.autoreset'):
                    last_state = env.reset()
                last_features = policy.get_initial_features()
                print("Episode finished. Sum of rewards: %d. Length: %d" % (rewards, length))
                length = 0
                rewards = 0
                break

        if not terminal_end:
            rollout.r = policy.value(last_state, *last_features)

        # once we have enough experience, yield it, and have the ThreadRunner place it on a queue
        yield rollout

var0 = None  # TODO: Change these two to local variables
var1 = None
class A3C(object):
    def __init__(self, env, task, visualise, num_workers, worker_id):
        """
An implementation of the A3C algorithm that is reasonably well-tuned for the VNC environments.
Below, we will have a modest amount of complexity due to the way TensorFlow handles data parallelism.
But overall, we'll define the model, specify its inputs, and describe how the policy gradients step
should be computed.
"""
        global sock_listen_thread
        self.env = env
        self.task = task

        with tf.variable_scope("local"):
            self.local_network = pi = LSTMPolicy(env.observation_space.shape, env.action_space.n)
            self.local_network.global_step = tf.get_variable("global_step", [], tf.int32, initializer=tf.constant_initializer(0, dtype=tf.int32), trainable=False)

        self.ac = tf.placeholder(tf.float32, [None, env.action_space.n], name="ac")
        self.adv = tf.placeholder(tf.float32, [None], name="adv")
        self.r = tf.placeholder(tf.float32, [None], name="r")

        log_prob_tf = tf.nn.log_softmax(pi.logits)
        prob_tf = tf.nn.softmax(pi.logits)

        # the "policy gradients" loss:  its derivative is precisely the policy gradient
        # notice that self.ac is a placeholder that is provided externally.
        # adv will contain the advantages, as calculated in process_rollout
        pi_loss = - tf.reduce_sum(tf.reduce_sum(log_prob_tf * self.ac, [1]) * self.adv)

        # loss of value function
        vf_loss = 0.5 * tf.reduce_sum(tf.square(pi.vf - self.r))
        entropy = - tf.reduce_sum(prob_tf * log_prob_tf)

        bs = tf.to_float(tf.shape(pi.x)[0])
        self.loss = pi_loss + 0.5 * vf_loss - entropy * 0.01

        # 20 represents the number of "local steps":  the number of timesteps
        # we run the policy before we update the parameters.
        # The larger local steps is, the lower is the variance in our policy gradients estimate
        # on the one hand;  but on the other hand, we get less frequent parameter updates, which
        # slows down learning.  In this code, we found that making local steps be much
        # smaller than 20 makes the algorithm more difficult to tune and to get to work.
        self.runner = RunnerThread(env, pi, 20, visualise)


        grads = tf.gradients(self.loss, pi.var_list)

        if use_tf12_api:
            tf.summary.scalar("model/policy_loss", pi_loss / bs)
            tf.summary.scalar("model/value_loss", vf_loss / bs)
            tf.summary.scalar("model/entropy", entropy / bs)
            tf.summary.image("model/state", pi.x)
            tf.summary.scalar("model/grad_global_norm", tf.global_norm(grads))
            tf.summary.scalar("model/var_global_norm", tf.global_norm(pi.var_list))
            self.summary_op = tf.summary.merge_all()

        else:
            tf.scalar_summary("model/policy_loss", pi_loss / bs)
            tf.scalar_summary("model/value_loss", vf_loss / bs)
            tf.scalar_summary("model/entropy", entropy / bs)
            tf.image_summary("model/state", pi.x)
            tf.scalar_summary("model/grad_global_norm", tf.global_norm(grads))
            tf.scalar_summary("model/var_global_norm", tf.global_norm(pi.var_list))
            self.summary_op = tf.merge_all_summaries()

        grads, _ = tf.clip_by_global_norm(grads, 40.0)

        grads_and_vars = list(zip(grads, pi.var_list))
        inc_step = self.local_network.global_step.assign_add(tf.shape(pi.x)[0])

        # each worker has a different set of adam optimizer parameters
        self.opt = tf.train.AdamOptimizer(1e-4)
        self.train_op = tf.group(self.opt.apply_gradients(grads_and_vars), inc_step)

        # Expose the gradients
        self.grads_and_vars = grads_and_vars
        self.summary_writer = None
        self.local_steps = 0

        # multicast setup
        self.inc_msg_q = Queue.Queue()
        self.ret_val = Queue.Queue()
        self.msg_sent = 0
        self.num_workers = num_workers
        self.worker_id = worker_id

        if self.num_workers > 1: # Only wait when we are using mutilple workers
            self.sock, self_IP, self.mcast_destination = socket_util.set_up_UDP_mcast_peer()
            sock_listen_thread = socket_util.SockListenThread(self.sock, self_IP, self.inc_msg_q, num_workers, self.ret_val)
            #TODO while waiting, other stuff are still happening
            socket_util.await_start_mcast(self.sock)
            

    def start_listen_thread(self):
        if self.num_workers == 1:
            return
        if sock_listen_thread:
            sock_listen_thread.start()
                
    def sync_initial_weights(self, sess, var_list):
        if self.num_workers == 1:
            return
            
        if self.worker_id == 0:
            print('Initial values of weights')
            var_init = sess.run(var_list) # After training
            pprint(var_init) 
            var_init_data = pickle.dumps(var_init) 
            time.sleep(1)  # wait for other workers' listen thread to start up
            socket_util.socket_send_data_chucks(self.sock, params.INIT_WEIGHTS_TAG + var_init_data, self.mcast_destination, 0)
            # Discard your own initial weights message
            while self.inc_msg_q.empty():
                time.sleep(0.05)
            self.inc_msg_q.get(False)
        else:
            print('Wait initial weights')
            while self.inc_msg_q.empty():
                time.sleep(0.05)
            print('Got Initial value from worker 0')
            # Receive remote var data and use it as a start signal
            remote_var_data = self.inc_msg_q.get(False)
            if remote_var_data[:len(params.INIT_WEIGHTS_TAG)] != params.INIT_WEIGHTS_TAG:
                print('Error! Received data other than initial weights. Exiting...')
                sys.exit(-1)
            remote_var = pickle.loads(remote_var_data[len(params.INIT_WEIGHTS_TAG):])
            assign_op = [v.assign(data) for (v, data) in zip(var_list, remote_var)]
            sess.run(assign_op)
        print('Sync initial weights completed')
    
    def start(self, sess, summary_writer):
        self.runner.start_runner(sess, summary_writer)
        self.summary_writer = summary_writer

    def pull_batch_from_queue(self):
        """
self explanatory:  take a rollout from the queue of the thread runner.
"""
        rollout = self.runner.queue.get(timeout=600.0)
        while not rollout.terminal:
            try:
                rollout.extend(self.runner.queue.get_nowait())
            except queue.Empty:
                break
        return rollout

    def process(self, sess):
        """
process grabs a rollout that's been produced by the thread runner,
and updates the parameters.  The update is then sent to the parameter
server.
"""
        global send_counter
        
        #sess.run(self.sync)  # copy weights from shared to local
        rollout = self.pull_batch_from_queue()
        batch = process_rollout(rollout, gamma=0.99, lambda_=1.0)

        should_compute_summary = self.task == 0 and self.local_steps % 11 == 0

        if should_compute_summary:
            fetches = [self.summary_op, self.train_op]
        else:
            fetches = [self.train_op]


        feed_dict = {
            self.local_network.x: batch.si,
            self.ac: batch.a,
            self.adv: batch.adv,
            self.r: batch.r,
            self.local_network.state_in[0]: batch.features[0],
            self.local_network.state_in[1]: batch.features[1],
        }

        # Get current trainable variables
        # This is trainable variables
        fetched = sess.run(fetches, feed_dict=feed_dict)


        if self.num_workers > 1:
            sys.stdout.write('\r' + str(self.local_steps))
            if self.local_steps % 10 == 0:
                global var0
                global var1
                var1 = sess.run(self.local_network.var_list) # After training
                if var0 != None:
                    var_diff = [a - b for (a,b) in zip(var1, var0)]
                    var_diff_data = pickle.dumps(var_diff, -1)  # size is 2352348 bytes
                    print('Sync weights')
                    self.msg_sent = socket_util.socket_send_data_chucks(self.sock, var_diff_data, self.mcast_destination, self.msg_sent)
                var0 = sess.run(self.local_network.var_list) # A list of numpy array

            # Handle each message in the socket queue
            while not self.inc_msg_q.empty():
                print('Apply remote gradients')
                # Process received grads_and_vars from other peers
                remote_var_diff_data = self.inc_msg_q.get(False)
                remote_var_diff = pickle.loads(remote_var_diff_data)

                add_op = [a+b for (a,b) in zip(self.local_network.var_list, remote_var_diff)]
                sess.run(add_op)

        if should_compute_summary:
            self.summary_writer.add_summary(tf.Summary.FromString(fetched[0]))
            self.summary_writer.flush()
        self.local_steps += 1


def stop_sock_listen_thread():
    if sock_listen_thread:
        sock_listen_thread.stop()

import atexit
atexit.register(stop_sock_listen_thread)
