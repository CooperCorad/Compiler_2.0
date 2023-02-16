TEST=test.jpl
FLAGS=...

all: run

compile: compiler.py
	python3 -m py_compile $^

run:
	python3 compiler.py $(FLAGS) $(TEST)

clean:
	rm -fr __pycache__