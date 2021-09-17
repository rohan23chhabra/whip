import sys

from whip.whip import Whip

if __name__ == "__main__":
    whip = Whip()
    ips = whip.resolve(sys.argv[1], sys.argv[2])
    print(ips)
