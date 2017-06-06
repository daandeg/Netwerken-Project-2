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


def handshake(ID):
    #Step 1
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

def termination_client(ID, SYN, ACK):
    #Step 1
    packet = Packet(ID, SYN, ACK, False, False, True, args.window, 0, "")
    sock.sendto(packet.getPacket(), (destination_ip, destination_port))
    #Step 2
    packet2 = fromRecv(sock.recv(1016))
    if(packet2 is not None and packet.streamID == packet2.streamID and packet2.flags == 3):
        packet = Packet(packet2.streamID, packet2.SYNNumber, packet2.ACKNumber, False, True, False, args.window, 0, "")
        sock.sendto(packet.getPacket(), (destination_ip, destination_port))
        sock.close()
        return True
    else:
        return False

def termination():
    # Step 1
    packet = fromRecv(sock.recv(1016))
    if (packet is not None and packet.flags == 1):
        # Step 2
        packet2 = Packet(packet.streamID, packet.SYNNumber, packet.ACKNumber, False, True, True, args.window, 0, "")
        sock.sendto(packet2.getPacket(), (destination_ip, destination_port))

        # Step 3
        packet = fromRecv(sock.recv(1016))
        if (packet is not None and packet2.streamID == packet.streamID and packet2.SYNNumber == packet.SYNNumber and packet2.ACKNumber == packet.ACKNumber and packet.flags == 2):
            sock.close()
            print("Termination completed")
            return True
        else:
            return False
    else:
        return False

handshake(random.getrandbits(32))
#termination_client(random.getrandbits(32), 0, 0)
termination()