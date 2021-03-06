#!/usr/local/bin/python3
import socket

from File import File
from Packet import *

""""
Implementation of a basic TCP server
"""
class bTCPServer:
    """"
    Initialization
    """
    def __init__(self, window, timeout, path, server):
        self.window = window
        self.timeout = timeout
        self.path = path
        self.server = server
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(self.timeout)
        self.connected = False
        self.terminate = False
        self.file = None

    """"
    Performing the 3-way handshake with the client
    """
    def handshake(self):
        #Step 1
        data, addr = self.sock.recvfrom(1016)
        packet = fromRecv(data)
        if packet is not None and packet.flags == 4:
            #Step 2
            streamID = packet.streamID
            synNumber = packet.SYNNumber
            ackNumber = packet.SYNNumber + 1
            client = addr
            self.window = min(self.window, packet.window)
            packet2 = Packet(streamID, synNumber, ackNumber, True, True, False, self.window, packet.dataLength, packet.payload)
            self.sock.sendto(packet2.getPacket(), client)

            #Step 3
            data, addr = self.sock.recvfrom(1016)
            packet = fromRecv(data)
            if packet is not None and streamID == packet.streamID and packet2.ACKNumber == packet.SYNNumber and packet.flags == 2 and addr == client:
                synNumber = packet.SYNNumber
                ackNumer = packet.ACKNumber
                print("handshake complete!")
                return True, streamID, synNumber, ackNumer, client
            else:
                print("failed step 3")
                return False, streamID, synNumber, ackNumber, client
        else:
            print("failed step 2")
            return False, 0, 0, 0, None

    """"
    React to termination from the client
    """
    def termination_re(self, streamID, synNumber, ackNumber, client):
        #Step 2:
        payload = ""
        packet = Packet(streamID, synNumber, ackNumber, False, True, True, self.window, len(payload), payload)
        self.sock.sendto(packet.getPacket(), client)

        #Step 3:
        data, addr = self.sock.recvfrom(1016)
        packet2 = fromRecv(data)
        if packet2 is not None and packet.SYNNumber == packet2.SYNNumber and packet.ACKNumber == packet2.ACKNumber and packet2.flags == 2 and addr == client:
            return False
        else:
            return True

    """"
    Initiate termination to the client
    """
    def termination_in(self, streamID, synNumber, ackNumber, client):
        #Step 1:
        payload = ""
        packet = Packet(streamID, synNumber, ackNumber, False, False, True, self.window, len(payload), payload)
        self.sock.sendto(packet.getPacket(), client)

        #Step 3:
        data, addr = self.sock.recvfrom(1016)
        packet2 = fromRecv(data)
        if packet2 is not None and packet2.streamID == streamID and packet2.SYNNumber == synNumber and packet2.ACKNumber == ackNumber and packet2.flags == 3 and addr == client:
            packet = Packet(streamID, synNumber, ackNumber, False, True, False, self.window, len(payload), payload)
            self.sock.sendto(packet.getPacket(), client)
            return False
        else:
            return True

    """"
    Receive message from the client. This is done by first performing the handshake,
    then receiving the message and finally terminating by either initiate it serverside
    or clientside
    """
    def receive(self):
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(self.server)
        synNumber = 0
        ackNumber = 0
        packets = []

        # Perform handshake until connected
        while not self.connected:
            try:
                self.connected, streamID, synNumber, ackNumber, client = self.handshake()
            except socket.timeout:
                pass

        # Receive packets
        while self.connected and not self.terminate:
            try:
                data, addr = self.sock.recvfrom(1016)
                packet = fromRecv(data)
                if packet is not None and addr == client and packet.streamID == streamID:
                    ackNumber = packet.SYNNumber
                    # If a FIN packet is received: react to termination
                    if packet.flags == 1:
                        while self.connected:
                            self.writePackets(list(set(packets)))
                            try:
                                self.connected = self.termination_re(streamID, synNumber, ackNumber, client)
                                return
                            except socket.timeout:
                                pass
                    # Else if ACK packet is received, acknowledge
                    elif packet.flags == 4:
                        packets.append((packet.SYNNumber, packet.payload))
                        synNumber = packet.SYNNumber
                        ackNumber = packet.SYNNumber
                        packet2 = Packet(streamID, synNumber, ackNumber, False, True, False, self.window, len(""), "")
                        self.sock.sendto(packet2.getPacket(), client)
            except socket.timeout:
                pass

        synNumber += 1
        ackNumber = synNumber
        # Initiate termination if asked for
        while self.connected and self.terminate:
            try:
                self.connected = self.termination_in(streamID, synNumber, ackNumber, client)
                self.writePackets(list(set(packets)))
            except socket.timeout:
                pass
        self.sock.close()

    """"
    Writing the received packets to the output file
    """
    def writePackets(self, packets):
        packets = sorted(packets, key = lambda tup: tup[0]) # Sort by synNumber
        packets = [i[1] for i in packets]
        self.file = File(self.path)
        self.file.fromPackets(packets)
        self.file.writeFile()

    """"
    Let the server initiate termination
    """
    def orderTermination(self):
        self.terminate = True