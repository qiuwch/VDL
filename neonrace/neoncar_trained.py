import gym
import universe  # register the universe environments
from model import LSTMPolicy
import envs
import tensorflow as tf

def init(env):
    policy = LSTMPolicy(env.observation_space.shape, env.action_space.n)
    # Load this from training snapshot
    return policy

# default_action = [('KeyEvent', 'ArrowUp', True)]
# default_action = 0
default_action = 3
# keys = ['left', 'right', 'up', 'left up', 'right up', 'down', 'up x']

def run_env(env, policy):
    last_state = env.reset()
    # state = last_state
    last_features = policy.get_initial_features()
    length = 0
    rewards = 0
    saver = tf.train.Saver()
    with tf.Session() as sess:
        # Restore variables from disk.
        # saver.restore(sess, "train/model.ckpt-361814.data-00000-of-00001")
        # saver.restore(sess, "train/model.ckpt-361814")
        saver.restore(sess, "/tmp/neonrace/train/model.ckpt-361714")
        while True:
            terminal_end = False

            fetched = policy.act(last_state, *last_features)
            action, value_, features = fetched[0], fetched[1], fetched[2:]
            # state, reward, terminal, info = env.step(action.argmax())
            action_n = action.argmax()

            # state, reward, terminal, info = env.step(default_action)
            state, reward, terminal, info = env.step(action_n)
            env.render() # I need to visualize it during testing

            length += 1
            rewards += reward

            last_state = state
            last_features = features

            if terminal:
                terminal_end = True
                print("Episode finished. Sum of rewards: %d. Length: %d" % (rewards, length))
                length = 0
                rewards = 0
                break

def create_env():
    # env = gym.make('flashgames.DuskDrive-v0')
    # env = gym.make('flashgames.NeonRace-v0')
    # env.configure(remotes=1)  # automatically creates a local docker container
    env_id = 'flashgames.NeonRace-v0'
    env = envs.create_flash_env(env_id, 'worker', remotes=1)
    return env

# while True:
#   action_n = [[('KeyEvent', 'ArrowUp', True)] for ob in observation_n]  # your agent here
#   observation_n, reward_n, done_n, info = env.step(action_n)
#   env.render()

def main():
    env = create_env()
    policy = init(env)

    run_env(env, policy)

if __name__ == '__main__':
    main()
