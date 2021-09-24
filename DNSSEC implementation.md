# DNSSEC implementation
There are 3 stages of verification of data:
* Verifying DNSKEY
* Verifying Zone
* Verifying DS record (chain of trust)

## Verifying DNSKEY RRSIG
* A separate request is made to obtain the DNSKEY and its RRSIG from the name servers.
```python
zone = <Current Name Server Zone>
root = <IP address of the name server>
queryName = dns.name.from_text(zone)  
query = dns.message.make_query(queryName, dns.rdatatype.DNSKEY, want_dnssec=True) 
response = dns.query.udp(query, root, timeout=conf.requestTimeout)
```
* Since the DNSKEY is signed using PvtKSK of the name server, we need information about the PubKSK of the nameserver.
* This information is present in the DNSKEY obtained.
* RRSIG decryption happens using the DNSKEY itself since it holds the pubKSK of the name server.
* The `validate` API takes care of the extraction of the PubKSK.
```python
rrSet = <DNSKEY RRSet>
rrSig = <Digital Signature of the DNSKEY RRSet signed using PvtKSK of the name server>
zone = 'edu.' (for example)
dns.dnssec.validate(rrSet, rrSig, {dns.name.from_text(zone): rrSet})
```

Here the map `{dns.name.from_text(zone): rrSet}` signifies that the key to decrypt the DNSKEY RRSIG for zone `edu.` lies in the DNSKEY RRSET itself.
* If the verification is successful, then DNSKEY RRSet is stored for future reference.

## Verifying Zone
* Zone verification happens by matching the hash of the PubKSK of the current zone with the DS record of the parent zone.
* In the case of root server, there is no parent. Therefore, ICANN has already published root PubKSKs which can be used to identify the root.
* Since we trust ICANN, we can trust the PubKSK published by ICANN for the root servers.
* Root PubKSKs are hard-coded and matched against the hash of the PubKSK of the DNSKEY (id = 257 in the code) which was stored when verifying the DNSKEY RRSIG.
* For other zones, DS records are stored at every step (zone) and are fetched in the next step (zone) to match against the PubKSK of the DNSKEY of the current zone.
```python
# From ICANN website (hard-coded)
rootPubKSKHashes = ['E06D44B80B8F1D39A95C0B0D7C65D08458E880409BBC683457104237C7F8EC8D',  
 '49AAC11D7B6F6446702E54A1607371607A1A41855200FD2CE1CDDE32F24E8FB5']
 
verifyZone(dnskey, savedDSRecord, zone):
	pubKSKCurrentZone = extractPubKSK(dnskey) # ID = 257
	algoId = extractAlgoID(dnskey) # algo = SHA1 or SHA256
	hashedKey = dns.dnssec.make_ds(zone, pubKSKCurrentZone, algoId)
	
	if hashedKey == savedDSRecord:
		# Zone verified
```

## Verifying RRSIG of the DS record of the current zone
* Since the DS record is signed using the PvtZSK of the zone, we need information about the PubZSK of the zone.
* This information is in the DNSKEY we saved earlier.
* We use the saved DNSKEY to extract the PubZSK to decrypt the RRSIG of the DS record obtained in the response.
* The actual extraction is done by the `validate` API as shown below:
```python
verifyDS(dsRRSet, rrSig, dnskey, zone):
	dns.dnssec.validate(dsRRSet, rrSig, {dns.name.from_text(zone): dnsKeyRRSet})
```
* The map `{dns.name.from_text(zone): dnsKeyRRSet}` shows that for the current zone, the key comes from the DNSKEY we saved earlier.

These 3 checks are sufficient to verify all the information involved in DNSSEC.

**Note:**:
* `DNSSec not supported` - This happens when RRSIG of the DNSKEY is't available.
* `DNSSec verification failed` - When any of the above checks fail, verification fails.

