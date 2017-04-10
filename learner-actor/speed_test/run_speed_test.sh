server="localhost"
num_client=2
python speed_test.py --server --num_client ${num_client} &
sleep 1
python speed_test.py --client --server_ip ${server} &
python speed_test.py --client --server_ip ${server} &
