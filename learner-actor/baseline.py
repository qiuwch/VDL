import sys, time, argparse, os
import gym
import dummy_env, util
import json
try:
    import ppaquette_gym_doom
except:
    pass

parser = argparse.ArgumentParser()
parser.add_argument('--task')
parser.add_argument('--log')

args = parser.parse_args()

task = args.task
if task and task.startswith('dummy'):
    dummy_env.create(task)

t0 = time.time()

env = gym.make(task)
for i_episode in range(200):
    observation = env.reset()
    #print observation
    #send_us(observation, 0)
    for t in range(100):
        #env.render()
        action = env.action_space.sample()
        #action = int(clientSocket.recv(1))
        observation, reward, done, info = env.step(action)
        #print 'ob:' + str(observation)
        #print 're:' + str(reward)
        #send_us(observation, reward)
        if done:
            #print("Episode finished after {} timesteps".format(t+1))
            break

t1 = time.time()
total_time = t1 - t0

if args.log:
    util.mkdirp(os.path.dirname(args.log))
    with open(args.log, 'w') as f:
        log_data = dict(
            num_actors = 1,
            total_time = total_time,
            task = args.task,
            mode = 'single-machine',
        )
        json.dump(log_data, f)
#clientSocket.send('over')
#clientSocket.close()
