#import sys
#from socket import *

import gym
import time

t0 = time.time()
#server_host = 'localhost'
#server_port = 10090

#clientSocket = socket(AF_INET, SOCK_STREAM)
#clientSocket.connect((server_host, server_port))

# def send_us(observation, reward):
#     ob_len = len(str(observation))
#     print 'ob_len:' + str(ob_len)
#     clientSocket.send(str(ob_len) + ' o ' + str(observation))
# 
#     re_len = len(str(reward))
#     print 're_len:' + str(re_len)
#     clientSocket.send('0' + str(re_len) + ' r ' + str(reward))
#     return
# 
env = gym.make('CartPole-v0')
for i_episode in range(20):
    observation = env.reset()
    #print observation
    #send_us(observation, 0)
    for t in range(100):
        #env.render()
        action = env.action_space.sample()
        #action = int(clientSocket.recv(1))
        observation, reward, done, info = env.step(action)
        #print 'ob:' + str(observation)
        #print 're:' + str(reward)
        #send_us(observation, reward)
        if done:
            #print("Episode finished after {} timesteps".format(t+1))
            break

t1 = time.time()
print (t1-t0)
#clientSocket.send('over')
#clientSocket.close()

