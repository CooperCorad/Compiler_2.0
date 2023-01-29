TEST=test.jpl

all: run

compile: compiler.py
	python3 -m py_compile $^

run:
	python3 compiler.py -l $(TEST)

clean:
	rm -fr __pycache__