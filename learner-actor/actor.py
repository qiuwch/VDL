import sys
import socket, struct

import gym

def log(msg):
    pass

server_host, server_port, task = sys.argv[1], int(sys.argv[2]), sys.argv[3]

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.connect((server_host, server_port))

def send_us(observation, reward):
    ob_len = len(str(observation))
    log('ob_len:' + str(ob_len))
    clientSocket.send(struct.pack('I', ob_len))
    clientSocket.send('o_' + str(observation))

    re_len = len(str(reward))
    log('re_len:' + str(re_len))
    clientSocket.send(struct.pack('I', re_len))
    clientSocket.send('r_' + str(reward))
    return

env = gym.make(task)
for i_episode in range(10):
    observation = env.reset()
    log(observation)
    send_us(observation, 0)
    for t in range(100):
        #env.render()
        #action = env.action_space.sample()
        #try:
        raw_action = clientSocket.recv(4)
        action = struct.unpack('I', raw_action)[0]
        observation, reward, done, info = env.step(action)
        log('ob:' + str(observation))
        log('re:' + str(reward))
        send_us(observation, reward)
        if done:
            log("Episode finished after {} timesteps".format(t+1))
            break

clientSocket.send('over')
print "over"


#clientSocket.close()

