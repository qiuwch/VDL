import sys
import gym

env = gym.make(sys.argv[1])
env.reset()
for _ in range(1000):
    env.render()
    env.step(env.action_space.sample()) # take a random action