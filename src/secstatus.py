# These are some status codes that represent errors that can occur during verification in DNSSEC
RRSigNotFound = 1
DNSKEYAbsent = 2
DNSKEYInvalid = 3
ZoneValid = 4
ZoneInvalid = 5
DSRecordAbsent = 6
DSRecordInvalid = 7
NSECRecordAbsent = 8
NSECRecordInvalid = 9
AllGood = 10
DNSSECVerificationFailed = 11
DNSKEYAndRRSigAbsent = 12
RequestTimedOut = 13
