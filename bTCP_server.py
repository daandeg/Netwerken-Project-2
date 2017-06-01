#!/usr/local/bin/python3
import socket, argparse
from struct import *

#Handle arguments
import binascii

from Packet import *

parser = argparse.ArgumentParser()
parser.add_argument("-w", "--window", help="Define bTCP window size", type=int, default=100)
parser.add_argument("-t", "--timeout", help="Define bTCP timeout in milliseconds", type=int, default=100)
parser.add_argument("-o","--output", help="Where to store file", default="tmp.file")
args = parser.parse_args()

server_ip = "127.0.0.1"
server_port = 9001

#Define a header format
header_format = "IHHBBHI"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
sock.bind((server_ip, server_port))

def handshake():
    #Step 1
    data, addr = sock.recvfrom(1016)
    packet = fromRecv(data)

    if(packet is not None and packet.flags == 4):
        print("Step 1 server completed")
        #Step 2
        packet2 = Packet(packet.streamID, packet.SYNNumber, packet.SYNNumber+1, True, True, False, args.window, 0, "")
        sock.sendto(packet2.getPacket(), addr)
        print("Step 2 server completed")

        #Step 3
        data, addr = sock.recvfrom(1016)
        packet = fromRecv(data)
        if(packet is not None and packet2.streamID == packet2.streamID and packet.SYNNumber == packet2.ACKNumber and packet.ACKNumber == packet2.ACKNumber, packet.flags == 2):
            print("Handshake completed!")
            return True
        else:
            print("Step 3 failed")
            return True
    else:
        print("Step 1 failed")
        return False

handshake()
