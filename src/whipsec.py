import dns.dnssec
import dns.message
import dns.query
import dns.rdataclass
import dns.rdatatype

import config.config as conf
import src.secstatus as secstatus
from records.answer import Answer


# WhipSec class holds all the attributes and class variables required to resolve the name
# and perform the DNSSEC verifications
class WhipSec:
    types = {
        'NS': dns.rdatatype.NS,
        'A': dns.rdatatype.A,
        'MX': dns.rdatatype.MX,
    }

    rootZone = '.'
    KSK = 257
    ZSK = 256

    algorithms = {
        dns.dnssec.RSASHA1: 1,
        dns.dnssec.RSASHA256: 2,
    }

    # Hard coded Root public KSK (from ICANN website)
    rootPubKSKHashes = ['E06D44B80B8F1D39A95C0B0D7C65D08458E880409BBC683457104237C7F8EC8D',
                        '49AAC11D7B6F6446702E54A1607371607A1A41855200FD2CE1CDDE32F24E8FB5']

    def __init__(self, name, recordType):
        self.mappings = {}
        self.name = name
        self.recordType = recordType

    # This function resolves a name by trying all the root servers
    # It returns True if it is able to resolve the name into at least one IP address
    # Else, it returns false
    def resolve(self, name, recordType, ans):
        status = False
        for root in conf.rootServers:
            resp = self.populateAnswers(root, self.rootZone, name, recordType, ans, self.rootPubKSKHashes)
            # If verifications fails at any step, then return immediately
            if ans.dnssecStatus == 1:
                return False
            if isinstance(resp, bool):
                if resp:
                    status = True
                    break
            else:  # Verification failed. Break immediately.
                return False
        return status

    # This function connects to the various root (and TLD) servers recursively
    # If the connection is successful and there are no errors in resolution,
    # then it populates the IPs in `ans` and returns True
    # else returns False
    def populateAnswers(self, root, zone, name, recordType, ans, parentDS):
        if name is not self.name:
            if name in self.mappings:
                return True

        query_name = dns.name.from_text(name)
        query = dns.message.make_query(query_name, self.types[recordType], want_dnssec=True)

        try:
            response = dns.query.udp(query, root, timeout=conf.requestTimeout)
        except:
            return False

        # Check if the response is SOA
        if len(response.authority) > 0 and response.authority[0].rdtype == dns.rdatatype.SOA:
            ans.rrSet = response.authority[0]
            return True

        status = self.verify(response, zone, root, ans, parentDS)
        if isinstance(status, bool):
            # If verifications fails, return an error code
            ans.dnssecStatus = 1
            return secstatus.DNSSECVerificationFailed
        # Save the DS record to use in the next zone
        newParentDS = status

        # Base case
        if len(response.answer) > 0:
            status = False
            for answerEntry in response.answer:
                if answerEntry.rdtype == self.types[recordType]:
                    ans.rrSet = answerEntry
                    status = True
                    break

            if not status:
                for answerEntry in response.answer:
                    if answerEntry.rdtype == dns.rdatatype.CNAME:
                        for cname, _ in answerEntry.items.items():
                            if self.resolve(cname.to_text(), self.recordType, ans):
                                status = True
                                break

            return status

        populateMappings(response, self.mappings)

        authorityRRSet = response.authority[0]
        status = False
        for server in authorityRRSet:
            if server.target.to_text() == name:
                continue

            ipStatus = True
            if server.target.to_text() not in self.mappings:
                ipStatus = False
                temp = Answer()
                if self.resolve(server.target.to_text(), 'A', temp):
                    ipStatus = True
                    if temp.rrSet:
                        for entry, _ in temp.rrSet.items.items():
                            self.mappings[server.target.to_text()] = entry.to_text()
                            break

            if ipStatus and self.populateAnswers(self.mappings[server.target.to_text()], authorityRRSet.name.to_text(),
                                                 name, recordType, ans, newParentDS):
                if ans.dnssecStatus == 1:
                    return secstatus.DNSSECVerificationFailed
                else:
                    status = True
                    break

        return status

    # Verifies the 3 stages
    def verify(self, resp, zone, root, ans, parentDS):
        status = self.verifyDNSKey(zone, root, ans)
        if isinstance(status, int):
            return False

        dnsKeyRRSet = status
        status = self.verifyZone(zone, dnsKeyRRSet, parentDS)
        if not status:
            ans.statusMessage = 'DNSSec verification failed'
            return False

        status = self.verifyChainOfTrust(zone, resp, ans, dnsKeyRRSet, dns.rdatatype.DS)
        if isinstance(status, int):
            return False

        return status

    def verifyDNSKey(self, zone, root, ans):
        queryName = dns.name.from_text(zone)
        query = dns.message.make_query(queryName, dns.rdatatype.DNSKEY, want_dnssec=True)

        try:
            response = dns.query.udp(query, root, timeout=conf.requestTimeout)
        except:
            return secstatus.RequestTimedOut

        if len(response.answer) == 0:
            ans.statusMessage = 'DNSSec not supported'
            return secstatus.DNSKEYAndRRSigAbsent

        if len(response.answer) == 1:
            return response.answer[0]

        if response.answer[0].rdtype == dns.rdatatype.RRSIG:
            rrSet = response.answer[1]
            rrSig = response.answer[0]
        else:
            rrSet = response.answer[0]
            rrSig = response.answer[1]

        try:
            dns.dnssec.validate(rrSet, rrSig, {dns.name.from_text(zone): rrSet})
        except dns.dnssec.ValidationFailure:
            ans.statusMessage = 'DNSSec verification failed'
            return secstatus.DNSKEYInvalid
        return rrSet

    def verifyZone(self, zone, dnsKeyRRSet, parentDS):
        for keyEntry in dnsKeyRRSet.items.items():
            # Handle only if it is a KSK
            if keyEntry[0].flags == self.KSK:
                keyHash = dns.dnssec.make_ds(zone, keyEntry[0], self.algorithms[keyEntry[0].algorithm])
                for storedHash in parentDS:
                    if storedHash == keyHash.digest.hex().upper():
                        return True
            # type of keyEntry is DNSKEY
            # attributes
            # flags, algorithm, protocol, key
        return False

    def verifyChainOfTrust(self, zone, resp, ans, dnsKeyRRSet, recordType):
        rrSig = None
        secRecords = resp.authority if len(resp.authority) > 0 else resp.answer
        for entry in secRecords:
            if entry.rdtype == dns.rdatatype.RRSIG:
                rrSig = entry
                break

        if rrSig is None:
            ans.statusMessage = 'DNSSec not supported'
            return secstatus.RRSigNotFound

        recordTypeToVerify = dns.rdatatype.DS
        if rrSig.covers == dns.rdatatype.A:
            recordTypeToVerify = dns.rdatatype.A
        elif rrSig.covers == dns.rdatatype.NSEC:
            recordTypeToVerify = dns.rdatatype.NSEC
        elif rrSig.covers == dns.rdatatype.NSEC3:
            recordTypeToVerify = dns.rdatatype.NSEC3
        elif rrSig.covers == dns.rdatatype.NS:
            recordTypeToVerify = dns.rdatatype.NS
        elif rrSig.covers == dns.rdatatype.MX:
            recordTypeToVerify = dns.rdatatype.MX

        isVerified = False
        currentDS = []
        for entry in secRecords:
            if entry.rdtype == recordTypeToVerify:
                try:
                    dns.dnssec.validate(entry, rrSig, {dns.name.from_text(zone): dnsKeyRRSet})
                except dns.dnssec.ValidationFailure:
                    continue
                isVerified = True
                for e in entry.items.items():
                    if recordTypeToVerify == dns.rdatatype.DS:
                        currentDS.append(e[0].digest.hex().upper())

        if isVerified:
            return currentDS

        ans.statusMessage = 'DNSSec verification failed'
        return secstatus.DSRecordInvalid


def populateMappings(response, nsIps):
    additionalList = response.additional
    for element in additionalList:
        for ipAddress, _ in element.items.items():
            nsIps[element.name.to_text()] = ipAddress.to_text()
