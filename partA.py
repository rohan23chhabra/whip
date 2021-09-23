import sys

from records.answer import Answer
from src.whip import Whip

if __name__ == "__main__":
    name = 'www.netflix.com'
    recordType = 'A'

    whip = Whip(name, recordType)

    ans = Answer()
    status = whip.resolve(name, recordType, ans)
    if not status:
        print('Could not resolve hostname - ', name)
    else:
        print(ans.rrSet)
