id=$1
# python run.py --env-id flashgames.NeonRace-v0 --num_actors 2 --log-dir train-log/ps-`hostname`
# python ps_run.py --env-id flashgames.NeonRace-v0 --num_actors 0 --log-dir train-log/ps-`hostname` --num-workers 5 --task ${id} 

# Very basic
# python ps_run.py --num_actors 0 --log-dir train-log/ps-`hostname`  --task 0 --job-name worker
python ps_run.py --env-id flashgames.NeonRace-v0 --num_actors 2 --log-dir train-log/worker-`hostname` --task ${id} --job-name worker
