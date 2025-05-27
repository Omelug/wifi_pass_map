install:
	cd map_app/static/lib/ && python3 download.py
test:
	clear
	pytest -q --tb=short tests/*

run:
	python3 app.py

.PHONY: run test