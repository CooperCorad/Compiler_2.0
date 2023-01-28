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
                // index++;
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

// cmd  : read image <string> to <argument>
//      | write image <expr> to <string>
//      | type <variable> = <type>
//      | let <lvalue> = <expr>
//      | assert <expr> , <string>
//      | print <string>
//      | show <expr>

// type : int
//      | bool
//      | float
//      | <variable>

// expr : <integer>
//      | <float>
//      | true
//      | false
//      | <variable>

// argument : <variable>

// lvalue : <argument>

class ASTNode {
    public:
        virtual string to_String(){
            return "";
        }
};

class Variable : public ASTNode {
    public:
        string variable;

        Variable(string inStr){
            variable = inStr;
        }

        virtual string to_String(){
            return variable;
        }

};

class Argument : public ASTNode {};

    // <variable>
    class VarArg : public Argument {
        public:
            unique_ptr<Variable> variable;

            VarArg(unique_ptr<Variable> inVariable){
                variable = move(inVariable);
            }

            virtual string to_String(){
                return "(VarArgument " + variable->to_String() + ")";
            }

    }; 

    // <variable>
    class ArgLValue : public Argument {
        public:
            unique_ptr<Variable> variable;

            ArgLValue(unique_ptr<Variable> inVariable){
                variable = move(inVariable);
            }

            virtual string to_String(){
                return "(ArgLValue " + variable->to_String() + ")";
            }
    };


// expr : <integer>
//      | <float>
//      | true
//      | false
//      | <variable>
class Expr : public ASTNode {};

    // int
    class IntExpr : public Expr {
        public:
            long int intVal;
            string intStr;

            IntExpr(string inInt){
                intStr = inInt;
                intVal = strtol(inInt.c_str(), nullptr, 10);
            }

            virtual string to_String(){
                return "(IntExpr " + intStr + ")";
            }

    };

    // float
    class FloatExpr : public Expr {
        public:
            double floatVal;
            string floatStr;

            FloatExpr(string inFloat){
                floatStr = inFloat;
                floatVal = strtod(inFloat.c_str(), nullptr);
            }

            virtual string to_String(){
                string res = "";
                int i = 0;
                while(floatStr[i] != '.'){
                    res += floatStr[i];
                }
                return "(FloatExpr " + res + ")";  //TODO later cut off '.'
            }

    };

    // true
    class TrueExpr : public Expr {
        public:
            virtual string to_String(){
                return "(TrueExpr)";
            }
    };

    // false
    class FalseExpr : public Expr {
        public:
            virtual string to_String(){
                return "(FalseExpr)";
            }
    };

    // <vairable>
    class VariableExpr : public Expr {
        public:
            unique_ptr<Variable> variable;

            VariableExpr(unique_ptr<Variable> inVariable){
                variable = move(inVariable);
            }

            virtual string to_String(){
                return "(VarExpr " + variable->to_String() + ")";
            }

    };

// type : int
//      | bool
//      | float
//      | <variable>
class Type : public ASTNode {
    public:
        virtual string to_String(){
                return "";
        }
};

    // int
    class IntType : public Type {
        public:
            virtual string to_String(){
                return "(IntType)";
            }
    };

    // bool
    class BoolType : public Type {
        public:
            virtual string to_String(){
                return "(BoolType)";
            }
    };

    // float
    class FloatType : public Type {
        public:
            virtual string to_String(){
                return "(FloatType)";
            }
    };

    // <variable>
    class VarType : public Type {
        public:
            unique_ptr<Variable> variable;

            VarType(unique_ptr<Variable> inVariable){
                variable = move(inVariable);
            }

            virtual string to_String(){
                return "(VarType " + variable->to_String() + ")";
            }
    }; 

// cmd  : read image <string> to <argument>
//      | write image <expr> to <string>
//      | type <variable> = <type>
//      | let <lvalue> = <expr>
//      | assert <expr> , <string>
//      | print <string>
//      | show <expr>

class Cmd : public ASTNode {
    public:
        virtual string to_String(){
                return "";
        }
};

    // read image <string> to <argument>
    class ReadCmd : public Cmd {
        public:
            string str;
            unique_ptr<VarArg> argument;

            ReadCmd(string inStr, unique_ptr<VarArg> inVarArg){
                str = inStr;
                argument = move(inVarArg);
            }

            virtual string to_String(){
                return "(ReadCmd " + str + " " + argument->to_String() + ")";
            }
    };

    // write image <expr> to <string>
    class WriteCmd : public Cmd {
        public:
            unique_ptr<Expr> expression;
            string str;

            WriteCmd(unique_ptr<Expr> inExpression, string inStr){
                expression = move(inExpression);
                str = inStr;
            }

            virtual string to_String(){
                return "(WriteCmd " + expression->to_String() + " " + str + ")";
            }
    };

    // type <variable> = <type>
    class TypeCmd : public Cmd {
        public:
            unique_ptr<Variable> variable;
            unique_ptr<Type> type;

            TypeCmd(unique_ptr<Variable> inVariable, unique_ptr<Type> inType){
                variable = move(inVariable);
                type = move(inType);
            }

            virtual string to_String(){
                return "(TypeCmd " + variable->to_String() + " " + type->to_String() + ")";
            }
    };

    // let <lvalue> = <expr>
    class LetCmd : public Cmd {
        public:
            unique_ptr<ArgLValue> lvalue;
            unique_ptr<Expr> expr;

            LetCmd(unique_ptr<ArgLValue> inLValue, unique_ptr<Expr> inExpr){
                lvalue = move(inLValue);
                expr = move(inExpr);
            }

            virtual string to_String(){
                return "(LetCmd " + lvalue->to_String() + " " + expr->to_String() + ")";
            }
    };

    // assert <expr> , <string>
    class AssertCmd : public Cmd {
        public:
            unique_ptr<Expr> expr;
            string str;

            AssertCmd(unique_ptr<Expr> inExper, string inStr){
                expr = move(inExper);
                str = inStr;
            }

            virtual string to_String(){
                return "(AssertCmd " + expr->to_String() + " " + str + ")";
            }
    };

    // print <string>
    class PrintCmd : public Cmd {
        public:
            string str;

            PrintCmd(string inStr){
                str = inStr;
            }

            virtual string to_String(){
                return "(PrintCmd " + str + ")";
            }
    };

    // show <expr>
    class ShowCmd : public Cmd {
        public:
            unique_ptr<Expr> expr;

            ShowCmd(unique_ptr<Expr> inExpr){
                expr = move(inExpr);
            }

            virtual string to_String(){
                return "(ShowCmd " + expr->to_String() + ")";
            }
    };
    

class Parser {
    public:
        vector<token> tokens;
        vector<ASTNode> nodes;
        vector<Cmd> program;

        Parser(vector<token> toks){
            tokens = toks;
        }

        vector<Cmd> parse(){
            int index = 0;

            while(true) {    
                switch (peek_tok(index)) {
                    case tokType::END_OF_FILE:
                        return program;
                        break;
                    
                    default:
                        pair<Cmd, int> p = parse_Cmd(index);
                        Cmd cmd = p.first;
                        index = p.second;
                        expect_tok(index++, tokType::NEWLINE);
                        program.push_back(cmd);
                        break;
                }
            }


        }

    private:
        tokType peek_tok(int index){
            return tokens[index].t;
        }

        string expect_tok(int index, tokType expected){
            if(tokens[index].t != expected){
                throw ParserException(makeError("the expected token could not be found at ", index));
            }
            return tokens[index].text;

        }



        /*
        cmd  ~: read image <string> to <argument>
            ~| write image <expr> to <string>
            ~| type <variable> = <type>
            ~| let <lvalue> = <expr>
            ~| assert <expr> , <string>
            ~| print <string>
            ~| show <expr>
        */
        pair<Cmd, int> parse_Cmd(int index){
            tokType command = peek_tok(index);
            pair<Cmd, int> ret;
            switch(command){
                case tokType::READ:
                    ret = parse_ReadCmd(index);
                    break;
                // case tokType::WRITE:
                //     ret = parse_WriteCmd(index);
                //     break;
                // case tokType::TYPE:
                //     ret = parse_TypeCmd(index);
                //     break;
                // case tokType::LET:
                //     ret = parse_LetCmd(index);
                //     break;
                // case tokType::ASSERT:
                //     ret = parse_AssertCmd(index);
                //     break;
                // case tokType::PRINT:
                //     ret = parse_PrintCmd(index);
                //     break;
                // case tokType::SHOW:
                //     ret = parse_ShowCmd(index);
                //     break;
                default:
                    throw ParserException("Not a command!");
                
            }
            return ret;
        }
        // read image <string> to <argument>
        pair<ReadCmd, int> parse_ReadCmd(int index){
            expect_tok(index++, tokType::READ); // read
            expect_tok(index++, tokType::IMAGE);    // image
            //<string>
            string filename = expect_tok(index++, tokType::STRING);
            expect_tok(index++, tokType::TO);   // to

            pair<Variable, int> result = parse_Argument(index);
            unique_ptr<Variable> varptr = make_unique<Variable>(result.first);
            unique_ptr<VarArg> varargptr = make_unique<VarArg>(VarArg(move(varptr)));   //<argument>

            ReadCmd readcmd(filename, move(varargptr));

            pair<ReadCmd, int> ret = make_pair(readcmd, result.second);

            return ret;

            
        }
        // // write image <expr> to <string>
        // pair<Cmd, int> parse_WriteCmd(int index){
        //     expect_tok(index++, tokType::WRITE);
        //     expect_tok(index++, tokType::IMAGE);
        //     pair<Expr,int> res = parse_expr(index);
        //     Expr image = res.first;
        //     index = res.second;
        //     string filename = expect_tok(index++, tokType::STRING);
        //     // return pair<writecmd
        // }

        // // type <variable> = <type>
        // pair<Cmd, int> parse_TypeCmd(int index){
        //     expect_tok(index++, tokType::LET);
        //     return make_pair(Cmd(), index); //TODO finish
        // }

        // // let <lvalue> = <expr>
        // pair<Cmd, int> parse_LetCmd(int index){
        //     return make_pair(Cmd(), index);
        // }

        // // assert <expr> , <string>
        // pair<Cmd, int> parse_AssertCmd(int index){
        //     expect_tok(index++, tokType::ASSERT);
        //     pair<Expr, int> res = parse_expr(index);
        //     Expr assertion = res.first;
        //     index = res.second;
        //     expect_tok(index++, tokType::COMMA);
        //     string str = expect_tok(index++, tokType::STRING);
        //     return make_pair(AssertCmd(assertion, str), index);
        // }

        // // print <string>
        // pair<Cmd, int> parse_PrintCmd(int index){
        //     expect_tok(index++, tokType::PRINT);
        //     string str = expect_tok(index++, tokType::STRING);
        //     return make_pair(PrintCmd(str), index);
        // }

        // // show <expr>
        // pair<Cmd, int> parse_ShowCmd(int index){
        //     expect_tok(index++, tokType::SHOW);
        //     pair<Expr, int> res = parse_expr(index);
        //     Expr expr = res.first;
        //     index = res.second;
        //     return make_pair(ShowCmd(expr), index);
        // }



        /*
            expr : <integer>
                 | <float>
                 | true
                 | false
                 | <variable>
        */
        // pair<Expr, int> parse_expr(int index){
        //     tokType tok = peek_tok(index);
        //     switch (tok)
        //     {
        //     case tokType::INTVAL:  //TODO inval or int?
        //         return parse_IntExpr(index);
        //         break;
            
        //     case tokType::FLOATVAL:
        //         return parse_FloatExpr(index);
        //         break;
            
        //     default:    //TODO in future pull the token place in the prog, not the list we made
        //         throw ParserException(makeError("Unable to parse expression at: ", index));
        //         break;
        //     }

        // }

        // pair<IntExpr, int> parse_IntExpr(int index){
        //     const char* intVal = expect_tok(index++, tokType::INTVAL).c_str(); 
        //     int64_t intParsed = strtol(intVal, nullptr, 10);
        //     return make_pair(IntExpr(intParsed) , index);
        // }

        // pair<FloatExpr, int> parse_FloatExpr(int index){
        //     const char* floatVal = expect_tok(index++, tokType::FLOATVAL).c_str();
        //     double floatParsed = strtod(floatVal, nullptr);
        //     return make_pair(FloatExpr(floatParsed), index);
        // }

        // argument : <variable>
        pair<Variable, int> parse_Argument(int index){
            Variable ret(expect_tok(index++, tokType::VARIABLE));
            return make_pair(ret, index);
        }
};


//// PARSER END


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

    if(flag != NULL){
        if(!strcmp(flag, "-l")){
            /*
                Perform lexical analysis only, printing the tokens to stdout. 
                In this case, the compilation is considered to be successful if the input file contains 
                only the lexemes described in this spec; otherwise, the compilation fails
            */

                
            Lexer lexer(filespec);
            lexer.to_string(); 
            
            
            
            
            
        }
        else if (!strcmp(flag, "-p")){
            /*
                Perform lexical analysis and parsing only, pretty-printing the parsed program back to ASCII 
                text in a format based on s-expressions that is described in your assignments. In this case, 
                the compilation is considered to be successful if the input program corresponds to the grammar
                described in your current assignment; otherwise, the compilation fails.
            */

            Lexer lexer(filespec);
            Parser parser(lexer.tokens);
            

        }
        else if (!strcmp(flag, "-t"))
        {
            /*
                Perform lexical analysis, parsing, and type checking (but not code generation). 
                In this case, the compilation is considered to be successful if the input program is fully 
                legal JPL; otherwise the compilation fails.
            */
        }
    }
    else{
        cout << "A flag is required" << endl;
        exit(0);
    }



    // file.open(filespec);

    
    
}
