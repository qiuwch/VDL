# Star the learner
learner_bin=learner.py
actor_bin=${PWD}/actor.py
server='127.0.0.1'
port=10000
if [ -z $1 ]; then
    task='CartPole-v0'
else
    task=$1
fi
# task=Humanoid-v1

echo "Start learner"
python ${learner_bin} --task ${task}&
sleep 1 # Wait for the server to boot
echo "Start actor1"
python ${actor_bin} --server_ip ${server} --port ${port} --task ${task} &
echo "Start actor2"
python ${actor_bin} --server_ip ${server} --port ${port} --task ${task} &
