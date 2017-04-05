import sys
import socket, struct
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
    serverSocket[i] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
                raw_message_len = connectionSocket[i].recv(4)
                if raw_message_len:
                    if raw_message_len == 'over':
                        print raw_message_len
                        ACTOR[i] = False
                    else:
                        message_len = struct.unpack('I', raw_message_len)[0]
                        print message_len
                        message = connectionSocket[i].recv((message_len+2))
                        if message.split('_')[0] == 'o':
                            observation = message.split('_')[1]
                            print 'ob_%d:' % i + str(observation)
                        if message.split('_')[0] == 'r':
                            reward = message.split('_')[1]
                            print 're_%d:' % i + str(reward)
                            connectionSocket[i].send(struct.pack('I', action))
            except socket.error:
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


