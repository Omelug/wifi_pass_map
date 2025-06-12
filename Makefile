install: env download_lib
env:
	python3 -m venv .venv
	. .venv/bin/activate && pip install --break-system-package -r requirements.txt

download_lib:
	cd src/map_app/static/lib/ && python3 download.py

test:
	PYTEST_CURRENT_TEST=1 . .venv/bin/activate && PYTHONPATH=./src pytest --basetemp=./tests/pytest_tmp -vv --tb=short ./tests

doc:
	 pyreverse

doc_install:
	sudo apt install pipx
	pipx install pylint


run: data_folder
	. .venv/bin/activate && cd src && python3 app.py

data_folder:
	mkdir -p ./data/clean ./data/raw
	chmod u+rwx ./data ./data/clean ./data/raw

set_up_git_hooks:
	for hook in tests/hooks/*; do \
		hook_name=$$(basename $$hook); \
		sudo cp $$hook .git/hooks/$$hook_name; \
		sudo chmod +x .git/hooks/$$hook_name; \
	done

clean:
	rm -rf .venv
	rm -rf src/map_app/static/lib/css
	rm -rf src/map_app/static/lib/js
	rm -rf __pycache__
	rm -rf src/__pycache__
	rm -rf tests/__pycache__

.PHONY: run test