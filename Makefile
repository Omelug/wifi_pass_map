install: env download_lib

download_lib:
	cd src/map_app/static/lib/ && python3 download.py

test:
	clear
	PYTHONPATH=./src && . .venv/bin/activate && pytest -q --tb=short ./tests/*

run:
	. .venv/bin/activate && cd src && python3 app.py

env:
	python3 -m venv .venv
	. .venv/bin/activate && pip install --break-system-package -r requirements.txt

clean:
	rm -rf .venv
	rm -rf src/map_app/static/lib/css
	rm -rf src/map_app/static/lib/js
	rm -rf __pycache__
	rm -rf src/__pycache__
	rm -rf tests/__pycache__

.PHONY: run test