if [ -z $1 ]; then
    task=Breakout-v0
else
    task=$1
fi
# python baseline.py CartPole-v0
python baseline.py ${task}
# python baseline.py Hopper-v1
# python baseline.py Humanoid-v1
