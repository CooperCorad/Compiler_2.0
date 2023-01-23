TEST=test.jpl

CXX=clang++
CXXFLAGS=-Og -std=c++17 -Werror -Wall -fsanitize=address,undefined -fno-sanitize-recover=address,undefined

all: run

compiler: compiler.cpp
	$(CXX) $(CXXFLAGS) -o a.out compiler.cpp 

run: a.out
	./a.out $(TEST)

clean:
	rm -f *.o a.out
