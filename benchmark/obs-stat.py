import gym
env_names = ['CartPole-v0', 'Breakout-v0', 'Hopper-v1', 'Humanoid-v1']
try:
    import ppaquette_gym_doom
    env_names.append('ppaquette/DoomBasic-v0')
except:
    pass

def print_obs_info(env_name):
    env = gym.make(env_name)
    print env.observation_space

if __name__ == '__main__':
    for v in env_names:
        print_obs_info(v)
