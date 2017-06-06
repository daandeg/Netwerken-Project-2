#!/usr/local/bin/python3
import random
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
    failaddr = (pack("I", 0), pack("I", 0))
    #Step 1
    data, addr = sock.recvfrom(1016)
    packet = fromRecv(data)

    if(packet is not None and packet.flags == 4):
        #Step 2
        packet2 = Packet(packet.streamID, packet.SYNNumber, packet.SYNNumber+1, True, True, False, args.window, 0, "")
        sock.sendto(packet2.getPacket(), addr)

        #Step 3
        data, addr = sock.recvfrom(1016)
        packet = fromRecv(data)
        if(packet is not None and packet2.streamID == packet2.streamID and packet.SYNNumber == packet2.ACKNumber and packet.ACKNumber == packet2.ACKNumber, packet.flags == 2):
            return (packet.streamID, addr)
        else:
            return (packet.streamID, failaddr)
    else:
        return (packet.streamID, failaddr)

def termination():
    #Step 1
    data, addr = sock.recvfrom(1016)
    packet = fromRecv(data)
    if(packet is not None and packet.flags == 1):
        #Step 2
        packet2 = Packet(packet.streamID, packet.SYNNumber, packet.ACKNumber, False, True, True, args.window, 0, "")
        sock.sendto(packet2.getPacket(), addr)

        #Step 3
        data, addr = sock.recvfrom(1016)
        packet = fromRecv(data)
        if(packet is not None and packet2.streamID == packet.streamID and packet2.SYNNumber == packet.SYNNumber and packet2.ACKNumber == packet.ACKNumber and packet.flags == 2):
            sock.close()
            return True
        else:
            return False
    else:
        return False

def termination_server(ID, SYN, ACK, addr):
    #Step 1
    packet = Packet(ID, SYN, ACK, False, False, True, args.window, 0, "")
    sock.sendto(packet.getPacket(), addr)
    #Step 2
    data, addr = sock.recvfrom(1016)
    packet2 = fromRecv(data)
    if(packet2 is not None and packet.streamID == packet2.streamID and packet2.flags == 3):
        packet = Packet(packet2.streamID, packet2.SYNNumber, packet2.ACKNumber, False, True, False, args.window, 0, "")
        sock.sendto(packet.getPacket(), addr)
        sock.close()
        return True
    else:
        return False

data = handshake()
#termination()
termination_server(data[0], 0, 0, data[1])
