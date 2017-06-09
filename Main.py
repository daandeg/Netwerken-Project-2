import sys


def test(a, b):
    return int(a)+int(b)

input = sys.argv
print(test(input[1], input[2]))
