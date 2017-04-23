import sys
import spread
import params

num_peers = int(sys.argv[1])
my_peer_ID = int(sys.argv[2]) - 1

group_name = params.SPREAD_GROUP_NAME
group_list = spread.GroupList()
group_list.add(group_name)

data = "Kraken";
data2 = "Magmus";

try:
  mbox = spread.Mailbox(params.SPREAD_DAEMON_PORT, "vyan1_mbox", False, 0) 
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

print('Waiting for start_mcast signal...')
num_byte = mbox.receive(rcv_msg, group_list)
assert (rcv_msg.read(num_byte) == params.START_MCAST_SIGNAL)
print('Signal received.')

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
    num_byte = mbox.receive(rcv_msg, group_list)
    print rcv_msg.read(num_byte)
