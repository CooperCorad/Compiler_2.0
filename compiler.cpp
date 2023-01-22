#include <iostream>
#include <string.h>
#include <vector>
#include <unordered_map>
#include <regex>
#include <iostream>
#include <fstream>
#include <charconv>

using namespace std;

class LexerException : public exception {
    private:
        const char* message;

    public:
        LexerException(const char* msg) : message(msg) {}
        const char * what () const throw () {
            return message;
        }
};

enum tokType {ARRAY, ASSERT, BOOL, ELSE, 
FALSE, FLOAT, FN, IF, IMAGE, INT, LET, PRINT, 
READ, RETURN, SHOW, SUM, THEN, TIME, TO, TRUE, TYPE, 
WRITE, COLON, LCURLY, RCURLY, LPAREN, RPAREN, COMMA, 
LSQUARE, RSQUARE, EQUALS, STRING, INTVAL, FLOATVAL, VARIABLE, 
OP, NEWLINE, END_OF_FILE};

unordered_map<string, tokType> stringToTok = { { "array", tokType::ARRAY }, { "assert", tokType::ASSERT },
{ "bool", tokType::BOOL }, { "else", tokType::ELSE }, { "false", tokType::FALSE }, { "float", tokType::FLOAT },
{ "fn", tokType::FN }, { "if", tokType::IF }, { "image", tokType::IMAGE }, { "int", tokType::INT },
{ "let", tokType::LET }, { "print", tokType::PRINT }, { "read", tokType::READ }, { "return", tokType::RETURN },
{ "show", tokType::SHOW }, { "sum", tokType::SUM }, { "then", tokType::THEN }, { "time", tokType::TIME },
{ "to", tokType::TO }, { "true", tokType::TRUE }, { "type", tokType::TYPE }, { "write", tokType::WRITE },
{ "write", tokType::WRITE }, { ":", tokType::COLON }, { "{", tokType::LCURLY }, { "}", tokType::RCURLY },
{ "(", tokType::LPAREN }, { ")", tokType::RPAREN }, { ",", tokType::COMMA }, { "[", tokType::LSQUARE },
{ "]", tokType::RSQUARE }, { "=", tokType::EQUALS }, { "string", tokType::STRING }, { "int", tokType::INTVAL },
{ "float", tokType::FLOATVAL }, { "var", tokType::VARIABLE }, { "op", tokType::OP }, { "\n", tokType::NEWLINE },
{ "EOF", tokType::END_OF_FILE } };

struct token {
  tokType t;
  int start;
  std::string text;
};


std::vector<token> tokens;
std::string file;
int fileSize; 


int lexWhiteSpace(int index){
    
    bool hasNL = false;

    while(index < fileSize){

        if(file[index] == ' '){
            index++;
        }
        else if(file[index] == '/'){
            if(file[index + 1] == '/'){
                while(file[index] != '\n'){
                    index++;
                }
                index++;
            }
            else if(file[index + 1] == '*'){
                index += 2;
                while(file[index] != '*' && file[index + 1] != '/'){
                    index++;
                }
                index += 3;

            }
        }
        else if(file[index] == '\\' && file[index] != '\n'){
            index++;
        }

        else if(file[index] == '\n' && file[index] != '\\'){
            if(!hasNL){
                hasNL = true;
                tokens.push_back(token{tokType::NEWLINE, index, "\n"});
            }
            index += 1;
        }
        else if(index == (fileSize - 1)){
            tokens.push_back(token{tokType::END_OF_FILE, index, "EOF"});
            break;
        }   
        else{
            break;
        }
        // index++;
    }
    
    return index;
}

const char* makeError(char* msg, int index){
    
    char temp[10000 + sizeof(char)];
    to_chars(temp, temp + 10000, index);    
    char const* ret = strcat(msg, temp);

    return ret;
}


std::pair<token, int> lexPunct(int index){
    int originalI = index;
    regex regPUNCT ("^[\\:\\{\\}\\(\\)\\[\\],=]");
    smatch PUNCTMatch;
    string sub = file.substr(index);

    regex_search(sub, PUNCTMatch, regPUNCT);
    string tokStr = PUNCTMatch[0];
    int newIndex = index + tokStr.size();

    if(!tokStr.size()){
        throw LexerException(makeError((char*)"unable to find punctuation at ", originalI));
    }

    return make_pair(token{stringToTok[tokStr], newIndex, tokStr}, newIndex);
}


std::pair<token, int> lexSTR(int index){
    int originalI = index;
    std::string tokStr = "";
    if (file[index] != '\"'){
        //TODO throw exception
        throw LexerException(makeError((char*)"unable to find a string at: ", originalI));

    }
    else{
        tokStr += '"';
        index++;
    }
    while((file[index] == 10 || (file[index] >= 32 && file[index] <= 126)) && file[index] != '\"' && index < fileSize){
        tokStr += file[index];
        index++;
    } 
    if(index == fileSize){
        throw LexerException("Lexing failed! Reached end of file without string termination");
    }

    tokStr += '"';
    index++;
    return std::make_pair(token{tokType::STRING, index, tokStr}, index);

}

std::pair<token, int> lexVAR(int index){
    int originalI = index;
    std::regex regVAR("^[A-Za-z]+[A-Za-z0-9_\\.]*$");
    string sub = file.substr(index);
    smatch VARmatch;

    regex_search(sub, VARmatch, regVAR);

    if(!string(VARmatch[0]).size()){
        //TODO throw
        throw LexerException(makeError((char*)"unable to find a variable at: ", originalI));
    }

    string tokStr = string(VARmatch[0]);
    int newindex = (int) tokStr.size() + index;

    return make_pair(token{tokType::VARIABLE, newindex, tokStr}, newindex);

}

std::pair<token, int> lexOP(int index){
    int originalI = index;
    std::regex regOP("^(&&)|(\\|\\|)|(<=)|(>=)|(<)|(>)|(==)|(!=)|(\\+)|(-)|(\\*)|(\\/)|(%)|(!)");
    string sub = file.substr(index);
    smatch OPmatch;

    regex_search(sub, OPmatch, regOP);
    string tokStr = string(OPmatch[0]);    
    int newIndex = index + (int)tokStr.size();

    if(!string(OPmatch[0]).size()){
        // TODO throw error
        throw LexerException(makeError((char*)"unable to find a operator at: ", originalI));

    }
    return make_pair(token{tokType::OP, newIndex, tokStr}, newIndex);

}

std::pair<token, int> lexKeyWord(int index){
    int originalI = index;
    std::regex regKeyword("(array)|(assert)|(bool)|(else)|(false)|(float)|(fn)|(if)|(image)|(int)|(let)|(print)|(read)|(return)|(show)|(sum)|(then)|(time)|(to)|(true)|(type)|(write)");
    smatch keywordmatch;
    string sub = file.substr(index);

    regex_search(sub, keywordmatch, regKeyword);
    string tokStr = string(keywordmatch[0]);
    int newIndex = index + (int)tokStr.size();

    if(!tokStr.size()){ // TODO throw!! if the size is 0
        throw LexerException(makeError((char*)"unable to find a keyword at: ", originalI));
    }
    return make_pair(token{stringToTok[tokStr], newIndex, tokStr}, newIndex);

}

std::pair<token, int> lexNum(int index){
    int originalI = index;
    std::regex regFloat ("(^[0-9]+\\.[0-9]*$)|(^[0-9]*\\.[0-9]+$)");
    std::regex regInt ("^[0-9]+$");
    std::smatch floatMatch;
    std::smatch intMatch;
    string sub = file.substr(index);

    regex_search(sub, floatMatch, regFloat);
    regex_search(sub, intMatch, regInt);

    if(!string(floatMatch[0]).size() && !string(intMatch[0]).size()){
        // TODO  throw

        throw LexerException(makeError((char*)"Unable to find a number at ", originalI));
    }
    else if(string(floatMatch[0]).size()){ // if the program has a match 
        string tokstr = string(floatMatch[0]);
        int newIndex = (int)tokstr.size() + index;
        return std::make_pair(token{tokType::FLOATVAL, newIndex, tokstr}, newIndex);
    }
    string tokstr = string(intMatch[0]);
    int newIndex = (int)tokstr.size() + index;
    return std::make_pair(token{tokType::INTVAL, newIndex, tokstr}, newIndex);
    
}


std::pair<token, int> tryLex(int index){
    pair<token, int> ret;
    try{
        ret = lexNum(index);
    }
    catch(LexerException lexep){
            try{
                ret = lexKeyWord(index);
            }
            catch(LexerException lexep){
                    try{
                        ret = lexVAR(index);
                    }
                    catch(LexerException lexep){
                            try{
                                ret = lexOP(index);
                            }
                            catch(LexerException lexep){
                                try{
                                    ret = lexPunct(index);
                                }
                                catch(LexerException lexep){
                                        try{
                                            ret = lexSTR(index);
                                        }
                                        catch(LexerException lexep){
                                                throw(LexerException("Compilation failed! Unable to lex your program!"));
                                        }
                                }
                            }
                    }
            }
    }
    return ret;

}

std::vector<token> lexer(){
    int index = lexWhiteSpace(0);

    while (index < fileSize){
        std::pair<token, int> info = tryLex(index);
        tokens.push_back(info.first);
        index = lexWhiteSpace(info.second);
    }

    return tokens;
}


int main(int argc, char **argv) {    
    char* filespec;
    char* flag;

    if(argv[1][0] == '-'){  //first arg is flag
        flag = argv[1];
        filespec = argv[2];
    }
    else{                   //second arg is flag
        flag = argv[2];
        filespec = argv[1];
    }


    std::string currline;
    std::ifstream fileReader;
    fileReader.open(filespec);

    while(getline(fileReader, currline)){
        file += currline + '\n';
    }
    fileReader.close();
    fileSize = file.size();

    if(!strcmp(flag, "-l")){
        /*
            Perform lexical analysis only, printing the tokens to stdout. 
            In this case, the compilation is considered to be successful if the input file contains 
            only the lexemes described in this spec; otherwise, the compilation fails
        */

        try{    
            std::vector<token> tokens = lexer();
        }
        catch(LexerException lexep){
            cout << "Compilation failed" << endl;
        }

        std::vector<token>::iterator ptr;

        for(ptr = tokens.begin(); ptr < tokens.end(); ptr++){
            std::cout << ptr->t << " \'" << ptr->text << "\'\n";
        }

       
    }
    else if (!strcmp(flag, "-p")){
        /*
            Perform lexical analysis and parsing only, pretty-printing the parsed program back to ASCII 
            text in a format based on s-expressions that is described in your assignments. In this case, 
            the compilation is considered to be successful if the input program corresponds to the grammar
             described in your current assignment; otherwise, the compilation fails.
        */
    }
    else if (!strcmp(flag, "-t"))
    {
        /*
            Perform lexical analysis, parsing, and type checking (but not code generation). 
            In this case, the compilation is considered to be successful if the input program is fully 
            legal JPL; otherwise the compilation fails.
        */
    }
    else{
        //terse error message
    }


    // file.open(filespec);

    
    
}
