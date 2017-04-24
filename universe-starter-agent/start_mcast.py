'''
Signaling program to start multicast process for all MNIST peers

Author: Yuan Jing Vincent Yan (vyan1@jhu.edu)
'''
import socket_util
import params

if __name__ == '__main__':
    sock, mcast_destination = socket_util.set_up_start_mcast()

    sock.sendto(params.START_MCAST_SIGNAL, mcast_destination)
    print ( "start_mcast: Let the show begin!" )
