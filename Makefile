.PHONY: build check

build:   ## перегенерировать адаптеры из канона
	python3 build-adapters.py

check:   ## адаптеры == генерация из канона
	python3 check-surfaces.py
