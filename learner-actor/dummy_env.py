# This environment did nothing but trying to simulate problem of different sizes
import gym
import gym.spaces
import numpy as np
import time



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
        pass

    def _reset(self):
        pass

    def _step(self, action):
        _start = time.time()
        obs = np.zeros((300, 300))
        reward = 1.0
        info = {}
        done = False
        _elapse = time.time() - _start

        # Use sleep to simulate the computation time
        time.sleep(self._compute_time - _elapse)
        return obs, reward, done, info

# The env name contains two parts
# Observation size, measured by bytes
# Frame rate, measured by frames per second
gym.envs.registration.register(
    id='dummy/OBS%d-FPS%d-v0' % (1000, 60),
    entry_point='dummy_env:DummyEnv',
    kwargs=dict(
        fps=60,
        obs_size=1000,
    )
    # max_episode_steps=10000, # No actual meaning
    # reward_threshold=10.0, # No actual meaning
)
