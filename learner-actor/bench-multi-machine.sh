# Star the learner
learner_bin=learner.py
actor_bin=${PWD}/actor.py 
server='10.1.1.1'
port=10000
if [ -z $1 ]; then
    task=Breakout-v0
else
    task=$1
fi

echo "Start learner"
python learner.py --port 10000 --task ${task} &
echo "Start actor1"
ssh n001 -f "source ~/.bash_profile; python ${actor_bin} ${server} ${port} ${task}"
echo "Start actor2"
ssh n003 -f "source ~/.bash_profile; python ${actor_bin} ${server} ${port} ${task}"

