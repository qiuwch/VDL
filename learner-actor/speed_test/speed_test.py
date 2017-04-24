# A simple script to test the upper bound socket communication speed we can achieve
import argparse, socket, sys, os, threading
import multiprocessing
import time
script_path = os.path.dirname(__file__)
sys.path.append(os.path.join(script_path, '..'))
from util import Timer, Counter
import numpy as np

send_timer = Timer("Communication")
throughput_counter = Counter("Network Throughput")
throughput_counter_2 = Counter("Troughput expected")
throughput_recv = Counter("Data received")
#packet_size = 100000 # bytes
#packet_count = 1000

class RecvThread(multiprocessing.Process):
    def __init__(self, connection, size):
        super(RecvThread, self).__init__()
        self.connection = connection
        self.size = size

    def run(self):
        while True:
            data = self.connection.recv(self.size)
            #print len(data)
            throughput_recv.add(len(data))
            #print throughput_recv
            #print data
            if not data:
                print 'Done'
                break
        print throughput_recv

#port = 10010
def server(num_client, port, size):
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.bind(('', port))
    listen_socket.listen(5)

    recv_threads = []
    for i in range(num_client):
        connection, addr = listen_socket.accept()
        recv_threads.append(RecvThread(connection, size))

    for thread in recv_threads:
        thread.start()

    for thread in recv_threads:
        thread.join()

def client(server_ip, port, packet_size, packet_count, t):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, port))

    send(client_socket, packet_size, packet_count, t)
    client_socket.close()

def send(client_socket, size, count, t):
    for i in range(count):
        random_array = np.random.rand((size))
        payload = random_array.tobytes()
        send_timer.tic()
        time.sleep(t)
        client_socket.send(payload)
        send_timer.toc()
        #print payload
        throughput_counter.add(len(payload))
        #throughput_counter_2.add(size)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', action='store_true')
    parser.add_argument('--num_client', type=int, default=1)
    parser.add_argument('--client', action='store_true')
    parser.add_argument('--server_ip', default='localhost')
    parser.add_argument('--port', type=int, default=10011)
    parser.add_argument('--packet_size', type=int, default=100000)
    parser.add_argument('--packet_count', type=int, default=1000)
    parser.add_argument('--sleep', type=float, default=0)
    parser.add_argument('--recv_size', type=int, default=1400)
    args = parser.parse_args()

    if args.server:
        server(args.num_client, args.port, args.recv_size)
        #print throughput_recv

    if args.client:
        client(args.server_ip, args.port, args.packet_size, args.packet_count, args.sleep)
        print throughput_counter
        print send_timer
        #print throughput_counter_2
        #print throughput_recv
        #print 'Speed: %.2fKB/s' % (throughput_counter.sum / send_timer.total / 1000)

if __name__ == '__main__':
    main()
