#include "../include/parser.h"
using namespace Parse;
using namespace Lex;
using namespace std;

ParseException::ParseException(const char* msg) :
    message(msg) {};

const char* ParseException::what() {
    return message;
}



Parser::Parser(std::vector<std::unique_ptr<Lex::Token>> tokens) :
    tokens(std::move(tokens)) {}

string Parser::expectToken(int *pos, Tokty tok) {
    if (tokens[*pos]->tokty != tok) {
        const char* ex = ("No token of type " + revTbl.find(tok)->second + " was found at " + to_string(*pos).c_str()).c_str();
        throw ParseException(ex);
    } 
    return tokens[*(pos)++]->text; //TODO: does this incr correctly? want tokens[pos] and THEN pos++ 
}


void Parser::doParse() {
    throw ParseException("did u just try to parse??");
}

void Parser::prettyPrint() {

}