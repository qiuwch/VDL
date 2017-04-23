import sys
import spread
import params
import socket_util
import socket

num_peers = int(sys.argv[1])
my_peer_ID = int(sys.argv[2]) - 1

group_name = "jhuVDL"
group_list = spread.GroupList()
group_list.add(group_name)

data = "Kraken";
data2 = "Magmus";

try:
  mbox = spread.Mailbox("4803", "vyan1_mbox", False, 0) 
except spread.Error as error:
  error._print()
  raise error

send_msg = spread.Message()
rcv_msg = spread.Message()
service = spread.Message.Reliable | spread.Message.SelfDiscard
send_msg.set_service(service)


mbox.clear_groups()
mbox.clear_message_parts()
mbox.join(group_name)

sock = socket_util.set_up_UDP_mcast_peer()[0]
socket_util.await_start_mcast(sock)

mbox.add_group(group_name)
send_msg.write(data + str(my_peer_ID))
mbox.send(send_msg)
send_msg.clear()
send_msg.write(data2 + str(my_peer_ID))
mbox.send(send_msg)


for _ in xrange( (num_peers - 1) * 2):
    rcv_msg.clear()
    #while mbox.poll() == 0:
    #    pass
    bytes = mbox.receive(rcv_msg, group_list)
    print rcv_msg.read(bytes)
