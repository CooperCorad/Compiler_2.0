TEST=test.jpl

CXX=clang++
CXXFLAGS=-Og -std=c++17 -Werror -Wall -fsanitize=address,undefined -fno-sanitize-recover=address,undefined

all: run

compile: compiler.o

compiler.o: compiler.cpp
	$(CXX) $(CXXFLAGS) -c compiler.cpp -o compiler.o

a.out: compiler.o
	$(CXX) $(CXXFLAGS) compiler.o -o a.out

run: a.out
	./a.out $(TEST)

clean:
	rm -f *.o a.out
