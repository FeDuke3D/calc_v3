all: test run

build:
	python3.11 setup.py build_ext -i

run: build
	python3.11 smart_calc_v3.py

mac_dist:
	python3.11 setup.py py2app
	productbuild --content dist/smart_calc_v3.app dist/smart_calc_v3.pkg

python_dist:
	python3.11 setup.py bdist

test: build
	pytest

clean:
	rm -rf build dist model/*.so
