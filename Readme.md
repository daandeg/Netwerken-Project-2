# Project 2 Framework

## Description

This directory contains a framework for a basic form of TCP over UDP. This effectively provides a file transfer client-server combination. This is done by implementing a 3-way handshake, a file tranfer respecting reliability and flow control and termination.

For this project, we used Python 3.6 in a framework provided for this project. For testing we are provided with a testing framework, which will be elaborated later.

## File structure

* bTCP_client.py: the basic TCP client. It has the following methods:
	* connect: connect the client to the server
	* disconnect: disconnect the client from the server
	* handshake: perform the 3-way handshake, which will be elaborated later
	* termination_in: initiate termination to the server
	* termination_re: react to termination from the server
	* send: send a file to the server
* bTCP_server: the basic TCP server. It has the following methods:
	* handshake: connect the server to the client
	* termination_re: react to termination from the client
	* termination_in: initiate termination to the client
	* receive: 
		* perform handshake with the client
		* receive file from the client
		* terminate connecting by either initiating itself or let the client initiate
	* writePackets: write the received packets to the output file
	* orderTermination: order the server to terminate the connection
* File: a file. It has the following methods:
	* readFile: read the contents of the file
	* writeFile: write the contents of the file
	* toPackets: convert the contents of the file to packets
	* splitcontent: split the content into packets with as maximum size the maximum data length
	* fromPackets: convert given packets into contents
	* compareTo: compare if the contents of the file equals the contents of another file
* Packet: a basic TCP packet consisting of a header and a payload. It has the following methods:
	* createHeader: create the header of the packet
	* getPacket: return the packet

## 3-way handshake

the 3-way handshake establishes the connection between the client and the server. It initializes a Sequence number and determines the window size. The process is described as follows:
1. The client sends a SYN packet to the server
2. The server responds with a SYN-ACK packet, where the ACK-number is set to one higher than the SYN-number of the clients packet
3. The client responds with an ACK packet, where the SYN-number is set to the ACK-number of the servers packet
Since the server sends one packet to the client, the client learns about the window size that the server allows for, which is needed to guarantee flow control.

## Transferring a file

For transferring a file the following procedure is followed:
1. The client splits the file up into packets
2. The client sends a number of packets to the server, up to the window size
3. The server acknowledges these packets if it receives it by setting the ACK-number equal to the SYN-number of the packet of the client
4. If the server does not acknowledge the message within the timeout time, the client sends the packet again, until all packets have been acknowledged
5. If there are more packets left, go to step 2
6. Otherwise, initiate termination

We see that if a packet is not acknowledged, it is sent again by the client. This makes that the client always knows if reliable tranfer is accomplished.

Another problem might be that the order of the packets might be shuffled. We fix this by letting the server save the payload of the packet in a tuple with the SYN-number. Then, in the end, we can order them by SYN-number, resulting in the right order of the payloads and thus in the right message.

## Terminating the connection

Termination can be initiated by either the client side or the server side. The process is as follows:
1. The initiator sends a FIN packet to the reactor
2. The reactor responds with a FIN-ACK packet to the initiator
3. The initiator responds to this packet by sending a FIN-ACK packet and he closes its connection
4. The reactor receives this FIN-ACK packet and he closes its connection

At this point in time, we assume that the client has sent all the packets of the file to the server, and thus at this point the server writes the packets to the file.

## Flags

A brief description for the flags must be given as they are hard to understand when seeing them in action in our project. We were provided with 8 bits to represent those three flags, but effectively we only used 3. The flags variable is set as follows:
* Initially, the flags are set to 0
* If the SYN-flag is set, 4 is added
* If the ACK-flag is set, 2 is added
* If the FIN-flag is set, 1 is added
This makes that all possible states for the flags are represented. E.g. if a SYN-ACK packet is sent, the flags are equal to 6. By this, it is easy to see which flags are set and which are not.
