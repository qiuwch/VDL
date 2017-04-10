# A simple script to test the upper bound socket communication speed we can achieve
import argparse, socket, sys, os, threading
script_path = os.path.dirname(__file__)
sys.path.append(os.path.join(script_path, '..'))
from util import Timer, Counter
import numpy as np

send_timer = Timer("Communication")
throughput_counter = Counter("Network Throughput")

packet_size = 100000 # bytes
packet_count = 1000

class RecvThread(threading.Thread):
    def __init__(self, connection):
        super(RecvThread, self).__init__()
        self.connection = connection

    def run(self):
        while True:
            data = self.connection.recv(1000)
            if not data:
                print 'Done'
                break


port = 10010
def server(num_client):
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.bind(('', port))
    listen_socket.listen(5)

    recv_threads = []
    for i in range(num_client):
        connection, addr = listen_socket.accept()
        recv_threads.append(RecvThread(connection))

    for thread in recv_threads:
        thread.start()

    for thread in recv_threads:
        thread.join()

def client(server_ip):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, port))

    send(client_socket, packet_size, packet_count)
    client_socket.close()

def send(client_socket, size, count):
    for i in range(count):
        random_array = np.random.rand((size))
        payload = random_array.tobytes()
        send_timer.tic()
        client_socket.send(payload)
        send_timer.toc()
        throughput_counter.add(len(payload))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', action='store_true')
    parser.add_argument('--num_client', type=int, default=1)
    parser.add_argument('--client', action='store_true')
    parser.add_argument('--server_ip', default='localhost')
    args = parser.parse_args()

    if args.server:
        server(args.num_client)

    if args.client:
        client(args.server_ip)
        print throughput_counter
        print send_timer
        print 'Speed: %.2fKB/s' % (throughput_counter.sum / send_timer.total / 1000)

if __name__ == '__main__':
    main()
