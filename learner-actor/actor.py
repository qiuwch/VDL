import sys, socket, struct, zlib, argparse
import gym
from util import Timer, Counter
import dummy_env
try:
    import ppaquette_gym_doom
except:
    pass

def log(msg):
    # print msg
    pass

parser = argparse.ArgumentParser()
parser.add_argument('--server_ip')
parser.add_argument('--port', type=int)
parser.add_argument('--task')
parser.add_argument('--compress', action='store_true')

args = parser.parse_args()
server_host = args.server_ip
server_port = args.port
task = args.task

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print 'ClientSocket is waiting for connection'
clientSocket.connect((server_host, server_port))
print 'ClientSocket is connected'

send_timer = Timer("Communication")
compress_timer = Timer("Compression")
compute_timer = Timer("Computation")
throughput_counter = Counter("Network Throughput")
total_timer = Timer("Total")

def send_payload(connection_socket, payload):
    # Make sure payload is a bytearray
    payload_size = len(payload)
    throughput_counter.add(payload_size + 1) # +1 for header
    connection_socket.send(struct.pack('I', payload_size))
    connection_socket.send(payload)

def serialize_numpy(arr):
    # http://stackoverflow.com/questions/30167538/convert-a-numpy-ndarray-to-stringor-bytes-and-convert-it-back-to-numpy-ndarray
    payload = arr.tostring()
    payload = zlib.compress(payload)
    return payload

def send_us(observation, reward):
    # It seems this function call takes a unreasonable amount of time
    # Does a deep copy happen in here?
    if args.compress:
        compress_timer.tic()
        payload = serialize_numpy(observation)
        payload = zlib.compress(payload)
        compress_timer.toc()
    else:
        payload = serialize_numpy(observation)

    send_timer.tic()
    send_payload(clientSocket, payload)
    send_timer.toc()


def main():
    env = gym.make(task)
    total_timer.tic()
    for i_episode in range(100):
        observation = env.reset()
        log(observation)
        send_us(observation, 0)
        # !!! Do not do str(observation) in the debug code, this operation is very expensive !!!
        for t in range(100):
            # print "Episode: %d      Iter: %d" % (i_episode, t)
            #env.render()
            compute_timer.tic()
            action = env.action_space.sample()
            compute_timer.toc()
            #try:
            # action = 0
            # send_timer.tic()
            # raw_action = clientSocket.recv(4)
            # action = struct.unpack('I', raw_action)[0]
            # send_timer.toc()

            compute_timer.tic()
            observation, reward, done, info = env.step(action)
            compute_timer.toc()

            send_us(observation, reward)

            if done:
                log("Episode finished after {} timesteps".format(t+1))
                break
    total_timer.toc()

    # Make sure the buffer is empty
    # data = clientSocket.recv(1000, socket.MSG_PEEK) # This will block IO
    # assert data == None, 'Unprocessed data is remaining in the socket buffer'
    clientSocket.close() # If the connection is closed when still data in the buffer.
    # The connection is reset by peer will happen

    print total_timer
    print send_timer
    print compute_timer
    print compress_timer
    print throughput_counter
    print 'Speed: %.2fKB/s' % (throughput_counter.sum / send_timer.total / 1000.0)

    # Print how much time is spent in the env.step and how much time is spent in sending messages


    #clientSocket.close()
if __name__ == '__main__':
    main()
