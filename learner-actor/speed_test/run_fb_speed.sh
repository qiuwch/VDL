server=10.161.48.42
remote_script=${PWD}/speed_test.py
#python speed_test.py --client --server_ip ${server} & 
#python speed_test.py --client --server_ip ${server} &
#python speed_test.py --server --num_client 2 --recv_size 100000&
python speed_test.py --server --num_client 1 &
sleep 1
#ssh n001 -f "source ~/.bash_profile; python ${remote_script} --client --server_ip ${server} --packet_size 100000 --packet_count 50 --sleep 0.2"
#ssh n003 -f "source ~/.bash_profile; python ${remote_script} --client --server_ip ${server} --packet_size 100000 --packet_count 50 --sleep 0.2"
#ssh n004 -f "source ~/.bash_profile; python ${remote_script} --client --server_ip ${server} --port 10010"
#ssh n004 -f "source ~/.bash_profile; python ${remote_script} --client --server_ip ${server} --packet_size 100 --packet_count 300 --sleep 0.0001"
#ssh n005 -f "source ~/.bash_profile; python ${remote_script} --client --server_ip ${server} --packet_size 100 --packet_count 200 --sleep 0.0001"
#ssh n007 -f "source ~/.bash_profile; python ${remote_script} --client --server_ip ${server} --packet_size 100 --packet_count 200 --sleep 0.0001"
#
