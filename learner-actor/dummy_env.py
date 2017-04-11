# This environment did nothing but trying to simulate problem of different sizes
import gym
import gym.spaces
import numpy as np
import time, re

def create(task_name):
    # The env name contains two parts
    # Observation size, measured by bytes
    # Frame rate, measured by frames per second
    regexp = re.compile('dummy/OBS(.*)-FPS(.*)-v0')
    match = regexp.match(task_name)
    obs_size = int(match.group(1))
    fps = int(match.group(2))

    gym.envs.registration.register(
        id='dummy/OBS%d-FPS%d-v0' % (obs_size, fps),
        entry_point='dummy_env:DummyEnv',
        kwargs=dict(
            fps = fps,
            obs_size = obs_size,
        )
        # max_episode_steps=10000, # No actual meaning
        # reward_threshold=10.0, # No actual meaning
    )


class DummyEnv(gym.Env):
    # The DummyEnv is modified from CartPole
    # https://github.com/openai/gym/blob/master/gym/envs/classic_control/cartpole.py
    def __init__(self, fps, obs_size):
        self.action_space = gym.spaces.Discrete(2)
        print 'FPS: ', fps
        print 'Observation size: ', obs_size
        self.fps = fps
        self.obs_size = obs_size
        self._compute_time = 1.0 / self.fps
        _start = time.time()

    def _reset(self):
        pass

    def _step(self, action):
        _start = time.time()
        obs = np.random.rand(self.obs_size)
        # It is important to notice the random observation is not compressable
        reward = 1.0
        info = {}
        done = False
        _elapse = time.time() - _start

        # Use sleep to simulate the computation time
        time.sleep(max(self._compute_time - _elapse, 0))
        # The sleep function is not very accurate, longer than my request
        # See here http://stackoverflow.com/questions/1133857/how-accurate-is-pythons-time-sleep
        return obs, reward, done, info
