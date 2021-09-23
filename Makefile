.DEFAULT_GOAL := run

.PHONY: run
run:
	@python main.py www.cs.stonybrook.edu A

fmt:
	@isort .