#include "../include/lexer.h"
#include <iostream>
using namespace std;
using namespace Lex;

Token(Tokty tok, int loc, string txt) {
    tokty = tok;
    loc = loc;
    text = txt;
}

