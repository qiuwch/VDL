# Star the learner
learner_bin=learner.py
actor_bin=${PWD}/actor.py
port=10000

run_task_fb () # Space is needed
{
  server='10.1.1.1'
  python learner.py --port 10000 --task ${task} &
  ssh n001 -f "source ~/.bash_profile; python ${actor_bin} ${server} ${port} ${task}"
  ssh n003 -f "source ~/.bash_profile; python ${actor_bin} ${server} ${port} ${task}"
}

run_task_local ()
{
  server='127.0.0.1'
  echo "Start learner"
  python ${learner_bin} --port ${port} ${learner_args} &
  sleep 1 # Wait for the server to boot
  echo "Start actor1"
  python ${actor_bin} --server_ip ${server} --port ${port} ${actor_args} &
  echo "Start actor2"
  python ${actor_bin} --server_ip ${server} --port ${port} ${actor_args} &
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

for task in CartPole-v0 Breakout-v0 Hopper-v1 Humanoid-v1
# for task in ppaquette/DoomDeathmatch-v0
do
  # With compression
  learner_args="--task ${task} --log log/${task}-nocompress-local.json"
  actor_args="--task ${task}"
  run_baseline
  run_task_local
done
