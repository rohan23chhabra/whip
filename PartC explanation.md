# Part C explanation
* Assuming RTTs vary in the following relation for the 3 scenarios:
	* RTT(my local resolver) is approximately equal to the RTT(local DNS resolver)
	* RTT(Google DNS resolver) > RTT(my local resolver) (since Google is the intermediate node)
	* RTT(Google DNS resolver) > RTT(my local resolver) (since Google is the intermediate node)
* The Local DNS resolver is the fastest amongst the 3 servers.
* Almost 95% of the websites take around 0.7 seconds on average to resolve the domain name.
* Courtesy of this assignment, many students have been hitting common domains to the root servers so it is highly likely that the Local DNS resolver has cached a lot of those IP addresses. Hence, it has very performance.
* Whip performs better than the Google DNS Resolver.
* This may be attributed to the following:
    * I am maintaining an in-memory mapping to save IP addresses of Name servers which need to be queried. This is particularly useful when CNAME occurs since it may be possible that the resolver may need to query the same name servers again. Hence storing those IPs helped in better performance.
    * Note that this is totally an in-memory map and nothing is being saved on the disk.
    * The higher latency for Google DNS Resolver may be attributed to higher RTTs as compared to my local resolver. If I use the google DNS resolver, then my local machine has to query the google DNS server and then google DNS server will query the root and the whole hierarchy. Google DNS server is acting as the intermediate between my local machine and the root servers. Thus, multiple requests will incur high RTTs which may be responsible for the latency of the Google DNS resolver.
    * A higher RTT may overweigh the caching and optimizations done by the Google DNS Resolver. 