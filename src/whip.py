import dns.message
import dns.query
import dns.rdataclass
import dns.rdatatype

import config.config as conf
from records.answer import Answer


class Whip:
    types = {
        'NS': dns.rdatatype.NS,
        'A': dns.rdatatype.A,
        'MX': dns.rdatatype.MX,
    }

    def __init__(self, name, recordType):
        self.mappings = {}
        self.name = name
        self.recordType = recordType

    # This function resolves a name by trying all the root servers
    # It returns True if it is able to resolve the name into at least one RRSet
    # Else, it returns false
    def resolve(self, name, recordType, ans):
        status = False
        for root in conf.rootServers:
            if self.populateAnswers(root, name, recordType, ans):
                status = True
                break
        return status

    # This function connects to the various root (and TLD) servers recursively
    # If the connection is successful and there are no errors in resolution,
    # then it populates the IPs in `ans` and returns True
    # else returns False
    def populateAnswers(self, root, name, recordType, ans):
        query_name = dns.name.from_text(name)
        query = dns.message.make_query(query_name, self.types[recordType])

        try:
            response = dns.query.udp(query, root, timeout=conf.requestTimeout)
        except:
            print('Request to', root, 'timed out. Trying other servers')
            return False

        # Check if the response is SOA
        if len(response.authority) > 0 and response.authority[0].rdtype == dns.rdatatype.SOA:
            ans.rrSet = response.authority[0]
            return True

        # Base case
        if len(response.answer) > 0:
            print('ANSWER')
            status = False
            for answerEntry in response.answer:
                if answerEntry.rdtype == self.types[recordType]:
                    print('Populating ips for ', name)
                    ans.rrSet = answerEntry
                    status = True
                    break

            if not status:
                for answerEntry in response.answer:
                    if answerEntry.rdtype == dns.rdatatype.CNAME:
                        print('CNAME encountered for name - ', name)
                        for cname, _ in answerEntry.items.items():
                            print('Resolving ', cname.to_text())
                            if self.resolve(cname.to_text(), self.recordType, ans):
                                status = True
                                break

            return status

        print('Name - ', name)
        print('Response.authority - ')
        print(response.authority)
        print('Response additional - ')
        print(response.additional)

        populateMappings(response, self.mappings)

        authorityRRSet = response.authority[0]
        status = False
        for server in authorityRRSet:
            print('Asking server - ', server.target.to_text())
            if server.target.to_text() == name:
                continue

            ipStatus = True
            if server.target.to_text() not in self.mappings:
                print(server.target, 'not in mappings. Resolving...')
                ipStatus = False
                temp = Answer()
                if self.resolve(server.target.to_text(), 'A', temp):
                    print('Resolved - ', server.target.to_text())
                    print('Temp - ')
                    print(temp)
                    print(type(temp))
                    ipStatus = True
                    if temp:
                        for entry, _ in temp.rrSet.items.items():
                            self.mappings[server.target.to_text()] = entry.to_text()
                            break

            if ipStatus and self.populateAnswers(self.mappings[server.target.to_text()], name, recordType, ans):
                status = True
                break

        return status


def populateMappings(response, nsIps):
    additionalList = response.additional
    for element in additionalList:
        for ipAddress, _ in element.items.items():
            nsIps[element.name.to_text()] = ipAddress.to_text()
