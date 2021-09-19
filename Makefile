.DEFAULT_GOAL := run

.PHONY: run
run:
	@python main.py netflix.com CNAME

fmt:
	@isort .