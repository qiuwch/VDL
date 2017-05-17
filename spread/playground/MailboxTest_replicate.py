import sys
import spread

group_name = "JHU_VDL"
group_list = spread.GroupList()
group_list.add(group_name)

try:
  mbox = spread.Mailbox("4803", "", False, 0)
except spread.Error as error:
  error._print()
  raise error
message = spread.Message()
rcv_msg = spread.Message()


data = "foobar"
service = spread.Message.Reliable | spread.Message.SelfDiscard
#message.set_service(service)

mbox.clear_groups()
mbox.clear_message_parts()
mbox.join(group_name) #

mbox.add_group(group_name)
message.write(data)
mbox.send(message)

while mbox.poll() == 0:
    pass
print 'poll ', mbox.poll()
#mbox.send(message, group_list)
bytes = mbox.receive(rcv_msg, group_list)

print bytes
print rcv_msg.read(len(data) + 1)

