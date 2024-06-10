#ifndef _PARSE_
#define _PARSE_

#include <string>
#include <vector>
#include <iostream>

#include "../include/lexer.h"

namespace Parse
{   
    class ASTNode {
        public:
            virtual std::string to_string();
    };

    class cmd : public ASTNode {};

    class ReadCmd : public cmd {};
    class WriteCmd : public cmd {};
    class TypeCmd : public cmd {};
    class LetCmd : public cmd {};
    class AssertCmd : public cmd {};
    class PrintCmd : public cmd {};
    class ShowCmd : public cmd {};


    class Type : public ASTNode {};

    class IntType : public Type {};
    class FloatType : public Type {};
    class BoolType : public Type {};
    class VarType : public Type {};


    class Expr : public ASTNode {};

    class IntExpr : public Expr {};
    class FloatExpr : public Expr {};
    class VarExpr : public Expr {};
    class TrueExpr : public Expr {};
    class FalseExpr : public Expr {};


    class Argument : public ASTNode {};

    class VarArgument : public Argument {};
    class ArgLValue : public Argument {}; // TODO: move to LValue class?



    class Parser {
        private:
            std::vector<std::unique_ptr<ASTNode>> astTree;
            std::vector<std::unique_ptr<Lex::Token>> tokens;

            std::string expectToken(int *, Lex::Tokty);
        public:
            Parser(std::vector<std::unique_ptr<Lex::Token>>);

            void doParse();
            void prettyPrint();
    };

    class ParseException : public std::exception {
        using std::exception::what;
        private:
            const char *message;
        public:
            ParseException(const char*);
            virtual const char* what();
    };
    
} // namespace Parse

#endif