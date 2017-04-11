# Star the learner
learner_bin=learner.py
actor_bin=${PWD}/actor.py
port=10000
setup_remote="source ${HOME}/.bash_profile"
${setup_remote}

run_task_fb () # Space is needed
{
  server='10.1.1.1'
  echo "Start learner"
  python ${learner_bin} --port ${port} ${learner_args} &
  actor_cmd="python ${actor_bin} ${actor_args} --server_ip ${server} --port ${port}"
  echo "Start actor1"
  ssh n001 -f "${setup_remote}; ${actor_cmd}"
  echo "Start actor2"
  ssh n003 -f "${setup_remote}; ${actor_cmd}"
  wait $(jobs -p)
}

run_task_local ()
{
  server='127.0.0.1'
  echo "Start learner"
  python ${learner_bin} --port ${port} ${learner_args} &
  sleep 1 # Wait for the server to boot
  actor_cmd="python ${actor_bin} --server_ip ${server} --port ${port} ${actor_args} &"
  echo "Start actor1"
  ${actor_cmd}
  echo "Start actor2"
  ${actor_cmd}
  wait $(jobs -p)
}

run_baseline ()
{
  python baseline.py --task ${task} --log log/${task}-base.json
}

# for task in CartPole-v0 Breakout-v0 Hopper-v1 Humanoid-v1
# # for task in ppaquette/DoomDeathmatch-v0
# do
#   # With compression
#   learner_args="--task ${task} --log log/${task}-compress-local.json"
#   actor_args="--task ${task} --compress"
#   run_baseline
#   run_task_local
# done

# for task in CartPole-v0 Breakout-v0 Hopper-v1 Humanoid-v1
for task in Hopper-v1 Humanoid-v1
# for task in ppaquette/DoomDeathmatch-v0
do
  # 1. baseline
  # run_baseline

  # 2. no compress in fb
  learner_args="--task ${task} --log log/${task}-nocompress-fb.json"
  actor_args="--task ${task}"
  run_task_fb

  # 3. compress in fb
  learner_args="--task ${task} --log log/${task}-compress-fb.json"
  actor_args="--task ${task} --compress"
  run_task_fb
done
