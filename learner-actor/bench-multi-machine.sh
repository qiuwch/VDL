# Star the learner
learner_bin=learner.py
actor_bin=${HOME}/workspace/VDL/VDL/learner-actor/actor.py 
echo "Start learner"
python learner.py 2 Breakout-v0 &
echo "Start actor1"
ssh n001 "source ~/.bash_profile; python ${actor_bin} yuille-fb-head 10000 Breakout-v0"
echo "Start actor2"
ssh n003 "source ~/.bash_profile; python ${actor_bin} yuille-fb-head 10001 Breakout-v0"
