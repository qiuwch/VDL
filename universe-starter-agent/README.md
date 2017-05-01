This code is modified from https://github.com/openai/universe-starter-agent. This is the [original readme file](readme_a3c.md).

The original code is modified with P2P learner communication and multi-machine learner-actor.

## Baseline

The `PongDeterministic-v3`

```shell
python run.py --logdir train-log/pong-baseline
```

The training result can be visualize in tensorboard, a tool to visualize the training result of tensorflow. To see the training result in tensorboard, use `tensorboard --logdir train-log/pong-baseline`. Use internet browser (such as chrome) to open the url printed in the console

The `flashgames.NeonRace-v0`

```shell
python run.py --env-id flashgames.NeonRace-v0 --logdir train-log/neonrace-baseline
```


## Learner - multiple actors 
Run run.py without defining value of num_actors to run one environment locally. `python run.py --env-id flashgames.NeonRace-v0`

To run two actors, do `python run.py --env-id flashgames.NeonRace-v0 --num_actors 2 --port (...)` to run learner. Port number is 10000 as default. And do `python actor.py --server_ip (...) --port (...)`on two different machine to run actors. Server ip is ccvl2 as default.

## Multiple learners
```shell
python run.py --num-workers 3 --log-dir train-log/pong-multi-learners-0 -id 0
python run.py --num-workers 3 --log-dir train-log/pong-multi-learners-1 -id 1
python run.py --num-workers 3 --log-dir train-log/pong-multi-learners-2 -id 2
```

In any machine
```shell
python start_spread.py
```

To clean up the train log
```shell
rm train-log/pong-multi-learners* -r
```

