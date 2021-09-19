class Record:

    def __init__(self, domain, ip, requestType, namespace):
        self.domain = domain
        self.ip = ip
        self.requestType = requestType
        self.namespace = namespace

    def __str__(self):
        return "Domain: {}, RequestType: {}, IP: {}, Namespace: {}".format(self.domain,
                                                                           self.requestType, self.ip, self.namespace)


def parse(recordStr):
    recordArr = recordStr.split(" ")
    domain = clean(recordArr[0])
    namespace = clean(recordArr[2])
    requestType = clean(recordArr[3])
    ip = ""
    if requestType == 'MX':
        ip = clean(recordArr[5])
    else:
        ip = clean(recordArr[4])
    return Record(domain, ip, requestType, namespace)


def clean(string):
    end = len(string) - 1
    while string[end] == '.':
        end -= 1

    start = 0
    while string[start] == '.':
        start += 1

    return string[start:end + 1]
