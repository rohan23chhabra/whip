import dns.message
import dns.query
import dns.rdataclass
import dns.rdatatype

import config.config as conf
from records.answer import Answer


# Whip class holds all the attributes and class variables required to resolve the name
class Whip:
    types = {
        'NS': dns.rdatatype.NS,
        'A': dns.rdatatype.A,
        'MX': dns.rdatatype.MX,
    }

    def __init__(self, name, recordType):
        # mappings - in memory map to hold IP addresses of name servers during resolution
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
            return False

        # Check if the response is SOA
        if len(response.authority) > 0 and response.authority[0].rdtype == dns.rdatatype.SOA:
            ans.rrSet = response.authority[0]
            return True

        # Base case
        if len(response.answer) > 0:
            status = False
            for answerEntry in response.answer:
                if answerEntry.rdtype == self.types[recordType]:
                    ans.rrSet = answerEntry
                    status = True
                    break

            # Check for CNAME
            if not status:
                for answerEntry in response.answer:
                    if answerEntry.rdtype == dns.rdatatype.CNAME:
                        for cname, _ in answerEntry.items.items():
                            # Resolve the CNAME recursively to get the IP address
                            if self.resolve(cname.to_text(), self.recordType, ans):
                                status = True
                                break

            return status

        # Populate the in-memory map
        populateMappings(response, self.mappings)

        authorityRRSet = response.authority[0]
        status = False
        for server in authorityRRSet:
            if server.target.to_text() == name:
                continue

            ipStatus = True
            # Check if the next name server is already in the map
            if server.target.to_text() not in self.mappings:
                ipStatus = False
                temp = Answer()
                # If the name server's IP is unknown, resolve it recursively to get its IP
                if self.resolve(server.target.to_text(), 'A', temp):
                    ipStatus = True
                    if temp:
                        for entry, _ in temp.rrSet.items.items():
                            self.mappings[server.target.to_text()] = entry.to_text()
                            break

            # Recursively ask the next name server to resolve the name
            if ipStatus and self.populateAnswers(self.mappings[server.target.to_text()], name, recordType, ans):
                status = True
                break

        return status


def populateMappings(response, nsIps):
    additionalList = response.additional
    for element in additionalList:
        for ipAddress, _ in element.items.items():
            nsIps[element.name.to_text()] = ipAddress.to_text()
