import gym
import dummy_env

def test_dummy_env():
    env = gym.make('dummy/OBS1000-FPS60-v0')
    for episode in range(100):
        for t in range(100):
            action = env.action_space.sample()
            obs, reward, done, info = env.step(action)

    pass

if __name__ == '__main__':
    test_dummy_env()
