import sys
from socket import *

import gym

server_host, server_port = sys.argv[1], int(sys.argv[2])

#server_host = "localhost"
#server_port = 10001

clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((server_host, server_port))

def send_us(observation, reward):
    ob_len = len(str(observation))
    print 'ob_len:' + str(ob_len)
    clientSocket.send(str(ob_len) + ' o ' + str(observation))

    re_len = len(str(reward))
    print 're_len:' + str(re_len)
    clientSocket.send('0' + str(re_len) + ' r ' + str(reward))
    return

env = gym.make('CartPole-v0')
for i_episode in range(10):
    observation = env.reset()
    print observation
    send_us(observation, 0)
    for t in range(100):
        #env.render()
        #action = env.action_space.sample()
        #try:
        action = int(clientSocket.recv(1))
        #except timeout:
        #    continue
        observation, reward, done, info = env.step(action)
        print 'ob:' + str(observation)
        print 're:' + str(reward)
        send_us(observation, reward)
        if done:
            print("Episode finished after {} timesteps".format(t+1))
            break

clientSocket.send('over')
print "over"

while True:
    pass

#clientSocket.close()

