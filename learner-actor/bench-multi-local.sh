# Star the learner
learner_bin=learner.py
actor_bin=${HOME}/workspace/VDL/VDL/learner-actor/actor.py
server='127.0.0.1'
task=Breakout-v0
# task=Humanoid-v1
port=10000

echo "Start learner"
python ${learner_bin} --port ${port} &
sleep 1 # Wait for the server to boot
echo "Start actor1"
python ${actor_bin} ${server} ${port} ${task} &
echo "Start actor2"
python ${actor_bin} ${server} ${port} ${task} &
