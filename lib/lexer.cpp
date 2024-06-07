#include "../include/lexer.h"
#include <iostream>
#include <fstream>
#include <sstream>
#include <regex>
using namespace std;
using namespace Lex;

// Token(Tokty tok, int loc, string txt) {
//     tokty = tok;
//     loc = loc;
//     text = txt;
// }




Token::Token(Lex::Tokty tokty, int loc, std::string text):
    tokty(tokty), loc(loc), text(text) {}

Token::Token() = default;
Token::~Token() = default;

Lexer::Lexer(string filename) {
    std::ifstream f(filename);
    std::stringstream buf;
    buf << f.rdbuf();
    file = buf.str();
    fsize = file.length();
    //tokens.push_back(make_unique<Token>(ARRAY, -1, "e"));
    cout << "made it" << endl;
}

int Lexer::goUntil(int pos, char end) {
    while(file[pos] != end) {
        if (pos == fsize-1 || !(file[pos] >= 32 && file[pos] <= 126)) {
            return -1;
        }
        pos++;
    }
    return pos-1; // -1?
}

int Lexer::lexWhiteSpc(int pos) {
    bool hasNL = 0;
    
    while(pos < fsize) {
        if (file[pos] == ' '){
            pos++;
        } else if (file[pos] == '/') {
            if (file[pos+1] == '/'){
                int res = goUntil(pos, '\n');
                if (res != -1) {pos += res;}
                if (!hasNL) {
                    hasNL = 1;
                    tokens.push_back(make_unique<Token>(NEWLINE, pos, "NEWLINE"));
                }
                pos++;
            } else if (file[pos+1] == '*') {
                pos += 2;
                while (pos < fsize) {
                    if (pos == fsize-1) {
                        return -1;
                    } 
                    if (file[pos] == '*' && file[pos+1] == '/'){
                        if (!hasNL) {
                            hasNL = 1;
                            tokens.push_back(make_unique<Token>(NEWLINE, pos, "NEWLINE"));
                        }
                        pos++;
                        break;
                    }
                    pos++;
                }
                pos += 2;
            } else {
                break;
            }
        } else if (file[pos] == '\\') {
            hasNL = 1;
            pos++;
        } else if (file[pos] == '\n') {
            if (!hasNL) {
                hasNL = 1;
                tokens.push_back(make_unique<Token>(NEWLINE, pos, "NEWLINE"));
            }
            pos++;
        } else if (pos == fsize-1) {
            tokens.push_back(make_unique<Token>(END_OF_FILE, pos, "END_OF_FILE"));
        } else {
            break;
        }
    }
    return pos;

}



std::tuple<std::unique_ptr<Lex::Token>, int> Lexer::lexItem(int pos) {
    smatch match;
    const string &curr = file.substr(pos);

    regex fl("(^[0-9]+\\.[0-9]*)|(^[0-9]*\\.[0-9]+)");
    regex nt("^[0-9]+");
    regex word("^[a-zA-Z]+[a-zA-Z0-9_\\.]*");
    regex op("^((&&)|(\\|\\|)|(<=)|(>=)|(<)|(>)|(==)|(!=)|(\\+)|(-)|(\\*)|(/)|(%)|(!))");
    regex st("^\"[ -~]*\"$");
    regex punct("[\\:\\{\\}\\(\\)\\[\\],=]");

    if (regex_search(curr.begin(), curr.end(), match, fl)) {
        return make_tuple(make_unique<Token>(FLOATVAL, pos, match[0]), match[0].length());
    } else if (regex_search(curr.begin(), curr.end(), match, nt)) {
        return make_tuple(make_unique<Token>(INTVAL, pos, match[0]), match[0].length());
    } else if (regex_search(curr.begin(), curr.end(), match, word)) {
        Tokty t = strToTokty(match[0]); //TODO: ???
        if (t == OP_OR_VAR) {
            t = VARIABLE;
        }
        return make_tuple(make_unique<Token>(t, pos, match[0]), match[0].length());
    } else if (regex_search(curr.begin(), curr.end(), match, op)) {
        return make_tuple(make_unique<Token>(OP, pos, match[0]), match[0].length());
    } else if (regex_search(curr.begin(), curr.end(), match, punct)) {
        return make_tuple(make_unique<Token>(strToTokty(match[0]), pos, match[0]), match[0].length());        
    } else if (regex_search(curr.begin(), curr.end(), match, st)) {
        return make_tuple(make_unique<Token>(STRING, pos, match[0]), match[0].length());
    }
    return make_tuple(make_unique<Token>(Token()), -1);
}



std::tuple<std::unique_ptr<Lex::Token>, int> Lexer::lexVar(int pos) {
    regex word("^[a-zA-Z]+[a-zA-Z0-9_\\.]*");
    smatch match;
    const string &curr = file.substr(pos);
    if (regex_search(curr.begin(), curr.end(), match, word)) {
        Tokty t = strToTokty(match[0]);
        if (t == OP_OR_VAR) {
            t = VARIABLE;
        } 
        return make_tuple(make_unique<Token>(t, pos, match[0]), match[0].length());
    }
    return make_tuple(make_unique<Token>(Token()), -1);
}


std::tuple<std::unique_ptr<Lex::Token>, int> Lexer::lexPunct(int pos) {
    regex punct("[\\:\\{\\}\\(\\)\\[\\],=]");
    smatch match;
    const string &curr = file.substr(pos);
    if (regex_search(curr.begin(), curr.end(), match, punct)) {
        return make_tuple(make_unique<Token>(strToTokty(match[0]), pos, match[0]), match[0].length());
    }
    return make_tuple(make_unique<Token>(Token()), -1);
}

// std::tuple<std::unique_ptr<Lex::Token>, int> Lexer::lexKeyword(int pos) {
//     regex keyword("^((array)|(assert)|(bool)|(else)|(false)|(float)|(fn)|(if)|(image)|(int)' \
//                       '|(let)|(print)|(read)|(return)|(show)|(sum)|(then)|(time)|(to)|(true)|(type)|(write))");
//     smatch match;
//     const string &curr = file.substr(pos);
//     if (regex_search(curr.begin(), curr.end(), match, keyword)) {
//         return make_tuple(make_unique<Token>(strToTokty(match[0]), pos, match[0]), match[0].length());
//     }
//     return make_tuple(make_unique<Token>(Token()), -1);
// }

std::tuple<std::unique_ptr<Lex::Token>, int> Lexer::lexNum(int pos) {
    regex fl("(^[0-9]+\\.[0-9]*)|(^[0-9]*\\.[0-9]+)");
    regex nt("^[0-9]+");
    smatch match;
    const string &curr = file.substr(pos);
    if (regex_search(curr.begin(), curr.end(), match, fl)) {
        return make_tuple(make_unique<Token>(FLOATVAL, pos, match[0]), match[0].length());
    } else if (regex_search(curr.begin(), curr.end(), match, nt)) {
        return make_tuple(make_unique<Token>(INTVAL, pos, match[0]), match[0].length());
    } 
    return make_tuple(make_unique<Token>(Token()), -1);
}

