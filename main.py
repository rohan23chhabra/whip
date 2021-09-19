import sys

from cli.whip import Whip

if __name__ == "__main__":
    name = sys.argv[1]
    recordType = sys.argv[2]

    whip = Whip(name, recordType)

    ips = []
    whip.resolve(name, recordType, ips)

    print(ips)
