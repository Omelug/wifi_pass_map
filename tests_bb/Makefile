testp: test_bb_setup # test but with test prints
	. ../.venv/bin/activate && cd test_env \
  	&& BEHAVE_LOG_LEVEL=DEBUG PYTHONPATH=./src && \
  	../../.venv/bin/python ../../.venv/bin/behave features/wigle.feature

test: test_bb_setup
	. ../.venv/bin/activate && cd test_env && PYTHONPATH=./src behave

cover: test_bb_setup
	. ../.venv/bin/activate && cd test_env && PYTHONPATH=./src coverage run -m behave && coverage report && coverage html

test_bb_setup:
	mkdir -p ./pytest_tmp
	mkdir -p ./test_env
	rsync -a --delete --exclude='config' ../src/ ./test_env/src/
	#if [ -d ./tests_bb/src/map_app/sources/config ]; then rm -rf ./tests_bb/src/map_app/sources/config; fi
	#rsync -a Makefile ./tests_bb/test_env/

clean:
	rm -rf ./test_env/data
	rm -rf ./test_env/.coverage
	rm -rf ./test_env/htmlcov


.PHONY: test
