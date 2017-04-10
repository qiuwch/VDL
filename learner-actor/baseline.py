import sys, time
import gym
import dummy_env

task = sys.argv[1]

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
print (t1-t0)
#clientSocket.send('over')
#clientSocket.close()
