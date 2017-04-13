import gym
import universe  # register the universe environments
import random, argparse, time

# env = gym.make('flashgames.DuskDrive-v0')
env = gym.make('flashgames.NeonRace-v0')
env.configure(remotes=1)  # automatically creates a local docker container
observation_n = env.reset()

action_pool = [
    [[('KeyEvent', 'ArrowUp', True)]],
    [[('KeyEvent', 'ArrowDown', True)]],
    [[('KeyEvent', 'ArrowLeft', True)]],
    [[('KeyEvent', 'ArrowRight', True)]],
]
release_pool = [
    [[('KeyEvent', 'ArrowUp', False)]],
    [[('KeyEvent', 'ArrowDown', False)]],
    [[('KeyEvent', 'ArrowLeft', False)]],
    [[('KeyEvent', 'ArrowRight', False)]],
]

# action_n = [[('KeyEvent', 'ArrowUp', True)] for ob in observation_n]  # your agent here
def forward_action():
    return action_pool[0]

last_choice = 0
last_choice_time = 0
time_interval = 1
def random_action():
    global last_choice_time
    global last_choice
    elapse = time.time() - last_choice_time
    if elapse > time_interval:
        # Make a new decision
        choice = random.randrange(len(action_pool))
        last_choice_time = time.time()
        release_action = release_pool[last_choice]
        last_choice = choice
        return release_action
        # Release the previous key
    else:
        choice = last_choice

    action = action_pool[choice]
    print action
    return action

def run_env(action_function):
    while True:
      # action_n = [[('KeyEvent', 'ArrowUp', True)] for ob in observation_n]  # your agent here
      action_n = action_function()
      observation_n, reward_n, done_n, info = env.step(action_n)
      env.render()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--random', action='store_true')
    parser.add_argument('--forward', action='store_true')
    args = parser.parse_args()

    if args.random:
        run_env(random_action)

    elif args.forward:
        run_env(forward_action)

    else:
        run_env(forward_action) # By default
