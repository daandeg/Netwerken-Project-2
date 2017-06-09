import filecmp
import os

""""
Implementation of a file
"""
class File:
    """"
    Initialization
    """
    def __init__(self, path):
        self.path = path
        self.content = ""
        self.MAX_DATA_LENGTH = 1000

    """"
    Read the contents of the file
    """
    def readFile(self):
        self.content = open(self.path, "r").read()

    """"
    Write the contents of the file
    """
    def writeFile(self):
        open(self.path, "w").write(self.content)

    """"
    Convert the contents of the file to packets
    """
    def toPackets(self):
        packets = []
        while len(self.content) > 0:
            payload, self.content = self.splitcontent()
            packets.append(payload)
        return packets

    """"
    Split the contents into packets of maximum size MAX_DATA_LENGTH
    """
    def splitcontent(self):
        if len(self.content) <= self.MAX_DATA_LENGTH:
            return self.content, ""
        else:
            return self.content[:self.MAX_DATA_LENGTH], self.content[self.MAX_DATA_LENGTH:]

    """"
    Convert packets into contents
    """
    def fromPackets(self, packets):
        self.content = ""
        for packet in packets:
            self.content += packet

    """"
    Compare if the contents of two files are equal
    """
    def compareTo(self, file):
        if os.path.isfile(self.path) and os.path.isfile(file.path):
            return filecmp.cmp(self.path, file.path)
        else:
            return False
