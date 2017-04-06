# Report the fps of each openai gym environments
# TODO: Check whether my way of checking fps is valid?
import gym
import time, argparse
env_names = ['CartPole-v0', 'Breakout-v0', 'Hopper-v1', 'Humanoid-v1']
try:
    import ppaquette_gym_doom
    env_names.append('ppaquette/DoomDeathmatch-v0')
except:
    pass

class FPSCounter():
    '''
    A simple FPSCounter for low frame rate, if the frame rate is extremlely high
    Then the overhead in this counter will be an issue.
    '''
    def __init__(self):
        self.reset()

    def reset(self):
        self.num_frames = 0
        self.last_time = 0

    def tick(self):
        self.num_frames += 1
        current_time = time.time()

        if self.last_time == 0:
            self.last_time = current_time

        if current_time - self.last_time > 1:
            print 'FPS %d' % self.num_frames
            self.num_frames = 0
            self.last_time = current_time

def test_FPSCounter():
    '''
    pytest -s gym-fps.py to run this test
    '''
    fps_counter = FPSCounter()
    sec_threshold = 5

    for sleep_time in [0.0001, 0.001, 0.01, 0.1]:
        fps_counter.reset()
        expected_fps = int(1/sleep_time)
        start = time.time()

        print 'Expected FPS = %d, run for %d seconds' % (expected_fps, sec_threshold)
        while(1):
            time.sleep(sleep_time) # means 1 second
            fps_counter.tick()
            if time.time() - start > sec_threshold:
                break

def get_an_intelligent_action():
    # do something
    pass

def run_env(env_name):
    # Need to disable the fps constraint so that I can get an accurate number
    fps_counter = FPSCounter()
    env = gym.make(env_name)
    env.reset()
    sec_threshold = 5
    start_time = time.time()
    while(1):
        # env.render()
        action = env.action_space.sample() # Get a random action
        # action = get_an_intelligent_action()
        [obs, reward, done, info] = env.step(action) # actor/environment process 2, openai gym
        if done:
            env.reset()
        # Learn based on obs and reward
        # learn(obs, reward) # learn process 1. tensorflow

        fps_counter.tick()
        if time.time() - start_time > sec_threshold:
            break

if __name__ == '__main__':
    # env_name = 'CartPole-v0'
    # env_name = 'Breakout-v0'
    # env_name = 'Hopper-v1'
    # env_name = 'Humanoid-v1'
    # env_name = 'CarRacing-v0'
    # run_env(env_name)

    parser = argparse.ArgumentParser()
    parser.add_argument('--env')
    args = parser.parse_args()

    if not args.env:
        for env_name in env_names:
            run_env(env_name)
    else:
        run_env(args.env)
