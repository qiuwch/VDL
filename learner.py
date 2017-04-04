import sys
from socket import *
import time
import errno

import gym

num_actors = int(sys.argv[1])

server_port = range(num_actors)
serverSocket = range(num_actors)
ACTOR = [True for _ in range(num_actors)]
connectionSocket = range(num_actors)
addr = range(num_actors)
port_num = 10000
for i in range(0, num_actors):
    server_port[i] = (port_num+i)
    serverSocket[i] = socket(AF_INET, SOCK_STREAM)
    serverSocket[i].bind(('', server_port[i]))
    serverSocket[i].listen(5)
    connectionSocket[i], addr[i] = serverSocket[i].accept()
    connectionSocket[i].settimeout(1.0)

env = gym.make('CartPole-v0')

t0 = time.time()

while True:
    action = env.action_space.sample()
    #print action

    for i in range(num_actors):
        if ACTOR[i]:
            try:
                #time.sleep(0.05)
                message_len = connectionSocket[i].recv(5)
                print message_len
                if message_len:
                    if message_len == 'over':
                        ACTOR[i] = False
                    else:
			message = connectionSocket[i].recv(int(message_len.split()[0]))
		        if message_len.split()[1] == 'o':
			    observation = message
			    print 'ob_%d:' % i + str(observation)
		        if message_len.split()[1] == 'r':
			    reward = message
			    print 're_%d:' % i + str(reward)
			    connectionSocket[i].send(str(action))
            except error:
                pass
                #err = e.args[0]
                #if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                    #pass
                #else:
		    #pass
                    #ACTOR[i] = False

    if any(ACTOR):
        pass
    else:
        break

t1 = time.time()
print (t1-t0)

for i in range(num_actors):
    serverSocket[i].close()


