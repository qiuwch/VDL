'''
Spread utility class for MNIST Tensorflow distributed learning via peer-to-peer multicast

Author: Yuan Jing Vincent Yan (vyan1@jhu.edu)
'''
import spread
import params
import sys
import signal
import time
import threading

timeout_flag = 0
sender_dict = {}  # sender Spread group name  ->  [data_remaining, recovering_data]
                  # #vyan1_mbox#ccvl1         ->  [4, "Hello W"]

def timeout_handler():
    global timeout_flag
    timeout_flag = 1
    
class SpreadListenThread(threading.Thread):
    """
    Thread class that listens for Spread message receiving. It terminates when stop() is called.
    """

    def __init__(self, mbox, rcv_MSG, group_list, num_peers, inc_msg_q, ret_val):
        super(SpreadListenThread, self).__init__()
        self.mbox = mbox
        self.rcv_MSG = rcv_MSG
        self.group_list = group_list
        self.num_peers = num_peers
        self.inc_msg_q = inc_msg_q
        self.ret_val = ret_val
        self.rcv_msg_num = 0
        self._stop = threading.Event()
        self.daemon = True # Make the daemon = True, so that I can kill this program with ctrl-c

    def run(self):
        while not self.stopped():
            if params.VERBOSE_LVL >= 3:
                print "Entering recv cycle..."
            self.rcv_msg_num = recv_chunks(self.mbox, self.rcv_MSG, self.group_list, self.inc_msg_q, self.num_peers, self.rcv_msg_num, True)
        if params.VERBOSE_LVL >= 1:
            print "SpreadListenThread terminating..."
        self.ret_val.put(self.rcv_msg_num)
    
    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

        
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
    
    # Register the signal timeout handler
    signal.signal(signal.SIGALRM, timeout_handler)

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
    service = spread.Message.FIFO | spread.Message.SelfDiscard
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
    start_spread_msg = recv(mbox, rcv_MSG, group_list, False)[0]
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
    if params.VERBOSE_LVL >= 4:
        print 'out: ', len(msg_str), msg_str.encode("hex")
    mbox.send(send_MSG)

def send_chunks(mbox, send_MSG, msg_str):
    '''
    Send a multicast message, fragmented as chunks, via Spread
    @param mbox      Spread mailbox
    @param send_MSG  Spread message object for sending
    @param msg_str   The message to send, as a string
    '''
    
    # Send PACKET_SIZE_TAG "Arnold" followed by data length
    if params.VERBOSE_LVL >= 4:
        print '[PACKET_SIZE_TAG]'
    send(mbox, send_MSG, params.PACKET_SIZE_TAG + str(len(msg_str)) )
    
    for i in xrange(0, len(msg_str), params.SPREAD_MAX_MESSAGE_SIZE):
        msg_chuck = msg_str[i : i + params.SPREAD_MAX_MESSAGE_SIZE]
        if params.VERBOSE_LVL >= 4:
            print '[Chunk]'
        send(mbox, send_MSG, msg_chuck)
        
    
def recv(mbox, rcv_MSG, group_list, timeout_enabled):
    '''
    Receive a multicast message via Spread
    @param mbox             Spread mailbox
    @param rcv_MSG          Spread message object for receiving
    @param group_list       Group list of the mailbox
    @param timeout_enabled  Is timeout enabled?
    @return The message received and the sender, or (None, None) if timed out
    '''  
    global timeout_flag
    
    timeout_flag = 0
    timer = threading.Timer(params.SOCK_TIMEOUT_VAL, timeout_handler)
    rcv_MSG.clear()
    
    if timeout_enabled:
         timer.start()
    while mbox.poll() == 0:
        time.sleep(params.SPREAD_MBOX_POLL_INTERVAL)
        if timeout_flag == 1:
            if params.VERBOSE_LVL >= 3:
                print "Signal timeout!"
            return (None, None)
    timer.cancel()

    # Number of bytes received
    num_bytes = mbox.receive(rcv_MSG, group_list)
    inc_msg = reconstruct_received_message(rcv_MSG, num_bytes)
    sender = rcv_MSG.sender()
    return inc_msg, sender

def recv_chunks(mbox, rcv_MSG, group_list, queue, num_peers, rcv_msg_num, timeout_enabled):
    '''
    Receive multicast messages from multiple peers, fragmented as chunks, via Spread
    @param mbox             Spread mailbox
    @param rcv_MSG          Spread message object for receiving
    @param group_list       Group list of the mailbox
    @param queue            The queue to store the received messages
    @param num_peers        Number of mulitcast peers
    @param rcv_msg_num      Total number of messages received from other peers before this call
    @param timeout_enabled  Is timeout enabled?
    @return Total number of messages received from other peers after this call
    '''  
    global sender_dict
   
    queue_cnt = 0
    while queue_cnt < num_peers - 1:  # until received messages from all other peers
        msg, sender = recv(mbox, rcv_MSG, group_list, timeout_enabled)
        # If message recv timed out
        if msg == None:
            if params.VERBOSE_LVL >= 2:
                print('Spread util recv_chunks timed out')
            return rcv_msg_num          
        rcv_msg_num += 1
        
        if sender not in sender_dict  or  sender_dict[sender][0] == 0:
            # if no "Arnold":
            if msg[0 : params.LEN_PACKET_SIZE_TAG] != params.PACKET_SIZE_TAG:
                if params.VERBOSE_LVL >= 2:
                    print('Warning: received fragment without head fragment')
                continue
            else:
                data_len = int(msg[params.LEN_PACKET_SIZE_TAG :])
                sender_dict[sender] = [data_len, '']
                if params.VERBOSE_LVL >= 2:
                    print('received head fragment')
        else:
            # if "Arnold":
            if msg[0 : params.LEN_PACKET_SIZE_TAG] == params.PACKET_SIZE_TAG:
                data_len = int(msg[params.LEN_PACKET_SIZE_TAG :])
                sender_dict[sender] = [data_len, '']
                if params.VERBOSE_LVL >= 2:
                    print('Warning: Received head fragment without completing previous packet')
            else:
                sender_dict[sender][0] -= len(msg)
                sender_dict[sender][1] += msg
                if params.VERBOSE_LVL >= 2:
                    sys.stdout.write('.')
                if sender_dict[sender][0] == 0:
                    queue.put(sender_dict[sender][1])
                    queue_cnt += 1
                    sender_dict[sender] = [0, '']
                    if params.VERBOSE_LVL >= 2:
                        print('Full packet received; adding to queue')

    return rcv_msg_num

    
def reconstruct_received_message(rcv_MSG, num_bytes):
    '''
    Reconstruct a received message from a Spread message object for receiving. This is
    necessary because sometimes the received message contains a '\x00' character, and
    the Spread python wrapper will only read until '\x00'.
    @param rcv_MSG    Spread message object for receiving
    @param num_bytes  Number of bytes the message has
    '''
    
    if params.VERBOSE_LVL >= 3:
        print "inc_msg of len ", num_bytes
    
    inc_msg = ''
    if params.VERBOSE_LVL >= 5:
        print 'inc ', num_bytes
    bytes_read = 0
    bytes_remaining = num_bytes
    
    while bytes_remaining > 0:
        inc_msg_chuck = rcv_MSG.read(bytes_remaining)
        if params.VERBOSE_LVL >= 5:
            print inc_msg_chuck.encode("hex")
            print 'len = ', len(inc_msg_chuck)
        inc_msg += inc_msg_chuck + '00'.decode("hex")
        
        bytes_read += len(inc_msg_chuck) + 1
        bytes_remaining -= len(inc_msg_chuck) + 1
        rcv_MSG.seek(bytes_read)
        if params.VERBOSE_LVL >= 5:
            print 'bytes_read', bytes_read
            print 'bytes_remaining = ', bytes_remaining
    if params.VERBOSE_LVL >= 5:
        print "Finally ", inc_msg.encode("hex")
    
    return inc_msg[:-1]
    