TEST=test.jpl

CXX=clang++
CXXFLAGS=-Og -std=c++17 -Werror -Wall -fsanitize=address,undefined -fno-sanitize-recover=address,undefined

all: run

compile: compiler.cpp
	$(CXX) $(CXXFLAGS) -o a.out compiler.cpp 

run: a.out
	./a.out -l $(TEST)

clean:
	rm -f *.o a.out
