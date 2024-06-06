
TEST=-l test.jpl

CXX=clang++
CXXFLAGS=-Og -std=c++17 -Werror -Wall -fsanitize=address,undefined -fno-sanitize-recover=address,undefined

all: run

compile: compiler.o

compiler.o: lib/compiler.cpp lib/lexer.cpp include/lexer.h
	$(CXX) $(CXXFLAGS) -c lib/compiler.cpp  -o src/compiler.o

a.out: compiler.o
	$(CXX) $(CXXFLAGS) src/compiler.o -o src/a.out

run: a.out
	./src/a.out $(TEST)

janker: compiler.o
	$(CXX) $(CXXFLAGS) src/compiler.o -o src/jank.out

jank: janker
	./src/jank.out $(TEST)

clean:
	rm -f src/*.o src/a.out src/jank