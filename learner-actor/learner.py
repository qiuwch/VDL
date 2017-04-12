import sys, socket, struct, time, errno, atexit, argparse, json, threading, datetime
import gym
from util import Counter
import dummy_env
try:
    import ppaquette_gym_doom
except:
    pass

parser = argparse.ArgumentParser()
parser.add_argument('--num_actors', default = 2)
parser.add_argument('--task')
parser.add_argument('--port', default = 10000, type=int)
parser.add_argument('--log')

args = parser.parse_args()

env = gym.make(args.task)

class SocketRecvThread(threading.Thread):
    def __init__(self, connection_socket):
        super(SocketRecvThread, self).__init__()
        self.connection_socket = connection_socket
        self.connected = True
        self.buffer_size = 1400

    def _recv(self, count):
        if not self.connected:
            return None
        try:
            data = self.connection_socket.recv(count)
            if not data:
                self.connected = False
                return None
            return data
        except socket.error, e:
            print e
            self.connected = False
            return data

    def _frag_recv(self, mess_len):
        mess_remain = mess_len
        mess = ''
        if mess_remain > 0:
            mess_temp = self._recv(min(mess_remain, self.buffer_size))
            assert mess_temp != None, 'Mess_len %d, Mess_remain %d' % (mess_len, mess_remain)
            mess += mess_temp
            mess_remain -= len(mess_temp)
        return mess

    def run(self):
        print 'Thread is running'
        self._recv_all()

    def _recv_all(self):
        while self.connected:
            raw_message_len = self._recv(4)
            if raw_message_len:
                message_len = struct.unpack('I', raw_message_len)[0]
                message = self._frag_recv(message_len)
                # raw_message_len = self._recv(4)
                # message_len = struct.unpack('I', raw_message_len)[0]
                # message = self._frag_recv(message_len+2)
                # if message.split('_')[0] == 'o':
                #     observation = message.split('_')[1]
                #     # log('ob_%d:' % i + str(observation))
                # if message.split('_')[0] == 'r':
                #     reward = message.split('_')[1]
                    # log('re_%d:' % i + str(reward))

                # action = env.action_space.sample() # based on observation and reward
                # self.connection_socket.send(struct.pack('I', action))


def log(msg): # Use log function, so that I am able to disable the verbose output
    # print(msg)
    pass

def main():
    server_port = args.port
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', server_port))
    server_socket.listen(5)

    client_addrs = []
    recv_threads = []
    for i in range(0, args.num_actors):
        # Create a new thread to handle data
        connection_socket, addr = server_socket.accept()
        client_addrs.append(addr)
        recv_thread = SocketRecvThread(connection_socket)
        recv_threads.append(recv_thread)

    for thread in recv_threads:
        thread.start()

    t0 = time.time()
    for thread in recv_threads:
        thread.join()
    t1 = time.time()
    total_time = (t1 - t0)
    print 'Total time in learner: ', total_time

    # Log is a summary with all the information related to this experiment
    if args.log:
        with open(args.log, 'w') as f:
            log_data = dict(
                num_actors = args.num_actors,
                date = str(datetime.datetime.now()),
                total_time = total_time,
                task = args.task,
                client_addrs = client_addrs,
                mode = 'multi-machine'
            )
            json.dump(log_data, f)

if __name__ == '__main__':
    main()
