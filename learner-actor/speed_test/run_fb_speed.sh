server=10.1.1.1
remote_script=${HOME}/workspace/VDL/VDL/learner-actor/speed_test/speed_test.py
python speed_test.py --server &
sleep 1
ssh n001 -f "source ~/.bash_profile; python ${remote_script} --client ${server}"
