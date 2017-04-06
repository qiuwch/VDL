import gym

def print_obs_info(env_name):
    env = gym.make(env_name)
    print env.observation_space

if __name__ == '__main__':
    env_names = ['CartPole-v0', 'Breakout-v0', 'Hopper-v1', 'Humanoid-v1']
    for v in env_names:
        print_obs_info(v)
