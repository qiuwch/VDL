Compare the speed between virtual environments, from very simple to very complex.

The list includes:

- [CartPole-v0](https://gym.openai.com/envs#classic_control)
- [Breakout-v0](https://gym.openai.com/envs#atari)
- [Hopper-v1](https://gym.openai.com/envs#mujoco)
- [Humanoid-v1](https://gym.openai.com/envs#mujoco)
- [DoomDeathmatch-v0](https://gym.openai.com/envs#doom)


`python obs-stat.py > obs-stat.log 2>&1`   
`python gym-fps.py > fps.log 2>&1`


`export LD_LIBRARY_PATH=/lib64:/usr/lib64:$LD_LIBRARY_PATH`, use this for libGL.so.1 not found error for mujoco.
