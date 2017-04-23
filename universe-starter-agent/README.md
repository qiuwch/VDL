This code is modified from https://github.com/openai/universe-starter-agent. This is the [original readme file](readme_a3c.md).

The original code is modified with P2P learner communication and multi-machine learner-actor.

## Baseline

The `PongDeterministic-v3`

`python run.py --logdir train-log/pong-baseline`

The training result can be visualize in tensorboard, a tool to visualize the training result of tensorflow. To see the training result in tensorboard, use `tensorboard --logdir train-log/pong-baseline`. Use internet browser (such as chrome) to open the url printed in the console

The `flashgames.NeonRace-v0`

`python run.py --env-id flashgames.NeonRace-v0 --logdir train-log/neonrace-baseline`


## Learner - multiple actors 

