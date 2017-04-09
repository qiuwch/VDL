# Star the learner
learner_bin=learner.py
actor_bin=${HOME}/workspace/VDL/VDL/learner-actor/actor.py 
server=10.1.1.1
task=Breakout-v0

echo "Start learner"
python learner.py 2 Breakout-v0 &
echo "Start actor1"
ssh n001 -f "source ~/.bash_profile; python ${actor_bin} ${server} 10000 Breakout-v0"
echo "Start actor2"
ssh n003 -f "source ~/.bash_profile; python ${actor_bin} ${server} 10001 Breakout-v0"
