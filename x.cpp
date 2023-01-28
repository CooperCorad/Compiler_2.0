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

// ReadCmd x("photo.jpg", VarArg(Variable("var")));
    