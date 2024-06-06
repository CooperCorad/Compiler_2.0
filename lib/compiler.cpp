#include <iostream>
#include "../include/lexer.h"
using namespace std;
int main(int argc, char **argv) {
    
    if (!strcmp(argv[1], "-l")){
        Lex::Token t = Lex::Token(Lex::ARRAY, 100, "hello!");
        cout << t.text << " " << t.loc << endl;
    }


    return 0;
}