# Report the fps of each openai gym environments
# TODO: Check whether my way of checking fps is valid?
import gym
import time, argparse, sys, json

group_gym = []
group_dummy = []

def load_gym():
    global group_gym
    group_gym += ['CartPole-v0', 'Breakout-v0', 'Hopper-v1', 'Humanoid-v1']
    try:
        import ppaquette_gym_doom
        group_gym.append('ppaquette/DoomDeathmatch-v0')
    except:
        pass

def load_dummy():
    # Dummy environments are used to simulate envs with different computation speeds and observation size
    global group_dummy
    sys.path.append('../learner-actor')
    import dummy_env
    fps =  [500, 600, 6000, 60000]
    group_dummy = ['dummy/OBS1000-FPS%d-v0' % v for v in fps]
    for env in group_dummy:
        dummy_env.create(env)

class FPSCounter():
    '''
    A simple FPSCounter for low frame rate, if the frame rate is extremlely high
    Then the overhead in this counter will be an issue.
    '''
    def __init__(self):
        self.reset()

    def reset(self):
        self.num_frames = 0
        self.total_time = 0
        self.total_frames = 0
        self.last_time = 0

    def tick(self):
        self.num_frames += 1
        current_time = time.time()

        if self.last_time == 0: # Initially
            self.last_time = current_time

        if current_time - self.last_time > 1:
            print 'FPS %d' % self.num_frames
            self.total_time += (current_time - self.last_time)
            self.total_frames += self.num_frames

            self.num_frames = 0
            self.last_time = current_time

    def average_fps(self):
        return float(self.total_frames) / self.total_time

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

    while(True):
        # env.render()
        action = env.action_space.sample() # Get a random action
        # action = get_an_intelligent_action()
        # action = 0

        [obs, reward, done, info] = env.step(action) # actor/environment process 2, openai gym
        if done:
            env.reset()
        # Learn based on obs and reward
        # learn(obs, reward) # learn process 1. tensorflow

        fps_counter.tick()
        if time.time() - start_time > sec_threshold:
            break

    log_data = dict(
        env_name = env_name,
        FPS = fps_counter.average_fps(),
    )
    return log_data

def main():
    # env_name = 'CarRacing-v0'

    parser = argparse.ArgumentParser()
    parser.add_argument('--env')
    parser.add_argument('--gym', action='store_true')
    parser.add_argument('--dummy', action='store_true')
    args = parser.parse_args()

    if args.env:
        run_env(args.env)
        return

    envs = []
    if not any([args.gym, args.dummy]):
        args.gym = True
        args.dummy = True

    if args.gym:
        load_gym()
        envs += group_gym

    if args.dummy:
        load_dummy()
        envs += group_dummy

    for env_name in envs:
        log_data = run_env(env_name)
        with open('log/%s-fps.json' % env_name, 'w') as f:
            json.dump(log_data, f)


if __name__ == '__main__':
    main()
