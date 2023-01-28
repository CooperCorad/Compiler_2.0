#include <iostream>
#include <string.h>
#include <vector>
#include <map>
#include <regex>
#include <iostream>
#include <fstream>
#include <charconv>
#include <math.h>
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

class ParserException : public exception {
    private:
        const char* message;

    public:
        ParserException(const char* msg) : message(msg) {}
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

map<string, tokType> stringToTok = { { "array", tokType::ARRAY }, { "assert", tokType::ASSERT },
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
  string text;
};

const char* makeError(string msg, int index){
    string temp = to_string(index);
    msg += temp;
    const char* ret = msg.c_str();

    return ret;
}

class Lexer{
    public:
        vector<token> tokens;
        string file;
        int fileSize; 

        Lexer(char* filespec){
            string currline;
            ifstream fileReader;
            fileReader.open(filespec);

            while(!fileReader.eof()){
                getline(fileReader, currline);
                file += currline + '\n';
            }
            fileReader.close();
            file.pop_back();
            fileSize = file.size();
            int index;

            try{
                index = lexWhiteSpace(0);
            }
            catch(LexerException lexep){
                    // cout << "Compilation failed " << lexep.what() << endl;
                    cout << "Compilation failed" << endl;
                    exit(0);
            } 
            while (index < fileSize){
                try{
                    pair<token, int> info = tryLex(index);
                    tokens.push_back(info.first);
                    index = lexWhiteSpace(info.second);
                }
                catch(LexerException lexep){
                    // cout << "Compilation failed " << lexep.what() << endl;
                    cout << "Compilation failed" << endl;
                    exit(0);
                }   
            }
            
            if(tokens.size() > 0 && tokens.back().t != tokType::END_OF_FILE){
                tokens.push_back(token{tokType::END_OF_FILE, index, "EOF"});
            }
        }

        void to_string(){
            vector<token>::iterator ptr;

            for(ptr = tokens.begin(); ptr < tokens.end(); ptr++){
                if(ptr->t == tokType::NEWLINE){

                    cout << "NEWLINE" << endl;
                } 
                else if(ptr->t == tokType::END_OF_FILE){
                    cout << "END_OF_FILE" << endl;
                }
                else{
                    string tok = "def";
                    
                    switch(ptr->t){
                        case 0:
                            tok = "ARRAY";
                            break;
                        case 1:
                            tok = "ASSERT";
                            break;
                        case 2:
                            tok = "BOOL";
                            break;
                        case 3:
                            tok = "ELSE";
                            break;
                        case 4:
                            tok = "FALSE";
                            break;
                        case 5:
                            tok = "FLOAT";
                            break;
                        case 6:
                            tok = "FN";
                            break;
                        case 7:
                            tok = "IF";
                            break;
                        case 8:
                            tok = "IMAGE";
                            break;
                        case 9:
                            tok = "INT";
                            break;
                        case 10:
                            tok = "LET";
                            break;
                        case 11:
                            tok = "PRINT";
                            break;
                        case 12:
                            tok = "READ";
                            break;
                        case 13:
                            tok = "RETURN";
                            break;
                        case 14:
                            tok = "SHOW";
                            break;
                        case 15:
                            tok = "SUM";
                            break;
                        case 16:
                            tok = "THEN";
                            break;
                        case 17:
                            tok = "TIME";
                            break;
                        case 18:
                            tok = "TO";
                            break;
                        case 19:
                            tok = "TRUE";
                            break;
                        case 20:
                            tok = "TYPE";
                            break;
                        case 21:
                            tok = "WRITE";
                            break;
                        case 22:
                            tok = "COLON";
                            break;
                        case 23:
                            tok = "LCURLY";
                            break;
                        case 24:
                            tok = "RCURLY";
                            break;
                        case 25:
                            tok = "LPAREN";
                            break;
                        case 26:
                            tok = "RPAREN";
                            break;
                        case 27:
                            tok = "COMMA";
                            break;
                        case 28:
                            tok = "LSQUARE";
                            break;
                        case 29:
                            tok = "RSQUARE";
                            break;
                        case 30:
                            tok = "EQUALS";
                            break;
                        case 31:
                            tok = "STRING";
                            break;
                        case 32:
                            tok = "INTVAL";
                            break;
                        case 33:
                            tok = "FLOATVAL";
                            break;
                        case 34:
                            tok = "VARIABLE";
                            break;
                        case 35:
                            tok = "OP";
                            break;
                        case 36: 
                            tok = "NEWLINE";
                            break;
                        case 37:
                            tok = "END_OF_FILE";
                            break;
                        
                    }

                    cout << tok << " \'" << ptr->text << "\'" << endl;
                }
            }
            cout << "Compilation succeeded: lexical analysis complete" << endl;
        
        }

    private:
        int lexWhiteSpace(int index){

            bool hasNL = false;

            while(index < fileSize){

                if(file[index] == ' '){
                    index++;
                }
                else if(file[index] == '/'){
                    if(file[index + 1] == '/'){
                        while(file[index] != '\n' && index < fileSize){
                            index++;
                        }
                        if(!hasNL){
                            hasNL = true;
                            tokens.push_back(token{tokType::NEWLINE, index, "\n"});
                        }
                        index++;
                    }
                    else if(file[index + 1] == '*'){
                        index += 2;
                        while(index < fileSize){
                            if(index == fileSize -1){
                                throw(LexerException("No end to the multiline comment!"));
                            }
                            if(file[index] == '*' && file[index + 1] == '/'){
                                if(!hasNL){
                                    hasNL = true;
                                    tokens.push_back(token{tokType::NEWLINE, index, "\n"});
                                }
                                index++;
                                break;
                            }
                            index++;
                        }
                        index += 2;

                    }
                    else{
                        break;
                    }
                }
                else if(file[index] == '\\' && file[index] != '\n'){
                    hasNL = true;
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
            }
            return index;
        }

        pair<token, int> lexPunct(int index){
            int originalI = index;
            regex regPUNCT ("^[\\:\\{\\}\\(\\)\\[\\],=]");
            smatch PUNCTMatch;
            string sub = file.substr(index);

            regex_search(sub, PUNCTMatch, regPUNCT);
            string tokStr = PUNCTMatch[0];
            int newIndex = index + tokStr.size();


            if(tokStr.size() == 0){
                throw LexerException(makeError((char*)"unable to find punctuation at ", originalI));
            }
            return make_pair(token{stringToTok[tokStr], newIndex, tokStr}, newIndex);
        }


        pair<token, int> lexSTR(int index){
            int originalI = index;
            string tokStr = "";
            if (file[index] != '\"'){
                throw LexerException(makeError((char*)"unable to find a string at: ", originalI));

            }
            else{
                tokStr += '"';
                index++;
            }
            if(file[index] == '\n'){
                throw LexerException("Cannot have an escape characrer in your string!");
            }
            while((file[index] >= 32 && file[index] <= 126) && file[index] != '\"' && index < fileSize){
                if(file[index] == '\n'){
                    throw LexerException("Cannot have an escape characrer in your string!");
                }

                tokStr += file[index];
                index++;
            } 
            if(index == fileSize){
                throw LexerException("Lexing failed! Reached end of file without string termination");
            }

            tokStr += '"';
            index++;
            return make_pair(token{tokType::STRING, index, tokStr}, index);

        }

        pair<token, int> lexVAR(int index){
            int originalI = index;
            regex regVAR("^[A-Za-z]+[A-Za-z0-9_\\.]*");
            regex regKeyword("^((array)|(assert)|(bool)|(else)|(false)|(float)|(fn)|(if)|(image)|(int)|(let)|(print)|(read)|(return)|(show)|(sum)|(then)|(time)|(to)|(true)|(type)|(write))");
            string sub = file.substr(index);
            smatch VARmatch;

            regex_search(sub, VARmatch, regVAR);

            if(!string(VARmatch[0]).size()){
                throw LexerException(makeError((char*)"unable to find a variable at: ", originalI));
            }

            string tokStr = string(VARmatch[0]);
            int newindex = (int) tokStr.size() + index;

            if(regex_match(tokStr, regKeyword)){
                return make_pair(token{stringToTok[tokStr], newindex, tokStr}, newindex);
            }

            return make_pair(token{tokType::VARIABLE, newindex, tokStr}, newindex);

        }

        pair<token, int> lexOP(int index){
            int originalI = index;
            regex regOP("^((&&)|(\\|\\|)|(<=)|(>=)|(<)|(>)|(==)|(!=)|(\\+)|(-)|(\\*)|(/)|(%)|(!))");
            string sub = file.substr(index);
            smatch OPmatch;

            // if(file[index] == '/'){
            //     // cout << "\n\n*** found /! ***\n\n" << endl;
            // }

            regex_search(sub, OPmatch, regOP);
            string tokStr = string(OPmatch[0]);    
            int newIndex = index + (int)tokStr.size();

            if(!string(OPmatch[0]).size()){
                throw LexerException(makeError((char*)"unable to find a operator at: ", originalI));
            }
            return make_pair(token{tokType::OP, newIndex, tokStr}, newIndex);

        }

        pair<token, int> lexKeyWord(int index){
            int originalI = index;
            regex regKeyword("^((array)|(assert)|(bool)|(else)|(false)|(float)|(fn)|(if)|(image)|(int)|(let)|(print)|(read)|(return)|(show)|(sum)|(then)|(time)|(to)|(true)|(type)|(write))");
            smatch keywordmatch;
            string sub = file.substr(index);

            regex_search(sub, keywordmatch, regKeyword);
            string tokStr = string(keywordmatch[0]);
            int newIndex = index + (int)tokStr.size();

            if(tokStr.size() == 0){ 
                throw LexerException(makeError((char*)"unable to find a keyword at: ", originalI));
            }


            return make_pair(token{stringToTok[tokStr], newIndex, tokStr}, newIndex);

        }

        pair<token, int> lexNum(int index){
            int originalI = index;
            regex regFloat ("(^[0-9]+\\.[0-9]*)|(^[0-9]*\\.[0-9]+)");
            regex regInt ("^[0-9]+");
            smatch floatMatch;
            smatch intMatch;
            string sub = file.substr(index);

            regex_search(sub, floatMatch, regFloat);
            regex_search(sub, intMatch, regInt);
            string floatStr = string(floatMatch[0]);
            string intStr = string(intMatch[0]);

            if(floatStr.size() == 0 && intStr.size() == 0){
                throw LexerException(makeError((char*)"Unable to find a number at ", originalI));
            }
            else if(string(floatMatch[0]).size()){ 
                string tokstr = string(floatMatch[0]);
                int newIndex = (int)tokstr.size() + index;
                return make_pair(token{tokType::FLOATVAL, newIndex, tokstr}, newIndex);
            }

            string tokstr = string(intMatch[0]);
            int newIndex = (int)tokstr.size() + index;
            return make_pair(token{tokType::INTVAL, newIndex, tokstr}, newIndex);
            
        }


        pair<token, int> tryLex(int index){
            pair<token, int> ret;
            try{
                // cout << "num" << endl;
                ret = lexNum(index);
            }
            catch(LexerException lexep){
                    try{
                        // cout << "keyword" << endl;
                        ret = lexVAR(index);
                    }
                    catch(LexerException lexep){
                            try{
                                // cout << "VAR" << endl;
                                ret = lexKeyWord(index);
                            }
                            catch(LexerException lexep){
                                    try{
                                        // cout << "OP" << endl;
                                        ret = lexOP(index);
                                    }
                                    catch(LexerException lexep){
                                        try{
                                            // cout << "punct" << endl;
                                            ret = lexPunct(index);
                                        }
                                        catch(LexerException lexep){
                                                try{
                                                    // cout << "string" << endl;
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

        


};



