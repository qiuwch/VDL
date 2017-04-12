import sys
import os
import time

if __name__ == '__main__':
  # Train
  batch_runtime = float(sys.argv[1])
  num_rounds = int(sys.argv[2])
  payload_kb_size = int(sys.argv[3])
  
  computation_time = 0
  
  for _ in range(num_rounds):
    t0 = time.time()
    payload = bytearray(payload_kb_size * 1000)
    time.sleep(batch_runtime)
    t1 = time.time()
    computation_time += t1 - t0
  
  print "Computation time: ", computation_time
  print "Communication time: ", 0
