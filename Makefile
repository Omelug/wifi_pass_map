
test:
	clear
	pytest -q --tb=short tests/*

run:
	python3 app.py

.PHONY: run test