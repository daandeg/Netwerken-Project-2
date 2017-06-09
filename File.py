
class File:
    def __init__(self, path):
        self.path = path
        self.content = ""
        self.MAX_DATA_LENGTH = 1000

    def readFile(self):
        self.content = open(self.path, "r").read()

    def writeFile(self):
        open(self.path, "w").write(self.content)

    def toPackets(self):
        packets = []
        while len(self.content) > 0:
            payload, self.content = self.splitcontent()
            packets.append(payload)
        return packets

    def splitcontent(self):
        if len(self.content) <= self.MAX_DATA_LENGTH:
            return self.content, ""
        else:
            return self.content[:self.MAX_DATA_LENGTH], self.content[self.MAX_DATA_LENGTH:]

    def fromPackets(self, packets):
        self.content = ""
        for packet in packets:
            self.content += packet
