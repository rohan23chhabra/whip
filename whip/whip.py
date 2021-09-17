import logging

import dns.message
import dns.query
import dns.rdataclass
import dns.rdatatype


class Whip:
    rootServers = ['198.41.0.4', '199.9.14.201', '192.33.4.12', '199.7.91.13',
                   '192.203.230.10', '192.5.5.241', '192.112.36.4', '198.97.190.53',
                   '192.36.148.17', '192.58.128.30', '193.0.14.129', '199.7.83.42',
                   '202.12.27.33']

    types = {
        'NS': dns.rdatatype.NS,
        'A': dns.rdatatype.A,
        'MX': dns.rdatatype.MX,
        'CNAME': dns.rdatatype.CNAME
    }

    config = {
        'timeout': 5
    }

    def __init__(self):
        self.ans = []

    def resolve(self, domain, recordType):
        for root in self.rootServers:
            ips = []
            if self.populateIPs(root, domain, recordType, ips):
                self.ans.append(ips)
                break
        return self.ans

    # This function connects to the various root (and TLD) servers recursively
    # If the connection is successful and there are no errors in resolution,
    # then it populates the IPs in `ips` and returns True
    # else returns False
    def populateIPs(self, root, domain, recordType, ips):
        print('Domain - ', domain)
        print('RecordType - ', recordType)
        query_name = dns.name.from_text(domain)
        query = dns.message.make_query(query_name, self.types[recordType])

        response = dns.query.udp(query, root, timeout=self.config['timeout'])

        # If the requests times out, then return and try the next root
        if response is None:
            return False

        # Base case
        if len(response.answer) > 0:
            print('ANSWER: ')
            print(type(response.answer))
            print(type(response.answer[0]))
            print(response.answer[0])

        print('Root: ', root)
        print('---------------------------')

        authorityRecords = getAuthorityRecords(response)
        authorityIPs = getNStoIPMap(response)

        status = False
        for authRecord in authorityRecords:
            # print(authRecord)
            if authRecord.ip not in authorityIPs:
                continue
            print("New domain = ", authRecord.domain)
            status = status or self.populateIPs(authorityIPs[authRecord.ip], domain, recordType, ips)

        return status


def getAuthorityRecords(response):
    authorityRecords = response.authority[0].to_text()
    uncleanedAuths = authorityRecords.split("\n")
    auths = []
    for a in uncleanedAuths:
        auths.append(parseRecord(a))
    return auths


def getNStoIPMap(response):
    nsIps = {}
    additionalRecords = getAdditionalRecords(response)
    for addRecord in additionalRecords:
        nsIps[addRecord.domain] = addRecord.ip
    return nsIps


def getAdditionalRecords(response):
    additionalRecords = []
    for add in response.additional:
        addRecord = parseRecord(add.to_text())
        additionalRecords.append(addRecord)
    return additionalRecords


def getAnswers(response):
    answerRecords = response.answer[0].to_text()
    uncleanedRecords = answerRecords.split(" ")


def isCNAME(record):
    return True


def parseRecord(recordStr):
    recordArr = recordStr.split(" ")
    domain = clean(recordArr[0])
    namespace = clean(recordArr[2])
    requestType = clean(recordArr[3])
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


class Record:

    def __init__(self, domain, ip, requestType, namespace):
        self.domain = domain
        self.ip = ip
        self.requestType = requestType
        self.namespace = namespace

    def __str__(self):
        return "Domain: {}, RequestType: {}, IP: {}, Namespace: {}".format(self.domain,
                                                                           self.requestType, self.ip, self.namespace)
