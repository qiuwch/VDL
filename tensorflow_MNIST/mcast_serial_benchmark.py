import sys
import time
import Queue
import socket_util
  
        
if __name__ == '__main__':
  sock, self_IP, mcast_destination = socket_util.set_up_UDP_mcast_peer()
  socket_util.await_start_mcast(sock)
  
  num_peers = int(sys.argv[1])
  batch_runtime = float(sys.argv[2])
  num_rounds = int(sys.argv[3])
  payload_kb_size = int(sys.argv[4])
  
  computation_time = communication_time = 0
  
  # Train
  inc_msg_q = Queue.Queue()
  
  for _ in range(num_rounds):
    t0 = time.time()
    payload = bytearray(payload_kb_size * 1000)
    time.sleep(batch_runtime)
    t1 = time.time()
    computation_time += t1 - t0
    
    t2 = time.time()
    socket_util.socket_send_data_chucks(sock, payload, mcast_destination, 0)
    
    socket_util.socket_recv_chucked_data(sock, self_IP, inc_msg_q, num_peers, 0)
    t3 = time.time()
    communication_time += t3 - t2
    
    t4 = time.time()
    while not inc_msg_q.empty():
        # Process received delta_W, delta_b from other peers
        payload_from_others = inc_msg_q.get(False)  
    t5 = time.time()
    computation_time += t5 - t4
   
  socket_util.close_UDP_mcast_peer(sock)
  print "Computation time: ", computation_time
  print "Communication time: ", communication_time
  