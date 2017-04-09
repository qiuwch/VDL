import sys
import socket, struct
import time
import errno

import gym

num_actors, task = int(sys.argv[1]), sys.argv[2]

def log(msg): # Use log function, so that I am able to disable the verbose output
    # print(msg)
    pass

k = 1400
def frag_recv(mess_len, sock):
    mess_remain = mess_len
    mess = ''
    if mess_remain > 0:
        mess_temp = sock.recv(min(mess_remain, k))
        mess += mess_temp
        mess_remain -= min(mess_remain, k)
    return mess

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

env = gym.make(task)

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
                    message_len = struct.unpack('I', raw_message_len)[0]
                    log(message_len)
                    message = frag_recv((message_len+2), connectionSocket[i])
                    if message.split('_')[0] == 'o':
                        observation = message.split('_')[1]
                        log('ob_%d:' % i + str(observation))
                    if message.split('_')[0] == 'r':
                        reward = message.split('_')[1]
                        log('re_%d:' % i + str(reward))
                        connectionSocket[i].send(struct.pack('I', action))
            except socket.error, e:
                err = e.args[0]
                if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                    pass
                else:
                    ACTOR[i] = False

    if any(ACTOR):
        pass
    else:
        break

t1 = time.time()
print (t1-t0)

for i in range(num_actors):
    serverSocket[i].close()


