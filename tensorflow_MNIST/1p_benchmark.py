import sys
import os
import time

if __name__ == '__main__':
  # Train
  batch_runtime = float(sys.argv[1])
  num_rounds = int(sys.argv[2])
  payload_kb_size = int(sys.argv[3])
  
  t0 = time.time()
  for _ in range(num_rounds):
    payload = bytearray(payload_kb_size * 1000)
    time.sleep(batch_runtime)

  t1 = time.time()
  print "Time passed: ", t1-t0
