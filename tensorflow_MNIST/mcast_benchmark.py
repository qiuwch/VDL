import sys
import time
import Queue
import threading
import socket_util

class SockListenThread(threading.Thread):
    """
    Thread class that listens for socket message receiving. It terminates when stop() is called.
    """

    def __init__(self, sock, self_IP, inc_msg_q, num_peers, ret_val):
        super(SockListenThread, self).__init__()
        self.sock = sock
        self.self_IP = self_IP
        self.inc_msg_q = inc_msg_q
        self.num_peers = num_peers
        self.ret_val = ret_val
        self._stop = threading.Event()

    def run(self):
        while not self.stopped():
            socket_util.socket_recv_chucked_data(self.sock, self.self_IP, self.inc_msg_q, self.num_peers, 0)
        # thread terminating
        time.sleep(1)
        socket_util.socket_recv_chucked_data(self.sock, self.self_IP, self.inc_msg_q, self.num_peers, 0)
        ret_val.put(-1)
    
    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

def create_sock_listen_thread(sock, self_IP, inc_msg_q, num_peers, ret_val):
  '''
  Create a SockListenThread and run it
  @params sock The socket to use
  @param self_IP The IP address of self
  @param inc_msg_q Incoming message queue storing messages from other peers
  @param num_peers Number of peers
  @param ret_val Queue for return value
  @return The thread
  '''
  sock_listen_thread = SockListenThread(sock, self_IP, inc_msg_q, num_peers, ret_val)
  sock_listen_thread.start()
  return sock_listen_thread
  
        
if __name__ == '__main__':
  sock, self_IP, mcast_destination = socket_util.set_up_UDP_mcast_peer()
  socket_util.await_start_mcast(sock)
  
  num_peers = int(sys.argv[1])
  batch_runtime = float(sys.argv[2])
  num_rounds = int(sys.argv[3])
  payload_kb_size = int(sys.argv[4])
  
  # Train
  inc_msg_q = Queue.Queue()
  ret_val = Queue.Queue()
  sock_listen_thread = create_sock_listen_thread(sock, self_IP, inc_msg_q, num_peers, ret_val)
  
  t0 = time.time()
  for _ in range(num_rounds):
    payload = bytearray(payload_kb_size * 1000)
    time.sleep(batch_runtime)
    socket_util.socket_send_data_chucks(sock, payload, mcast_destination, 0)
    
    while not inc_msg_q.empty():
        # Process received delta_W, delta_b from other peers
        payload_from_others = inc_msg_q.get(False)  
  sock_listen_thread.stop()
  ret_val.get()
  while not inc_msg_q.empty():
    # Process received delta_W, delta_b from other peers
    payload_from_others = inc_msg_q.get(False) 
  t1 = time.time()
  
  socket_util.close_UDP_mcast_peer(sock)
  print "Time passed: ", t1-t0
  