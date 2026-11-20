.PHONY: install build refresh test
install:
	python3 -m pip install -r requirements.txt
build:
	python3 -m src.analysis --offline
refresh:
	python3 -m src.analysis --refresh
test:
	python3 -m pytest -q
