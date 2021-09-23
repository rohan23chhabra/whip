import dns.message

rootServers = ['198.41.0.4', '199.9.14.201', '192.33.4.12', '199.7.91.13',
               '192.203.230.10', '192.5.5.241', '192.112.36.4', '198.97.190.53',
               '192.36.148.17', '192.58.128.30', '193.0.14.129', '199.7.83.42',
               '202.12.27.33']

requestTimeout = 1

rootPublicKSK = dns.rrset.from_text('.', 172800, 'IN', 'DNSKEY', '257 3 8 AwEAAaz/tAm8yTn4Mfeh5eyI96WSVexT '
                                                                 'BAvkMgJzkKTOiW1vkIbzxeF3+/4RgWOq '
                                                                 '7HrxRixHlFlExOLAJr5emLvN7SWXgnLh '
                                                                 '4+B5xQlNVz8Og8kvArMtNROxVQuCaSnI '
                                                                 'DdD5LKyWbRd2n9WGe2R8PzgCmr3EgVLr '
                                                                 'jyBxWezF0jLHwVN8efS3rCj/EWgvIWgb '
                                                                 '9tarpVUDK/b58Da+sqqls3eNbuv7pr+e '
                                                                 'oZG+SrDK6nWeL3c6H5Apxz7LjVc1uTId '
                                                                 'sIXxuOLYA4/ilBmSVIzuDWfdRUfhHdY6 '
                                                                 '+cn8HFRm+2hM8AnXGXws9555KrUB5qih '
                                                                 'ylGa8subX2Nn6UwNR1AkUTV74bU=')
