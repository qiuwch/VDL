id=$1
# python run.py --env-id flashgames.NeonRace-v0 --num_actors 2 --log-dir train-log/ps-`hostname`
python run.py --env-id flashgames.NeonRace-v0 --num_actors 1 --log-dir train-log/ps-`hostname` -num_workers 5 --task ${id} 
