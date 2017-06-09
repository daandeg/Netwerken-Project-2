import argparse

from bTCP_client import *
from bTCP_server import *

parser = argparse.ArgumentParser()
parser.add_argument("-w", "--window", help="Define bTCP window size", type=int, default=100)
parser.add_argument("-t", "--timeout", help="Define bTCP timeout in milliseconds", type=int, default=100)
parser.add_argument("-i", "--input", help="File to send", default="tmp.file")
args = parser.parse_args()

addr_server = ("127.0.0.1", 9001)
addr_client = ("127.0.0.1", 9002)
server = bTCPServer(args.window, args.timeout, "Output/test.txt", addr_server)
client = bTCPClient(args.window, args.timeout, "Input/test.txt", addr_server, addr_client)

server.receive()
client.connect()
client.send()