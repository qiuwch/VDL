'''
Signaling program to start multicast process for all MNIST peers

Author: Yuan Jing Vincent Yan (vyan1@jhu.edu)
'''
import spread
import params

if __name__ == '__main__':
    try:
        mbox = spread.Mailbox(params.SPREAD_DAEMON_PORT, "start_spread", False, 0) 
    except spread.Error as error:
        error._print()
        raise error
    
    send_msg = spread.Message()
    service = spread.Message.Reliable | spread.Message.SelfDiscard
    send_msg.set_service(service)

    mbox.add_group(params.SPREAD_GROUP_NAME)
    send_msg.write(params.START_SPREAD_SIGNAL)
    mbox.send(send_msg)
    print ( "start_mcast: Let the show begin!" )
