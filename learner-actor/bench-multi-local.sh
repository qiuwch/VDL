# Star the learner
learner_bin=learner.py
actor_bin=${HOME}/workspace/VDL/VDL/learner-actor/actor.py
server='127.0.0.1'
task=Breakout-v0

echo "Start learner"
python ${learner_bin} 2 Breakout-v0 &
sleep 1 # Wait for the server to boot
echo "Start actor1"
python ${actor_bin} ${server} 10000 Breakout-v0 &
echo "Start actor2"
python ${actor_bin} ${server} 10001 Breakout-v0 &
