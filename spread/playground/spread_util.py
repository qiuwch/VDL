'''
Spread utility class for MNIST Tensorflow distributed learning via peer-to-peer multicast

Author: Yuan Jing Vincent Yan (vyan1@jhu.edu)
'''
#TODO import
import spread
import params
#import struct
#import time
#import threading


#TODO thread to Spread
# class SockListenThread(threading.Thread):
    # """
    # Thread class that listens for socket message receiving. It terminates when stop() is called.
    # """

    # def __init__(self, sock, self_IP, inc_msg_q, num_peers, ret_val, verbose_lvl = 1):
        # super(SockListenThread, self).__init__()
        # self.sock = sock
        # self.self_IP = self_IP
        # self.inc_msg_q = inc_msg_q
        # self.num_peers = num_peers
        # self.ret_val = ret_val
        # self.rcv_MSG_num = 0
        # self.verbose_lvl = verbose_lvl
        # self._stop = threading.Event()
        # self.daemon = True # Make the daemon = True, so that I can kill this program with ctrl-c

    # def run(self):
        # while not self.stopped():
            # if self.verbose_lvl >= 3:
                # print "Entering recv cycle..."
            # self.rcv_MSG_num = socket_recv_chucked_data(self.sock, self.self_IP, self.inc_msg_q, self.num_peers, self.rcv_MSG_num, self.verbose_lvl)
        # # thread terminating
        # time.sleep(1)
        # if self.verbose_lvl >= 3:
            # print "Entering final recv cycle..."
        # self.rcv_MSG_num = socket_recv_chucked_data(self.sock, self.self_IP, self.inc_msg_q, self.num_peers, self.rcv_MSG_num, self.verbose_lvl)
        # self.ret_val.put(self.rcv_MSG_num)
    
    # def stop(self):
        # self._stop.set()

    # def stopped(self):
        # return self._stop.isSet()

        
def set_up_start_spread():
    '''
    Set up Spread utility for start_spread program
    @return (Spread mailbox, Spread message object for sending)
    '''
    
    try:
        mbox = spread.Mailbox(params.SPREAD_DAEMON_PORT, "start_spread", False, 0) 
    except spread.Error as error:
        error._print()
        raise error
    mbox.add_group(params.SPREAD_GROUP_NAME)
    
    send_MSG = spread.Message()
    service = spread.Message.Reliable | spread.Message.SelfDiscard
    send_MSG.set_service(service)
    
    return (mbox, send_MSG)

def set_up_spread_peer():
    '''
    Set up Spread utility for Spread peer
    @return Tuple of (Spread mailbox, Spread message object for sending, 
        Spread message object for receiving, group list of the mailbox)
    '''

    group_list = spread.GroupList()
    group_list.add(params.SPREAD_GROUP_NAME)  
    
    try:
      mbox = spread.Mailbox(params.SPREAD_DAEMON_PORT, "vyan1_mbox", False, 0) 
    except spread.Error as error:
      error._print()
      raise error
    mbox.join(params.SPREAD_GROUP_NAME)
    mbox.add_group(params.SPREAD_GROUP_NAME)
      
    send_MSG = spread.Message()
    rcv_MSG = spread.Message()
    service = spread.Message.Reliable | spread.Message.SelfDiscard
    send_MSG.set_service(service)
      
    return (mbox, send_MSG, rcv_MSG, group_list)

def await_start_spread(mbox, rcv_MSG, group_list):
    '''
    Blocks and waits for start_spread signal
    @param mbox        Spread mailbox
    @param rcv_MSG     Spread message object for receiving
    @param group_list  Group list of the mailbox
    '''
    
    print('Waiting for start_spread signal...')
    start_spread_msg = recv(mbox, rcv_MSG, group_list)
    assert (start_spread_msg == params.START_SPREAD_SIGNAL)
    print('Signal received.')
    

def send(mbox, send_MSG, msg_str):
    '''
    Send a multicast message via Spread
    @param mbox      Spread mailbox
    @param send_MSG  Spread message object for sending
    @param msg_str   The message to send, as a string
    '''
    
    send_MSG.clear()
    send_MSG.write(msg_str)
    mbox.send(send_MSG)

def recv(mbox, rcv_MSG, group_list):
    '''
    Receive a multicast message via Spread
    @param mbox        Spread mailbox
    @param rcv_MSG     Spread message object for receiving
    @param group_list  Group list of the mailbox
    @return The message received
    '''
    
    rcv_MSG.clear()
    num_byte = mbox.receive(rcv_MSG, group_list)
    return rcv_MSG.read(num_byte)
