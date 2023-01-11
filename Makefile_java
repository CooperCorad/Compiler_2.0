TEST=test.jpl

all: run

compile: compiler.class

compiler.class: compiler.java
	javac compiler.java

run: compiler.class
	java compiler $(TEST)

clean:
	rm -fr *.class
