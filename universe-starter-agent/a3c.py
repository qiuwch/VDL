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

class A3C(object):
    def __init__(self, env, task, visualise, num_workers):
        """
An implementation of the A3C algorithm that is reasonably well-tuned for the VNC environments.
Below, we will have a modest amount of complexity due to the way TensorFlow handles data parallelism.
But overall, we'll define the model, specify its inputs, and describe how the policy gradients step
should be computed.
"""

        self.env = env
        self.task = task

        with tf.variable_scope("local"):
            self.local_network = pi = LSTMPolicy(env.observation_space.shape, env.action_space.n)

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

        # each worker has a different set of adam optimizer parameters
        self.opt = tf.train.AdamOptimizer(1e-4)
        self.train_op = self.opt.apply_gradients(grads_and_vars)

        # Expose the gradients
        self.grads_and_vars = grads_and_vars
        self.summary_writer = None
        self.local_steps = 0
        
        # multicast setup
        self.inc_msg_q = Queue.Queue()
        self.ret_val = Queue.Queue()
        self.msg_sent = 0
        
        self.sock, self_IP, self.mcast_destination = socket_util.set_up_UDP_mcast_peer()
        self.sock_listen_thread = socket_util.SockListenThread(self.sock, self_IP, self.inc_msg_q, num_workers, self.ret_val)
        #TODO while waiting, other stuff are still happening
        socket_util.await_start_mcast(self.sock)

    def start(self, sess, summary_writer):
        self.runner.start_runner(sess, summary_writer)
        self.summary_writer = summary_writer
        self.sock_listen_thread.start()

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

        #sess.run(self.sync)  # copy weights from shared to local
        rollout = self.pull_batch_from_queue()
        batch = process_rollout(rollout, gamma=0.99, lambda_=1.0)

        should_compute_summary = self.task == 0 and self.local_steps % 11 == 0

        if should_compute_summary:
            # TODO: @Vincent Add gradient information into fetch list, so that we can get gradients from the computation.
            # See
            # `grads_and_vars = list(zip(grads, self.network.var_list))`
            # and
            # `self.train_op = tf.group(opt.apply_gradients(grads_and_vars), inc_step)``
            # Search this file to find these two lines.
            # I did not use line number because it might change
            # @Vincent, the loop is executed in worker.py:L81

            fetches = [self.summary_op, self.train_op, self.grads_and_vars]
        else:
            fetches = [self.train_op, self.grads_and_vars]

        feed_dict = {
            self.local_network.x: batch.si,
            self.ac: batch.a,
            self.adv: batch.adv,
            self.r: batch.r,
            self.local_network.state_in[0]: batch.features[0],
            self.local_network.state_in[1]: batch.features[1],
        }

        fetched = sess.run(fetches, feed_dict=feed_dict)

        grads_and_vars = fetched[-1] # This is the grads and vars
        grads_and_vars_data = pickle.dumps(grads_and_vars, -1)
        self.msg_sent = socket_util.socket_send_data_chucks(self.sock, grads_and_vars_data, self.mcast_destination, self.msg_sent)

        # remote_grads_and_vars = grads_and_vars # TODO: @qiuwch, need to fix this
        # self.opt.apply_gradients(remote_grads_and_vars)

        # Handle each message in the socket queue
        while not self.inc_msg_q.empty():
            # Process received grads_and_vars from other peers
            remote_grads_and_vars_data = inc_msg_q.get(False)
            remote_grads_and_vars = pickle.loads(remote_grads_and_vars_data)
            # self.opt.apply_gradients(remote_grads_and_vars) # TODO: @qiuwch, need to fix this
            print('Apply remote gradients')
            # apply_grad(grads) # Need to implement this @qiuwch

        if should_compute_summary:
            self.summary_writer.add_summary(tf.Summary.FromString(fetched[0]))
            self.summary_writer.flush()
        self.local_steps += 1
