#ifndef _LEX_

#define _LEX_

#include <string>
#include <vector>
#include <tuple>
#include <unordered_map>
namespace Lex
{
    enum Tokty{
        ARRAY, 
        ASSERT, 
        BOOL, 
        ELSE,
        FALSE, 
        FLOAT, 
        FN, 
        IF, 
        IMAGE, 
        INT, 
        LET, 
        PRINT,
        READ, 
        RETURN, 
        SHOW, 
        SUM, 
        THEN, 
        TIME, 
        TO, 
        TRUE, 
        TYPE, 
        WRITE,
        COLON, 
        LCURLY, 
        RCURLY, 
        LPAREN, 
        RPAREN, 
        COMMA, 
        LSQUARE, 
        RSQUARE, 
        EQUALS,
        STRING, 
        INTVAL, 
        FLOATVAL, 
        VARIABLE, 
        OP, 
        NEWLINE, 
        END_OF_FILE,
        OP_OR_VAR
    };

    static std::unordered_map<std::string, Tokty> const tbl = {
        {"array", ARRAY}, {"assert", ASSERT}, {"bool", BOOL}, {"else", ELSE},
        {"false", FALSE}, {"float", FLOAT}, {"fn", FN}, {"if", IF}, {"image", IMAGE},
        {"int", INT}, {"let", LET}, {"print", PRINT}, {"read", READ}, {"return", RETURN},
        {"show", SHOW}, {"sum", SUM}, {"then", THEN}, {"to", TO}, {"true", TRUE},
        {"type", TYPE}, {"write", WRITE}, {":", COLON}, {"{", LCURLY}, {"}", RCURLY},
        {"(", LPAREN}, {")", RPAREN}, {",", COMMA}, {"[", LSQUARE}, {"]", RSQUARE},
        {"=", EQUALS}, {"string", STRING}, {"intval", INTVAL}, {"floatval", FLOATVAL},
        {"var", VARIABLE}, {"op", OP}, {"read", READ}, {"\n", NEWLINE}, {"eof", END_OF_FILE}
    };

    inline Tokty strToTokty(std::string match){
        auto it = tbl.find(match);
        if (it == tbl.end()) {
            return OP_OR_VAR;
        }
        return it->second;
    }

    class Token{
        public:
            Lex::Tokty tokty;
            int row;
            int col;
            int loc;
            std::string text;

            //Token(Lex::Tokty tok, int loc, std::string txt);
            Token(Lex::Tokty tokty, int loc, std::string text);
            Token();
            ~Token();

    };

    class Lexer {
        public:
            std::string file;
            int fsize;
            std::vector<std::unique_ptr<Lex::Token>> tokens;

            Lexer(std::string);

            std::tuple<std::unique_ptr<Lex::Token>, int> lexNum(int);
            // std::tuple<std::unique_ptr<Lex::Token>, int> lexKeyword(int);
            std::tuple<std::unique_ptr<Lex::Token>, int> lexPunct(int);
            std::tuple<std::unique_ptr<Lex::Token>, int> lexVar(int);
            std::tuple<std::unique_ptr<Lex::Token>, int> lexItem(int);
            int lexWhiteSpc(int);
            int goUntil(int, char);

            void doLex();
    };      



} // namespace Lex


#endif