import sys
import spread_util
import os

num_peers = int(sys.argv[1])
my_peer_ID = int(sys.argv[2]) - 1

data = "kraken"
data2 = str(bytearray(os.urandom(1600)))

mbox, send_MSG, rcv_MSG, group_list = spread_util.set_up_spread_peer()

spread_util.await_start_spread(mbox, rcv_MSG, group_list)

spread_util.send(mbox, send_MSG, data + str(my_peer_ID))
print (data2 + str(my_peer_ID)).encode('hex') 
spread_util.send(mbox, send_MSG, data2 + str(my_peer_ID))


for _ in xrange( (num_peers - 1) * 2):
    rcv_message = spread_util.recv(mbox, rcv_MSG, group_list, True)
    print rcv_message.encode('hex')

print 'Should timeout...'
rcv_message = spread_util.recv(mbox, rcv_MSG, group_list, True)