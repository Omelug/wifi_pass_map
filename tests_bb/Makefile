test:
	. ../.venv/bin/activate && cd test_env && PYTHONPATH=./src behave

cover:
	. ../.venv/bin/activate && cd test_env && PYTHONPATH=./src coverage run -m behave && coverage report && coverage html

.PHONY: test
