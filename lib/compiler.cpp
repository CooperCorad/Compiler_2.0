#include <iostream>
#include "../include/lexer.h"
#include <regex>
using namespace std;
using namespace Lex;

int main(int argc, char **argv) {
    if (!strcmp(argv[1], "-l")){
        Lexer lexMachine = Lexer(argv[2]);
        lexMachine.doLex();
        lexMachine.prettyPrint();
        printf("Compilation succeeded: lexical analysis complete\n");
        
    } else if (!strcmp(argv[1], "-h")) {
        string help_msg = 
        "./jank [stage flag] [optimizer level] [filename]\
        \n\tstage flags:\n\t\t -h -> help \n\t\t -l -> lex \n\t\t -p -> parse \n\t\t -c -> compile\
        \n\toptimizer level: -O[1-3]";
        cout << help_msg << endl;
    }


    return 0;
}