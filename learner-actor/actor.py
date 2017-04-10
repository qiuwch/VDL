import sys
import socket, struct
import gym
from util import Timer, Counter

def log(msg):
    # print msg
    pass

server_host, server_port, task = sys.argv[1], int(sys.argv[2]), sys.argv[3]

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.connect((server_host, server_port))

send_timer = Timer("Communication")
compute_timer = Timer("Computation")
throughput_counter = Counter("Network Throughput")

def send_payload(connection_socket, payload):
    # Make sure payload is a bytearray
    payload_size = len(payload)
    connection_socket.send(struct.pack('I', payload_size))
    connection_socket.send(payload)

def send_us(observation, reward):
    send_payload(clientSocket, str(observation))
    send_payload(clientSocket, str(reward))

env = gym.make(task)
for i_episode in range(10):
    observation = env.reset()
    log(observation)
    send_us(observation, 0)
    for t in range(100):
        # print "Episode: %d      Iter: %d" % (i_episode, t)
        #env.render()
        #action = env.action_space.sample()
        #try:
        action = 0
        # send_timer.tic()
        # raw_action = clientSocket.recv(4)
        # action = struct.unpack('I', raw_action)[0]
        # send_timer.toc()

        compute_timer.tic()
        observation, reward, done, info = env.step(action)
        compute_timer.toc()

        log('ob:' + str(observation))
        log('re:' + str(reward))

        payload = str(observation) + str(reward)
        b = bytearray()
        b.extend(payload)
        throughput_counter.add(len(b))
        send_timer.tic()
        send_us(observation, reward)
        send_timer.toc()

        if done:
            log("Episode finished after {} timesteps".format(t+1))
            break

# Make sure the buffer is empty
# data = clientSocket.recv(1000, socket.MSG_PEEK) # This will block IO
# assert data == None, 'Unprocessed data is remaining in the socket buffer'
clientSocket.close() # If the connection is closed when still data in the buffer.
# The connection is reset by peer will happen

print send_timer
print compute_timer
print throughput_counter
print 'Speed: %.2fKB/s' % (throughput_counter.sum / send_timer.total / 1000.0)

# Print how much time is spent in the env.step and how much time is spent in sending messages


#clientSocket.close()
