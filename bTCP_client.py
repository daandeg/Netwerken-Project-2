#!/usr/local/bin/python3
import random
import socket, argparse, uuid
from struct import *

#Handle arguments
import binascii

from Packet import *

parser = argparse.ArgumentParser()
parser.add_argument("-w", "--window", help="Define bTCP window size", type=int, default=100)
parser.add_argument("-t", "--timeout", help="Define bTCP timeout in milliseconds", type=int, default=100)
parser.add_argument("-i", "--input", help="File to send", default="tmp.file")
args = parser.parse_args()

destination_ip = "127.0.0.1"
destination_port = 9001

#bTCP header
header_format = "IHHBBHI"

synNumber = 0

bTCP_payload = "Hello World!"

#UDP socket which will transport your bTCP packets
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#send payload
#sock.sendto(createPacket(), (destination_ip, destination_port))


def handshake():
    #Step 1
    ID = random.getrandbits(32)
    print(ID)
    packet = Packet(ID, 0, 0, True, False, False, args.window, 0, "")
    sock.sendto(packet.getPacket(), (destination_ip, destination_port))
    print("Step 1 client completed")
    #Step 2
    packet2 = fromRecv(sock.recv(1016))
    if(packet2 is not None and packet.streamID == packet2.streamID and packet.SYNNumber == packet2.SYNNumber and packet.ACKNumber + 1 == packet2.ACKNumber and packet2.flags == 6):
        print("Step 2 client completed")
        #Step 3
        packet = Packet(packet2.streamID, packet2.ACKNumber, packet2.ACKNumber, False, True, False, args.window, 0, "")
        sock.sendto(packet.getPacket(), (destination_ip, destination_port))
        print("Step 3 client completed")
        return True
    else:
        print("Step 2 failed")
        return False

handshake()