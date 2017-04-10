server="localhost"
python speed_test.py --server &
sleep 1
python speed_test.py --client ${server} &
