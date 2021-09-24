import sys
import time
from datetime import date

from records.answer import Answer
from src.whip import Whip


def formatOutput(ans, whipObj, elapsedTime):
    print('QUESTION SECTION:')
    print(whipObj.name, '\t', ' IN ', whipObj.recordType)

    print('ANSWER SECTION:')
    print(ans.rrSet)

    t = int(elapsedTime * 1000)
    print('Query time: ', t, ' ms')
    print('WHEN: ', date.today())
    print('MSG SIZE RECEIVED: ', sys.getsizeof(ans.rrSet))


if __name__ == "__main__":
    name = sys.argv[1]
    recordType = sys.argv[2]

    whip = Whip(name, recordType)

    ans = Answer()
    startTime = time.time()
    status = whip.resolve(name, recordType, ans)
    endTime = time.time()
    if not status:
        print('Could not resolve hostname - ', name)
    else:
        formatOutput(ans, whip, endTime - startTime)
