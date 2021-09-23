class Record:

    def __init__(self, zone, ip, requestType, namespace):
        self.zone = zone
        self.ip = ip
        self.requestType = requestType
        self.namespace = namespace

    def __str__(self):
        return "Zone: {}, RequestType: {}, IP: {}, Namespace: {}".format(self.zone,
                                                                         self.requestType, self.ip, self.namespace)


def parse(recordStr):
    recordArr = recordStr.split(" ")
    zone = clean(recordArr[0])
    namespace = clean(recordArr[2])
    requestType = clean(recordArr[3])
    ip = ""
    if requestType == 'MX':
        ip = clean(recordArr[5])
    else:
        ip = clean(recordArr[4])
    return Record(zone, ip, requestType, namespace)


def clean(string):
    end = len(string) - 1
    while string[end] == '.':
        end -= 1

    start = 0
    while string[start] == '.':
        start += 1

    return string[start:end + 1]
