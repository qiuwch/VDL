import sys
from socket import *

import gym

server_port = 10080

max_len = 1024

serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', server_port))
serverSocket.listen(5)

env = gym.make('CartPole-v0')

connectionSocket, addr1 = serverSocket.accept()
connectionSocket, addr2 = serverSocket.accept()
while True:
    try:
        message = connectionSocket.recv(max_len)
        if int(message.split()[1]) == 1:
            max_len = int(message.split()[2])*1024
            print 'observation length:' + message.split()[2]
        if int(message.split()[1]) == 2:
            if int(message.split()[0]) == 1:
                print 'reward from actor 1:' + message.split()[2]
            if int(message.split()[0]) == 2:
                print 'reward from actor 2:' + message.split()[2]
        if int(message.split()[1]) == 3:
            if int(message.split()[0]) == 1:
                print 'observation from actor 1:' + message.split()[2]
            if int(message.split()[0]) == 2:
                print 'observation from actor 2:' + message.split()[2]

        action = env.action_space.sample()
        connectionSocket.send(str(action))
    except IOError:
        print 'Generating action fail.'

serverSocket.close()


