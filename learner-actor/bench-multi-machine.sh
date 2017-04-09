# Star the learner
python learner.py 2 Breakout-v0
server=10.1.1.1
ssh n001 "source ~/.bash_profile; python actor.py ${server} 10000 Breakout-v0"
ssh n002 "source ~/.bash_profile; python actor.py ${server} 10001 Breakout-v0"
