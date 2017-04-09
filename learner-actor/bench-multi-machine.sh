# Star the learner
python learner.py 2 Breakout-v0
ssh n001 "source ~/.bash_profile; python actor.py yuille-fb-head 10000 Breakout-v0"
ssh n002 "source ~/.bash_profile; python actor.py yuille-fb-head 10001 Breakout-v0"
