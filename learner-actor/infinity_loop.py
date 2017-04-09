# An infinity loop to test the ssh remote execution.
import time
while True:
    print 'Hello'
    time.sleep(1)

# ssh n001 "python ${HOME}/workspace/VDL/VDL/learner-actor/infinity_loop.py"
# ssh n001 -f "python ${HOME}/workspace/VDL/VDL/learner-actor/infinity_loop.py"
