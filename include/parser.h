#ifndef _PARSE_
#define _PARSE_

#include <string>
#include <vector>
#include <iostream>
#include <regex>

#include "../include/lexer.h"

/*
    TODO:   1. see if lvl6/cont necessary?
            2. change all class containers of pts from 
                unique_ptr -> shared_ptr 
                for the sake of type checking l8r

*/


namespace Parse
{   
    class ParseException : public std::exception {
        using std::exception::what;
        private:
            std::string message;
        public:
            ParseException(std::string);
            std::string what();
    };

    class ASTNode {
        public:
            ASTNode() = default;
            virtual std::string to_string() { return ""; };
            virtual ~ASTNode() = default;
    };


    class Variable : public ASTNode {
        public:
            std::string name;
            Variable(std::string name) : name(name) {}
            ~Variable() override = default;
            std::string to_string() override { return name; }
    };


    class Argument : public ASTNode {};

    class VarArgument : public Argument {
        public:
            std::unique_ptr<Variable> variable;
            VarArgument(std::unique_ptr<Variable> variable) :
                variable(std::move(variable)) {}
            ~VarArgument() override = default;
            std::string to_string() override {
                return "(VarArgument " + variable->to_string() + ")"; 
            }

    };
    class ArgLValue : public Argument {
        public:
            std::unique_ptr<Argument> varArg;
            ArgLValue(std::unique_ptr<Argument> varArg) :
                varArg(std::move(varArg)) {}
            ~ArgLValue() = default;
            std::string to_string() override {
                return "(ArgLValue " + varArg->to_string() + ")";
            }
    }; // TODO: move to LValue class?
    class TupleLValue : public Argument {
        public:
            std::vector<std::unique_ptr<Argument>> args;

            TupleLValue(std::vector<std::unique_ptr<Argument>> args) :
                args(std::move(args)) {}
            ~TupleLValue() = default;

            std::string to_string() override {
                std::string str = "(TupleLValue";
                for(const auto &a: args) {
                    str += " " + a->to_string();
                }
                return str + ")";
            }
    };
    class ArrayArgument : public Argument {
        public:
            std::unique_ptr<Variable> var;
            std::vector<std::unique_ptr<Variable>> vars;

            ArrayArgument(std::unique_ptr<Variable> var, std::vector<std::unique_ptr<Variable>> vars) :
                var(std::move(var)), vars(std::move(vars)) {}
            ~ArrayArgument() = default;

            std::string to_string() override {
                std::string str = "(ArrayArgument " + var->to_string();
                for (const auto &v: vars) {
                    str += " " + v->to_string();
                }
                return str + ")";
            }
    };


    class Expr : public ASTNode {
        public: 
            bool unop = false;
    };

    class IntExpr : public Expr {
        public:
            long long value;
            std::string str;

            IntExpr(std::string v) : str(v) {
                char *end;
                long long tmp = strtoll(v.c_str(), &end, 10);
                if (errno == ERANGE) {
                    throw ParseException("integer far too large!");
                }
                value = tmp;
            }
            ~IntExpr() = default;
            std::string to_string() override {
                return "(IntExpr " + std::to_string(value) + ")";
            }
    };
    class FloatExpr : public Expr {
        public:
            double value;
            std::string str;
            char* end;
            FloatExpr(std::string istr) {
                bool touched_num = false;
                for(char &c: istr) {
                    if (c == '.') {
                        break;
                    } else if (c != '0') {
                        if (!touched_num) { touched_num = 1; }
                    } if (touched_num) {
                        str += c;
                    }
                }
                if (!str.length()) {
                    str = "0";
                }
                double tmp = strtod(str.c_str(), &end);
                if (isnan(tmp)) {
                    throw ParseException("you cannot create a NaN!");
                } else if (isinf(tmp)) {
                    throw ParseException("you cannot create an inf!");
                }
                
                value = tmp;
            }
            ~FloatExpr() = default;
            std::string to_string() override {
                return "(FloatExpr " + str + ")";
            }

    };
    class VarExpr : public Expr {
        public:
            std::unique_ptr<Variable> var;

            VarExpr(std::unique_ptr<Variable> var) :
                var(std::move(var)) {}
            ~VarExpr() = default;
            std::string to_string() override {
                return "(VarExpr " + var->to_string() + ")";
            }
    };
    class TrueExpr : public Expr {
        public:
            TrueExpr() = default;
            ~TrueExpr() = default;
            std::string to_string() override { return "(TrueExpr)"; }
    };
    class FalseExpr : public Expr {
        public:
            FalseExpr() = default;
            ~FalseExpr() = default;
            std::string to_string() override { return "(FalseExpr)"; }
    };
    class TupleLiteralExpr : public Expr {
        public:
            std::vector<std::unique_ptr<Expr>> exprs;

            TupleLiteralExpr(std::vector<std::unique_ptr<Expr>> exprs) :
                exprs(std::move(exprs)) {}
            ~TupleLiteralExpr() = default;
            
            std::string to_string() override {
                std::string str = "(TupleLiteralExpr";
                for (const auto &e: exprs) {
                    str += " " + e->to_string();
                }
                return str + ")";
            }

    };
    class ArrayLiteralExpr : public Expr {
        public:
            std::vector<std::unique_ptr<Expr>> exprs;

            ArrayLiteralExpr(std::vector<std::unique_ptr<Expr>> exprs) :
                exprs(std::move(exprs)) {}
            ~ArrayLiteralExpr() = default;

            std::string to_string() override {
                std::string str = "(ArrayLiteralExpr";
                for (const auto &e: exprs) {
                    str += " " + e->to_string();
                }
                return str + ")";
            }
    };
    class TupleIndexExpr : public Expr {
        public:
            std::unique_ptr<Expr> expr;
            std::string index;

            TupleIndexExpr(std::unique_ptr<Expr> expr, std::string index) :
                expr(std::move(expr)), index(index) {}
            ~TupleIndexExpr() = default;

            std::string to_string() override {
                char *end;
                return "(TupleIndexExpr " + expr->to_string() + " " + std::to_string(strtoll(index.c_str(), &end, 10)) + ")";
            }
    };
    class ArrayIndexExpr : public Expr {
        public:
            std::unique_ptr<Expr> expr;
            std::vector<std::unique_ptr<Expr>> indices;

            ArrayIndexExpr(std::unique_ptr<Expr> expr, std::vector<std::unique_ptr<Expr>> indices) :
                expr(std::move(expr)), indices(std::move(indices)) {}
            ~ArrayIndexExpr() = default;

            std::string to_string() override {
                std::string str = "(ArrayIndexExpr " + expr->to_string();
                for (const auto &e: indices) {
                    str += " " + e->to_string();
                }
                return str + ")";
            }
    };
    class CallExpr : public Expr {
        public:
            std::unique_ptr<Variable> var;
            std::vector<std::unique_ptr<Expr>> parameters;

            CallExpr(std::unique_ptr<Variable> var, std::vector<std::unique_ptr<Expr>> parameters) :
                var(std::move(var)), parameters(std::move(parameters)) {}
            ~CallExpr() = default;

            std::string to_string() override {
                std::string str = "(CallExpr " + var->to_string();
                for (const auto &e: parameters) {
                    str += " " + e->to_string();
                }
                return str + ")";
            }
    };
    class UnopExpr : public Expr {
        public:
            std::string op;
            std::unique_ptr<Expr> expr;

            UnopExpr(std::string op, std::unique_ptr<Expr> expr) :
                op(op), expr(std::move(expr)) { unop = true; }
            ~UnopExpr() = default;

            std::string to_string() override {
                return "(UnopExpr " + op + " " + expr->to_string() + ")";
            }
    };
    class BinopExpr : public Expr {
        public:
            std::string op;
            std::unique_ptr<Expr> lExpr;
            std::unique_ptr<Expr> rExpr;

            BinopExpr(std::string op, std::unique_ptr<Expr> lExpr, std::unique_ptr<Expr> rExpr) :
                op(op), lExpr(std::move(lExpr)), rExpr(std::move(rExpr)) {}
            ~BinopExpr() = default;

            std::string to_string() override {
                return "(BinopExpr " + lExpr->to_string() + " " + op + " " + rExpr->to_string() + ")";
            }
    };
    class IfExpr : public Expr {
        public:
            std::unique_ptr<Expr> condExpr;
            std::unique_ptr<Expr> thenExpr;
            std::unique_ptr<Expr> elseExpr;

            IfExpr(std::unique_ptr<Expr> condExpr, std::unique_ptr<Expr> thenExpr, std::unique_ptr<Expr> elseExpr) :
                condExpr(std::move(condExpr)), thenExpr(std::move(thenExpr)), elseExpr(std::move(elseExpr)) {}
            ~IfExpr() = default;

            std::string to_string() override {
                return "(IfExpr " + condExpr->to_string() + " " + thenExpr->to_string() + " " + elseExpr->to_string() + ")";
            }
    };
    class ArrayLoopExpr : public Expr {
        public:
            std::vector<std::unique_ptr<Variable>> vars;
            std::vector<std::unique_ptr<Expr>> exprs;
            std::unique_ptr<Expr> body;

            ArrayLoopExpr(std::vector<std::unique_ptr<Variable>> vars, std::vector<std::unique_ptr<Expr>>exprs, std::unique_ptr<Expr> body) :
                vars(std::move(vars)), exprs(std::move(exprs)), body(std::move(body)) {}
            ~ArrayLoopExpr() = default;

            std::string to_string() override {
                std::string str = "(ArrayLoopExpr";
                for (int i = 0; i < vars.size(); i++) {
                    str += " " + vars[i]->to_string() + " " + exprs[i]->to_string();
                }
                return str + " " + body->to_string() + ")";
            }
    };
    class SumLoopExpr : public Expr {
        public:
            std::vector<std::unique_ptr<Variable>> vars;
            std::vector<std::unique_ptr<Expr>> exprs;
            std::unique_ptr<Expr> body;

            SumLoopExpr(std::vector<std::unique_ptr<Variable>> vars, std::vector<std::unique_ptr<Expr>>exprs, std::unique_ptr<Expr> body) :
                vars(std::move(vars)), exprs(std::move(exprs)), body(std::move(body)) {}
            ~SumLoopExpr() = default;

            std::string to_string() override {
                std::string str = "(SumLoopExpr";
                for (int i = 0; i < vars.size(); i++) {
                    str += " " + vars[i]->to_string() + " " + exprs[i]->to_string();
                }
                return str + " " + body->to_string() + ")";
            }
    };


    class Type : public ASTNode {};

    class IntType : public Type {
        public:
            IntType() = default;
            ~IntType() = default;
            std::string to_string() override {
                return "(IntType)";
            }
    };
    class FloatType : public Type {
        public:
            FloatType() = default;
            ~FloatType() = default;
            std::string to_string() override {
                return "(FloatType)";
            }
    };
    class BoolType : public Type {
        public:
            BoolType() = default;
            ~BoolType() = default;
            std::string to_string() override {
                return "(BoolType)";
            }
    };
    class VarType : public Type {
        public:
            std::unique_ptr<Variable> var;

            VarType(std::unique_ptr<Variable> var) :
                var(std::move(var)) {}
            ~VarType() = default;

            std::string to_string() override {
                return "(VarType " + var->to_string() + ")";
            }
    };
    class ArrayType : public Type {
        public:
            std::unique_ptr<Type> ty;
            int dimension;

            ArrayType(std::unique_ptr<Type> ty, int dimension) :
                ty(std::move(ty)), dimension(dimension) {}
            ~ArrayType() = default;

            std::string to_string() override {
                return "(ArrayType " + ty->to_string() + " " + std::to_string(dimension) + ")";
            }
    };
    class TupleType : public Type {
        public:    
            std::vector<std::unique_ptr<Type>> tys;

            TupleType(std::vector<std::unique_ptr<Type>> tys) :
                tys(std::move(tys)) {}
            ~TupleType() = default;

            std::string to_string() override {
                std::string str = "(TupleType";
                for (const auto &t: tys) {
                    str += " " + t->to_string();
                }
                return str + ")";
            }

    };


    class Binding : public ASTNode {};

    class VarBinding : public Binding {
        public:
            std::unique_ptr<Argument> arg;
            std::unique_ptr<Type> ty;

            VarBinding(std::unique_ptr<Argument> arg, std::unique_ptr<Type> ty) :
                arg(std::move(arg)), ty(std::move(ty)) {}
            ~VarBinding() = default;

            std::string to_string() override {
                return "(VarBinding " + arg->to_string() + " " + ty->to_string() + ")";
            }
    };
    class TupleBinding : public Binding {
        public:
            std::vector<std::unique_ptr<Binding>> bindings;

            TupleBinding(std::vector<std::unique_ptr<Binding>> bindings) :
                bindings(std::move(bindings)) {}
            ~TupleBinding() = default;

            std::string to_string() override {
                std::string str = "(TupleBinding";
                for (const auto &b: bindings) {
                    str += " " + b->to_string();
                }
                return str + ")";
            }
    };


    class Stmt : public ASTNode {};

    class LetStmt : public Stmt {
        public:
            std::unique_ptr<Argument> lval;
            std::unique_ptr<Expr> expr;

            LetStmt(std::unique_ptr<Argument> lval, std::unique_ptr<Expr> expr) :
                lval(std::move(lval)), expr(std::move(expr)) {}
            ~LetStmt() = default;
            std::string to_string() override {
                return "(LetStmt " + lval->to_string() + " " + expr->to_string() + ")";
            }
    };
    class AssertStmt : public Stmt {
        public:
            std::unique_ptr<Expr> expr;
            std::string str;
            AssertStmt(std::unique_ptr<Expr> expr, std::string str) :
                expr(std::move(expr)), str(str) {}
            ~AssertStmt() = default;
            std::string to_string() override {
                return "(AssertStmt " + expr->to_string() + " " + str + ")";
            }
    };
    class ReturnStmt : public Stmt {
        public:
            std::unique_ptr<Expr> retExp;

            ReturnStmt(std::unique_ptr<Expr> retExp) :
                retExp(std::move(retExp)) {}
            ~ReturnStmt() = default;

            std::string to_string() override {
                return "(ReturnStmt " + retExp->to_string() + ")";
            }
    };


    class Cmd : public ASTNode {};

    class ReadCmd : public Cmd {
        public:
            std::string file;
            std::unique_ptr<Argument> varArg;

            ReadCmd(std::string file, std::unique_ptr<Argument> varArg) :
                file(file), varArg(std::move(varArg)) {}
            ~ReadCmd() override = default;

            std::string to_string() override {
                return "(ReadCmd " + file + " " + varArg->to_string() + ")";
            }
    };
    class WriteCmd : public Cmd {
        std::unique_ptr<Expr> exp;
        std::string str;
        public:
            WriteCmd(std::unique_ptr<Expr> exp, std::string str) :
                exp(std::move(exp)), str(str) {}
            ~WriteCmd() = default;
            std::string to_string() override {
                return "(WriteCmd " + exp->to_string() + " " + str + ")";
            }

    };
    class TypeCmd : public Cmd {
        public:
            std::unique_ptr<Variable> var;
            std::unique_ptr<Type> ty;

            TypeCmd(std::unique_ptr<Variable> var, std::unique_ptr<Type> ty) :
                var(std::move(var)), ty(std::move(ty)) {}
            ~TypeCmd() = default;

            std::string to_string() override {
                return "(TypeCmd " + var->to_string() + " " + ty->to_string() + ")";
            }
    };
    class LetCmd : public Cmd {
        public:
            std::unique_ptr<Argument> lval;
            std::unique_ptr<Expr> expr;

            LetCmd(std::unique_ptr<Argument> lval, std::unique_ptr<Expr> expr) :
                lval(std::move(lval)), expr(std::move(expr)) {}
            ~LetCmd() = default;
            std::string to_string() override {
                return "(LetCmd " + lval->to_string() + " " + expr->to_string() + ")";
            }
    };
    class AssertCmd : public Cmd {
        public:
            std::unique_ptr<Expr> expr;
            std::string str;
            AssertCmd(std::unique_ptr<Expr> expr, std::string str) :
                expr(std::move(expr)), str(str) {}
            ~AssertCmd() = default;
            std::string to_string() override {
                return "(AssertCmd " + expr->to_string() + " " + str + ")";
            }
    };
    class PrintCmd : public Cmd {
        public:
            std::string str;
            PrintCmd(std::string str) :
                str(str) {}
            ~PrintCmd() = default;
            std::string to_string() override {
                return "(PrintCmd " + str + ")";
            }

    };
    class ShowCmd : public Cmd {
        public:
            std::unique_ptr<Expr> expr;
            ShowCmd(std::unique_ptr<Expr> expr) :
                expr(std::move(expr)) {}
            ~ShowCmd() = default;
            std::string to_string() override {
                return "(ShowCmd " + expr->to_string() + ")";
            }
    };
    class TimeCmd : public Cmd {
        public:
            std::unique_ptr<Cmd> cmd;

            TimeCmd(std::unique_ptr<Cmd> cmd) :
                cmd(std::move(cmd)) {}
            ~TimeCmd() = default;

            std::string to_string() override {
                return "(TimeCmd " + cmd->to_string() + ")";
            }
    };
    class FnCmd : public Cmd {
        public:
            std::unique_ptr<Variable> var;
            std::vector<std::unique_ptr<Binding>> bindings;
            std::unique_ptr<Type> retTy;
            std::vector<std::unique_ptr<Stmt>> statements;

            FnCmd(std::unique_ptr<Variable> var, std::vector<std::unique_ptr<Binding>> bindings,
            std::unique_ptr<Type> retTy, std::vector<std::unique_ptr<Stmt>> statements) : 
                var(std::move(var)), bindings(std::move(bindings)), 
                retTy(std::move(retTy)), statements(std::move(statements)) {}
            ~FnCmd() = default;

            std::string to_string() override {
                std::string str = "(FnCmd " + var->to_string();
                str += " (";    //TODO ?? iffy print
                for (int i = 0; i < bindings.size(); i++) {
                    str += bindings[i]->to_string();
                    if (i != bindings.size() - 1) {str += " ";}
                }
                str += ") " + retTy->to_string();
                for (const auto &s: statements) {
                    str += " " + s->to_string();
                }
                return str + ")";
            }
    };

    class Parser {
        private:
            std::vector<std::unique_ptr<ASTNode>> astTree;
            std::vector<std::unique_ptr<Lex::Token>> tokens;
            std::vector<std::vector<std::string>> precedence;


            std::string expectToken(int *, Lex::Tokty);
            Lex::Tokty peekToken(int);

            std::pair<std::unique_ptr<Cmd>, int> parseCmd(int);
            std::pair<std::unique_ptr<Cmd>, int> parseWriteCmd(int);
            std::pair<std::unique_ptr<Cmd>, int> parseReadCmd(int);
            std::pair<std::unique_ptr<Cmd>, int> parseTypeCmd(int);
            std::pair<std::unique_ptr<Cmd>, int> parseLetCmd(int);
            std::pair<std::unique_ptr<Cmd>, int> parseAssertCmd(int);
            std::pair<std::unique_ptr<Cmd>, int> parsePrintCmd(int);
            std::pair<std::unique_ptr<Cmd>, int> parseShowCmd(int);
            std::pair<std::unique_ptr<Cmd>, int> parseTimeCmd(int);
            std::pair<std::unique_ptr<Cmd>, int> parseFnCmd(int);


            std::pair<std::unique_ptr<Type>, int> parseType(int);
            std::pair<std::unique_ptr<Type>, int> parseTypeCont(std::unique_ptr<Type>, int);
            std::pair<std::unique_ptr<Type>, int> parseArrayType(std::unique_ptr<Type>, int);
            std::pair<std::unique_ptr<Type>, int> parseTupleType(int);

            std::tuple<std::vector<std::unique_ptr<Variable>>, std::vector<std::unique_ptr<Expr>>, int> parseLoopBinds(int);
            std::pair<std::unique_ptr<Expr>, int> parseArrayLoopExpr(int);
            std::pair<std::unique_ptr<Expr>, int> parseSumLoopExpr(int);
            std::pair<std::unique_ptr<Expr>, int> parseIfExpr(int);
            std::pair<std::unique_ptr<Expr>, int> parseExprLvl6Cont(std::unique_ptr<Expr>, int);
            std::pair<std::unique_ptr<Expr>, int> parseExprLvl6(int);
            std::pair<std::unique_ptr<Expr>, int> parseExprLvl5Cont(std::unique_ptr<Expr>, int);
            std::pair<std::unique_ptr<Expr>, int> parseExprLvl5(int);
            std::pair<std::unique_ptr<Expr>, int> parseExprLvl4Cont(std::unique_ptr<Expr>, int);
            std::pair<std::unique_ptr<Expr>, int> parseExprLvl4(int);
            std::pair<std::unique_ptr<Expr>, int> parseExprLvl3Cont(std::unique_ptr<Expr>, int);
            std::pair<std::unique_ptr<Expr>, int> parseExprLvl3(int);
            std::pair<std::unique_ptr<Expr>, int> parseExprLvl2Cont(std::unique_ptr<Expr>, int);
            std::pair<std::unique_ptr<Expr>, int> parseExprLvl2(int);
            std::pair<std::unique_ptr<Expr>, int> parseExprLvl1Cont(std::unique_ptr<Expr>, int);
            std::pair<std::unique_ptr<Expr>, int> parseExprLvl1(int);
            std::pair<std::unique_ptr<Expr>, int> parseExpr(int);
            
            std::pair<std::unique_ptr<Expr>, int> parseLiteralExpr(int);
            std::pair<std::unique_ptr<Expr>, int> parseLiteralExprCont(std::unique_ptr<Expr>, int);
            std::pair<std::unique_ptr<Expr>, int> parseVariableExprCont(std::unique_ptr<Variable>, int);
            std::pair<std::vector<std::unique_ptr<Expr>>, int> parseExprSequence(int, Lex::Tokty, Lex::Tokty); 
            std::pair<std::unique_ptr<Expr>, int> parseTupleLiteralExpr(int);
            std::pair<std::unique_ptr<Expr>, int> parseTupleIndexExpr(std::unique_ptr<Expr>, int);
            std::pair<std::unique_ptr<Expr>, int> parseArrayIndexExpr(std::unique_ptr<Expr>, int);
            std::pair<std::unique_ptr<Expr>, int> parseArrayLiteralExpr(int);


            std::pair<std::unique_ptr<Argument>, int> parseArgument(int);
            std::pair<std::unique_ptr<Argument>, int> parseArrayArgument(std::unique_ptr<Variable>, int);            
            std::pair<std::unique_ptr<Argument>, int> parseLValue(int);
            std::pair<std::unique_ptr<Argument>, int> parseTupleLValue(int);
            std::pair<std::unique_ptr<Variable>, int> parseVariable(int);

            std::pair<std::unique_ptr<Binding>, int> parseBinding(int);
            std::pair<std::unique_ptr<TupleBinding>, int> parseTupleBinding(int);
            std::pair<std::vector<std::unique_ptr<Binding>>, int> parseParameterSequence(int);

            std::pair<std::unique_ptr<Stmt>, int> parseLetStmt(int);
            std::pair<std::unique_ptr<Stmt>, int> parseAssertStmt(int);
            std::pair<std::unique_ptr<Stmt>, int> parseReturnStmt(int);
            std::pair<std::unique_ptr<Stmt>, int> parseStmt(int);
            std::pair<std::vector<std::unique_ptr<Stmt>>, int> parseStmtSequence(int);


        public:
            Parser(std::vector<std::unique_ptr<Lex::Token>>);

            void prettyPrint();
            void doParse();
    };

    
} // namespace Parse

#endif