import sys
from socket import *

import gym

server_host = 'localhost'
server_port = 10080

clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((server_host, server_port))

def send_us(obser):
    obser_len = len(observation, reward)
    clientSocket.send(obser_len)
    clientSocket(observation)

    reward_len = len(reward)
    clientSocket(reward_len)
    clientSocket(reward)
    return

env = gym.make('CartPole-v0')
for i_episode in range(20):
    observation = env.reset()
    print observation
    send_us(observation, 0)
    for t in range(100):
        env.render()
        print(observation)

        action = env.action_space.sample()
        observation, reward, done, info = env.step(action)
        send_us(observation, reward)
        if done:
            print("Episode finished after {} timesteps".format(t+1))
            break


