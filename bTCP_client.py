#!/usr/local/bin/python3
import random
import socket

from File import *
from Packet import *

"""
Implementation of a basic TCP client
"""
class bTCPClient:
    """"
    Initialization
    """
    def __init__(self, window, timeout, path, server, client):
        self.window = window
        self.timeout = timeout
        self.path = path
        self.server = server
        self.client = client
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.connected = False
        self.streamID = 0   # initialized later
        self.synNumber = 0
        self.ackNumber = 0
        self.file = None

    """"
    Connecting the client to the server by performing a 3-way handshake
    """
    def connect(self):
        self.sock.bind(self.client)
        self.sock.settimeout(self.timeout)
        self.connected = False
        self.streamID = random.getrandbits(32)
        while not self.connected:
            try:
                self.connected = self.handshake()
            except socket.timeout:
                pass

    """"
    Disconnecting the client from the server by performing a 4-way termination
    """
    def disconnect(self):
        while self.connected:
            try:
                self.connected = self.termination_in()
            except socket.timeout:
                pass

    """"
    Perform the 3-way handshake with the server
    """
    def handshake(self):
        # Step 1
        payload = ""
        packet = Packet(self.streamID, self.synNumber, self.ackNumber, True, False, False, self.window, len(payload), payload)
        self.sock.sendto(packet.getPacket(), self.server)

        # Step 2
        data, addr = self.sock.recvfrom(1016)
        packet2 = fromRecv(data)
        if packet2 is not None and packet.streamID == packet2.streamID and packet.SYNNumber == packet2.SYNNumber and packet.SYNNumber + 1 == packet2.ACKNumber and packet2.flags == 6 and addr == self.server:
            # Step 3
            self.synNumber = packet2.ACKNumber
            self.ackNumber = packet2.ACKNumber
            self.window = min(self.window, packet2.window)  # set window size
            packet = Packet(self.streamID, self.synNumber, self.ackNumber, False, True, False, self.window, len(payload), payload)
            self.sock.sendto(packet.getPacket(), self.server)
            self.synNumber += 1

            return True
        else:
            return False

    """"
    Initiate termination to server
    """
    def termination_in(self):
        # Step 1
        payload = ""
        packet = Packet(self.streamID, self.synNumber, self.ackNumber, False, False, True, self.window, len(payload), payload)
        self.sock.sendto(packet.getPacket(), self.server)

        # Step 2
        data, addr = self.sock.recvfrom(1016)
        packet2 = fromRecv(data)
        if packet2 is not None and packet.streamID == packet2.streamID and packet2.ACKNumber == packet.SYNNumber and packet2.flags == 3 and addr == self.server:
            # Step 3
            self.synNumber += 1
            self.ackNumber = self.synNumber
            packet = Packet(self.streamID, self.synNumber, self.ackNumber, False, True, False, self.window, len(payload), payload)
            self.sock.sendto(packet.getPacket(), self.server)
            return False
        else:
            return True

    """"
    React to termination from server
    """
    def termination_re(self):
        # Step 2:
        payload = ""
        packet = Packet(self.streamID, self.synNumber, self.ackNumber, False, True, True, self.window, len(payload), payload)
        self.sock.sendto(packet.getPacket(), self.server)

        # Step 4:
        data, addr = self.sock.recvfrom(1016)
        packet2 = fromRecv(data)
        if packet2.streamID == self.streamID and packet2.ACKNumber == packet.SYNNumber and packet2.flags == 2 and addr == self.server:
            return False
        else:
            return True

    """"
    Send file to server
    """
    def send(self):
        self.file = File(self.path)
        self.file.readFile()
        packets = self.file.toPackets()

        while len(packets) > 0:
            initSyn = self.synNumber
            length = list(range(0, min(self.window, len(packets)))) # indices of the packets with a maximum of the windowsize
            l = len(length)
            # while there are still packets that are not acknowledged
            while len(length) > 0:
                # Send packets
                for i in length:
                    packet = Packet(self.streamID, initSyn + i, self.ackNumber, True, False, False, self.window, len(packets[i]), packets[i])
                    self.sock.sendto(packet.getPacket(), self.server)

                # Get ACKs for sent packets
                for j in length:
                    try:
                        data, addr = self.sock.recvfrom(1016)
                        packet = fromRecv(data)
                        # Check if server wants to FIN
                        if packet is not None and packet.flags == 1 and packet.streamID == self.streamID:
                            while self.connected:
                                try:
                                    self.connected = self.termination_re()
                                    return
                                except socket.timeout:
                                    pass
                        # Else check if ACK is coming in
                        elif packet is not None and packet.streamID == self.streamID and packet.flags == 2:
                            try:
                                # Remove the index from the packets that have to be checked
                                length.remove(j)
                                self.ackNumber = packet.ACKNumber
                            except ValueError:
                                pass
                    except socket.timeout:
                        pass
            packets = packets[l:]
            self.synNumber += l