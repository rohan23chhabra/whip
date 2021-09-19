import dns.message
import dns.query
import dns.rdataclass
import dns.rdatatype

import config.config as conf
import records.parseutils as parseutils


class Whip:
    types = {
        'NS': dns.rdatatype.NS,
        'A': dns.rdatatype.A,
        'MX': dns.rdatatype.MX,
        'CNAME': dns.rdatatype.CNAME
    }

    def __init__(self, name, recordType):
        self.nsIPs = {}
        self.name = name
        self.recordType = recordType

    # This function resolves a name by trying all the root servers
    # It returns True if it is able to resolve the name into at least one IP address
    # Else, it returns false
    def resolve(self, name, recordType, ips):
        status = False
        for root in conf.rootServers:
            if self.populateIPs(root, name, recordType, ips):
                status = True
                break
        return status

    # This function connects to the various root (and TLD) servers recursively
    # If the connection is successful and there are no errors in resolution,
    # then it populates the IPs in `ips` and returns True
    # else returns False
    def populateIPs(self, root, name, recordType, ips):
        print('-------------------------------')
        print('Name to resolve - ', name)
        print('Root: ', root)
        query_name = dns.name.from_text(name)
        query = dns.message.make_query(query_name, self.types[recordType])

        try:
            response = dns.query.udp(query, root, timeout=conf.requestTimeout)
        except:
            print('Request to', root, 'timed out. Trying other servers')
            return False

        # Base case
        if len(response.answer) > 0:
            answers = parseutils.parseAnswers(response)
            status = False
            for ans in answers:
                if ans.requestType == self.recordType:
                    status = True
                    ips.append(ans.ip)

                if not status and ans.requestType == 'CNAME':
                    print('CNAME encountered. Resolving CNAME....')
                    if self.resolve(ans.ip, self.recordType, ips):
                        status = True

                if status:
                    break
            return status

        authorityRecords = parseutils.parseAuthorityRecords(response)
        populateNSIPs(response, self.nsIPs)

        status = False
        for authRecord in authorityRecords:
            if authRecord.ip not in self.nsIPs:
                nsIP = []
                if self.resolve(authRecord.ip, recordType, nsIP):
                    self.nsIPs[authRecord.ip] = nsIP[0]

            if self.populateIPs(self.nsIPs[authRecord.ip], name, recordType, ips):
                status = True
                break

        return status


def populateNSIPs(response, nsIps):
    additionalRecords = parseutils.parseAdditionalRecords(response)
    for addRecord in additionalRecords:
        if addRecord.requestType == 'A':
            nsIps[addRecord.domain] = addRecord.ip
    return nsIps
