import sys
from socket import *

import gym

server_host = 'localhost'
server_port = 10080

my_id = 2

clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((server_host, server_port))

def send_us(observation, reward):
    ob_len = len(observation)
    clientSocket.send(str(my_id) + ' 1 ' + str(ob_len))
    clientSocket.send(str(my_id) + ' 2 ' + str(observation))

    clientSocket.send(str(my_id) + ' 3 ' + str(reward))
    return

env = gym.make('CartPole-v0')
for i_episode in range(20):
    observation = env.reset()
    print observation
    send_us(observation, 0)
    for t in range(100):
        env.render()
        #action = env.action_space.sample()
        action = int(clientSocket.recv(1024))
        observation, reward, done, info = env.step(action)
        print observation
        print reward
        send_us(observation, reward)
        if done:
            print("Episode finished after {} timesteps".format(t+1))
            break

clientSocket.close()

