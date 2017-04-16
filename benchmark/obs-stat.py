import gym
import json
import numpy as np
env_names = ['CartPole-v0', 'Breakout-v0', 'Hopper-v1', 'Humanoid-v1']
try:
    import ppaquette_gym_doom
    env_names.append('ppaquette/DoomDeathmatch-v0')
except:
    pass

def print_obs_info(env_name):
    env = gym.make(env_name)
    print env.observation_space
    log_data = dict(
        env_name = env_name,
        obs_size = np.prod(env.observation_space.shape),
        obs_shape = str(env.observation_space),
    )
    with open('log/%s-obs.json' % env_name, 'w') as f:
        json.dump(log_data, f)

if __name__ == '__main__':
    for v in env_names:
        print_obs_info(v)
