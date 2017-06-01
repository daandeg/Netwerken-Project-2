import binascii
import uuid
from struct import pack, unpack, unpack_from


def fromRecv(byteString):
    header = byteString[0:16]
    streamID, = unpack_from("I", header)
    SYNNumber, = unpack_from("H", header, 4)
    ACKNumber, = unpack_from("H", header, 6)
    flags, = unpack_from("B", header, 8)
    window, = unpack_from("B", header, 9)
    dataLength, = unpack_from("H", header, 10)
    fmt = str(dataLength) + "s"
    payload = str(byteString[16:])
    print(payload)
    SYNflag = False
    ACKflag = False
    FINflag = False
    if(flags >= 4):
        SYNflag = True
        flags -= 4
    if(flags >= 2):
        ACKflag = True
        flags -= 2
    if(flags >= 1):
        FINflag = True
    return Packet(streamID, SYNNumber, ACKNumber, SYNflag, ACKflag, FINflag, window, dataLength, payload)

class Packet:

    def __init__(self, streamID, SYNNumber, ACKNumber, SYNflag, ACKflag, FINflag, window, dataLength, payload):
        self.streamID = streamID
        print(self.streamID)
        self.SYNNumber = SYNNumber
        self.ACKNumber = ACKNumber
        self.flags = 0
        if (SYNflag):
            self.flags += 4
        if (ACKflag):
            self.flags += 2
        if (FINflag):
            self.flags += 1
        self.window = window
        self.dataLength = dataLength
        self.payload = payload
        header = self.createHeader(0)
        packet = header + payload.encode("utf-8")
        self.checksum = binascii.crc32(packet)


    def createHeader(self, checksum):
        return pack("IHHBBHI", self.streamID, self.SYNNumber, self.ACKNumber, self.flags, self.window, self.dataLength, checksum)

    def getPacket(self):
        return self.createHeader(self.checksum) + self.payload.encode("utf-8")
