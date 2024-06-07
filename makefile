
TEST=-l test.jpl

INCLUDE = ../include/
CXX=clang++
# CXXFLAGS=-Og -std=c++17 -Werror -Wall -fsanitize=address,undefined -fno-sanitize-recover=address,undefined
CXXFLAGS=-Og -std=c++17 -Wall -fsanitize=address,undefined -fno-sanitize-recover=address,undefined

all: run

compile: compiler.o

lexer.o: lib/lexer.cpp include/lexer.h
	$(CXX) $(CXXFLAGS) -c lib/lexer.cpp -o src/lexer.o

compiler.o:
	$(CXX) $(CXXFLAGS) -c lib/compiler.cpp -o src/compiler.o

a.out: lexer.o compiler.o
	$(CXX) $(CXXFLAGS) src/compiler.o src/lexer.o -o src/a.out

run: a.out
	./src/a.out $(TEST)



janker: compiler.o
	$(CXX) $(CXXFLAGS) src/compiler.o -o src/jank.out

jank: janker
	./src/jank.out $(TEST)

clean:
	rm -f src/*.o src/a.out src/jank