.DEFAULT_GOAL := dns

.PHONY: dns
dns:
	@python partA.py stonybrook.edu A

.PHONY: dnssec
dnssec:
	@python partB.py example.com A

fmt:
	@isort .

install:
	@pip3 install -r requirements.txt