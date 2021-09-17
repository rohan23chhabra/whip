.DEFAULT_GOAL := run

.PHONY: run
run:
	@python main.py www.netflix.com A

fmt:
	@isort .