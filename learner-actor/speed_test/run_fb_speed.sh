server=10.1.1.1
python speed_test.py --server &
sleep 1
ssh n001 -f "source ~/.bash_profile; python speed_test.py --client ${server}"
