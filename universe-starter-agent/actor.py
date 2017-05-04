import sys, socket, struct, zlib, argparse
import gym
from util import Timer, Counter
#import dummy_env
import cPickle
from envs import create_env
try:
    import ppaquette_gym_doom
except:
    pass

def log(msg):
    # print msg
    pass

parser = argparse.ArgumentParser()
parser.add_argument('--server_ip')
parser.add_argument('--port', type=int, default=10000)
parser.add_argument('--env-id', default="PongDeterministic-v3", help='Environment id')
parser.add_argument('--compress', action='store_true')
parser.add_argument('--task', default=0, type=int, help='Task index')
parser.add_argument('-r', '--remotes', default=None)

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
frame_count = Counter("frame count")

def send_payload(connection_socket, payload):
    # Make sure payload is a bytearray
    payload_size = len(payload)
    throughput_counter.add(payload_size + 4) # +1 for header
    connection_socket.send(struct.pack('I', payload_size))
    connection_socket.send(payload)

def serialize_pickle(data):
    # http://stackoverflow.com/questions/30167538/convert-a-numpy-ndarray-to-stringor-bytes-and-convert-it-back-to-numpy-ndarray
    payload = cPickle.dumps(data)
    #payload = zlib.compress(payload)
    return payload

def send_us(observation, reward, done, info):
    # It seems this function call takes a unreasonable amount of time
    # Does a deep copy happen in here?

    data = dict(
        obs = observation,
        reward = reward,
        terminal = done,
        info = info,
    )
#    print (data)

    if args.compress:
        compress_timer.tic()
        payload = serialize_pickle(data)
        payload = zlib.compress(payload)
        compress_timer.toc()
    else:
        payload = serialize_pickle(data)

    send_timer.tic()
    send_payload(clientSocket, payload)
    send_timer.toc()


def main():
    env = create_env(args.env_id, client_id=str(args.task), remotes=args.remotes)
    '''
    total_timer.tic()
    for i_episode in range(100):
        observation = env.reset()
        #log(observation)
        send_us(observation, 0, False, dict(extra_field=''))
        # !!! Do not do str(observation) in the debug code, this operation is very expensive !!!
        for t in range(100):
            # print "Episode: %d      Iter: %d" % (i_episode, t)
            #env.render()
            #compute_timer.tic()
            #action = env.action_space.sample()
            #compute_timer.toc()
            #try:
            # action = 0
            # send_timer.tic()
'''
    observation = env.reset()
    send_us(observation, 0, 0, 0)
    while True:
        raw_action = clientSocket.recv(4)
        if raw_action == 'rest':
            observation = env.reset()
            send_us(observation, 0, 0, 0)
        else:
            action = struct.unpack('I', raw_action)[0]
            # send_timer.toc()
#        compute_timer.tic()
            observation, reward, done, info = env.step(action)
#        compute_timer.toc()

            send_us(observation, reward, done, info)
#            frame_count.add(1)

#            if done:
#                log("Episode finished after {} timesteps".format(t+1))
#                break
#    total_timer.toc()

    # Make sure the buffer is empty
    # data = clientSocket.recv(1000, socket.MSG_PEEK) # This will block IO
    # assert data == None, 'Unprocessed data is remaining in the socket buffer'
    #clientSocket.close() # If the connection is closed when still data in the buffer.
    # The connection is reset by peer will happen

    print total_timer
    print send_timer
    print compute_timer
    print compress_timer
    print throughput_counter
    print 'Speed: %.2fKB/s' % (throughput_counter.sum / send_timer.total / 1000.0)
    print frame_count

    # Print how much time is spent in the env.step and how much time is spent in sending messages

    #clientSocket.close()
if __name__ == '__main__':
    main()
