import sys
from socket import *
import time, errno

import gym

def log(msg):
    # print msg
    pass

server_port_1 = 10080
server_port_2 = 10090

serverSocket_1 = socket(AF_INET, SOCK_STREAM)
serverSocket_1.bind(('', server_port_1))
serverSocket_1.listen(5)

serverSocket_2 = socket(AF_INET, SOCK_STREAM)
serverSocket_2.bind(('', server_port_2))
serverSocket_2.listen(5)

env = gym.make('CartPole-v0')

connectionSocket_1, addr1 = serverSocket_1.accept()
ACTOR1 = True
connectionSocket_1.settimeout(1.0)

connectionSocket_2, addr2 = serverSocket_2.accept()
ACTOR2 = True
connectionSocket_2.settimeout(1.0)

t0 = time.time()

while True:
    action = env.action_space.sample()
    #print action

    if ACTOR1:
        try:
            # time.sleep(0.05)
            message_1_len = connectionSocket_1.recv(5)
            log(message_1_len)
            if message_1_len:
                if message_1_len == 'over':
                    ACTOR1 = False
                else:
                    message_1 = connectionSocket_1.recv(int(message_1_len.split()[0]))
                    if message_1_len.split()[1] == 'o':
                        observation_1 = message_1
                        log('ob_1:' + str(observation_1))
                    if message_1_len.split()[1] == 'r':
                        reward_1 = message_1
                        log('re_1:' + str(reward_1))
                        connectionSocket_1.send(str(action))
        except error, e:
            err = e.args[0]
            if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                pass # No data to read
            else:
                ACTOR1 = False

    if ACTOR2:
        try:
            # time.sleep(0.05)
            message_2_len = connectionSocket_2.recv(5)
            log(message_2_len)
            if message_2_len:
                if message_2_len == 'over':
                    ACTOR2 = False
                else:
                    message_2 = connectionSocket_2.recv(int(message_2_len.split()[0]))
                    if message_2_len.split()[1] == 'o':
                        observation_2 = message_2
                        log('ob_2:' + str(observation_2))
                    if message_2_len.split()[1] == 'r':
                        reward_2 = message_2
                        log('re_2:' + str(reward_2))
                        connectionSocket_2.send(str(action))
        except error, e:
            err = e.args[0]
            if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                pass # No data to read
            else:
                ACTOR2 = False




    if (not ACTOR1) and (not ACTOR2):
        break

t1 = time.time()
print (t1-t0)

serverSocket_1.close()
serverSocket_2.close()
