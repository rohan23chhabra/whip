import sys

from records.answer import Answer
from src.whipsec import WhipSec

if __name__ == "__main__":
    name = sys.argv[1]
    recordType = sys.argv[2]

    whipSec = WhipSec(name, recordType)

    ans = Answer()
    status = whipSec.resolve(name, recordType, ans)
    if not status:
        print('Could not resolve hostname - ', name)
    else:
        print(ans.rrSet)
        print(ans.statusMessage)

def formatOutput(ans):
    