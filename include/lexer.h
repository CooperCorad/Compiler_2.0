#include <string>
namespace Lex
{
    enum Tokty{ARRAY, 
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
        END_OF_FILE};

    class Token{
        public:
            Lex::Tokty tokty;
            int row;
            int col;
            int loc;
            std::string text;

            Token(Lex::Tokty tok, int loc, std::string txt);
    };
 
} // namespace Lex
