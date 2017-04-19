`worker_num=2`

In node1 `python run.py --log-dir /tmp/neonrace --env-id flashgames.NeonRace-v0 --num-workers ${worker_num} --task 0 --remotes 1`

In node2 `python run.py --log-dir /tmp/neonrace --env-id flashgames.NeonRace-v0 --num-workers ${worker_num} --task 1 --remotes 1`

In any node, `python start_mcast.py`
