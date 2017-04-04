'''
Socket utility class for MNIST Tensorflow distributed learning via peer-to-peer multicast

Author: Yuan Jing Vincent Yan (vyan1@jhu.edu)
'''
import sys
import socket
import struct
import params

def set_up_start_mcast():
    '''
    Set up the network for start_mcast program
    '''
    
    # UDP setup
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind( ('', params.START_MCAST_PORT_NUM) )
    
    mcast_destination = (params.MCAST_ADDR, params.PEER_PORT_NUM)
    
    return (sock, mcast_destination)

def set_up_UDP_mcast_peer():
    '''
    Set up the network for UDP multicast peer
    @return Tuple of (the socket, the IP address of self, destination multicast address)
    '''

    # UDP setup
    self_IP = socket.gethostbyname(socket.gethostname())
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind( ('', params.PEER_PORT_NUM) )

    # mulitcast setup
    mcast_destination = (params.MCAST_ADDR, params.PEER_PORT_NUM)
    mcast_group = socket.inet_aton(params.MCAST_ADDR)
    mreq = struct.pack('4sL', mcast_group, socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    
    return (sock, self_IP, mcast_destination)


def close_UDP_mcast_peer(sock):
    '''
    Close the UDP multicast peer
    @params sock The socket to close
    '''
    sock.close()


def await_start_mcast(sock):
    '''
    Blocks and waits for start_mcast signal
    @params sock The socket to use
    '''
    
    print('Waiting for start_mcast signal...')
    signal = sock.recvfrom(params.LEN_START_MCAST_SIGNAL)[0]
    assert (signal == params.START_MCAST_SIGNAL)
    print('Signal received.')
    

def socket_send_data_chucks(sock, data, mcast_destination):
    '''
    Send a data string, fragmented as chucks, to a multicast address
    @params sock The socket to use
    @params data The data string
    @params mcast_destination Destination multicast address
    '''
    
    # Send tag "Arnold" followed by data length
    sock.sendto(params.IMAGE_SIZE_PACKET_TAG + str(len(data)), mcast_destination)
    
    for i in xrange(0, sys.getsizeof(data), params.MAX_PACKET_SIZE):
        data_chuck = data[i : i + params.MAX_PACKET_SIZE]
        sock.sendto(data_chuck, mcast_destination)


def socket_recv_chucked_data(sock, data_len, self_IP):
    '''
    Let the socket receive chucked data with a given total length. Retry receiving if packets
    are incomplete, but return null if timeout. Ignore packets sent by self
    @params sock The socket to use
    @param data_len The total length
    @param self_IP The IP address of self
    @return The original unchucked data string, or null if timeout
    '''

    sock.settimeout(None)
    data_remaining = data_len
    orig_data = ""
    while data_remaining > 0:
        try:
            recv_data_len = min(data_remaining, params.MAX_PACKET_SIZE)
            sock.settimeout(0.3)
            chuck, addr = sock.recvfrom(recv_data_len)
            #print ('L1', chuck[0:3], addr)
            while addr[0] == self_IP:
                chuck, addr = sock.recvfrom(recv_data_len)
                #print ('L2', chuck[0:3], addr)
            if chuck[0 : params.LEN_IMAGE_SIZE_PACKET_TAG] == params.IMAGE_SIZE_PACKET_TAG:
                return socket_recv_chucked_data(int(chuck[params.LEN_IMAGE_SIZE_PACKET_TAG :]))
            orig_data += chuck
            data_remaining -= recv_data_len
            sock.settimeout(None)
        except socket.timeout:
            print('socket_recv_chucked_data timed out')
            return None

    return orig_data
