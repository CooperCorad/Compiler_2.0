import mylexer

# cmd  : read image <string> to <argument>
#      | write image <expr> to <string>
#      | type <variable> = <type>
#      | let <lvalue> = <expr>
#      | assert <expr> , <string>
#      | print <string>
#      | show <expr>

# type : int
#      | bool
#      | float
#      | <variable>

# expr : <integer>
#      | <float>
#      | true
#      | false
#      | <variable>

# argument : <variable>

# lvalue : <argument>
import math


class ParserException(Exception):
    def __init__(self, _message):
        self.message = _message
        super().__init__(self.message)


class ASTNode:
    def to_string(self):
        return ''


class Variable(ASTNode):
    variable : str

    def __init__(self, _variable):
        self.variable = _variable

    def to_string(self):
        return self.variable


class Argument(ASTNode):
    pass


class VarArg(Argument):
    variable : Variable

    def __init__(self, _variable : Variable):
        self.variable = _variable

    def to_string(self):
        ret = '(VarArgument ' + self.variable.to_string() + ')'
        return ret


class ArgLValue(Argument):
    variable : Variable

    def __init__(self, _variable : Variable):
        self.variable = _variable

    def to_string(self):
        ret = '(ArgLValue ' + self.variable.to_string() + ')'
        return ret

# expr : <integer>
#      | <float>
#      | true
#      | false
#      | <variable>
class Expr(ASTNode):
    pass


class IntExpr(Expr):
    intVal : int

    def __init__(self, _intVal : str):
        self.intVal = int(_intVal)
        if self.intVal < (-2 << 63)  or self.intVal > (2 << 63 - 1):
            raise ParserException("You cannot have an int beyond the ranges -2^63 <-> 2^63 - 1")

    def to_string(self):
        ret = '(IntExpr ' + str(self.intVal) + ')'
        return ret


class FloatExpr(Expr):
    floatVal : float

    def __init__(self, _floatVal : str):
        self.floatVal = float(_floatVal)
        if math.isnan(self.floatVal) or math.isinf(self.floatVal):
            raise ParserException("You cannot have an infinite or NaN float (likely a divide by Zero issue!")

    def to_string(self):
        ret = '(FloatExpr ' + str(int(self.floatVal)) + ')'


class TrueExpr(Expr):
    def to_string(self):
        ret = '(TrueExper)'
        return ret


class FalseExpr(Expr):
    def to_string(self):
        ret = '(FalseExpr)'
        return ret


class VariableExpr(Expr):
    variable : Variable

    def __init__(self, _variable : Variable):
        self.variable = _variable

    def to_string(self):
        ret = '(VarExpr ' + self.variable.to_string() + ')'
        return ret


class Type(ASTNode):
    def __init__(self):
        pass

    def to_string(self):
        return ''


class IntType(Type):
    def __init__(self):
        pass

    def to_string(self):
        ret = '(IntType)'
        return ret


class BoolType(Type):
    def __init__(self):
        pass

    def to_string(self):
        ret = '(BoolType)'
        return ret


class FloatType(Type):
    def __init__(self):
        pass

    def to_string(self):
        ret = '(FloatType)'
        return ret


class VarType(Type):
    vairable : Variable

    def __init__(self, _variable : Variable):
        self.vairable = _variable

    def to_string(self):
        ret = '(VarType ' + self.vairable.to_string() + ')'
        return ret


class Cmd(ASTNode):
    pass


class ReadCmd(Cmd):
    filename : str
    vararg : VarArg

    def __init__(self, _filename : str, _vararg : VarArg):
        self.filename = _filename
        self.vararg = _vararg

    def to_string(self):
        ret = '(ReadCmd ' + self.filename + ' ' + self.vararg.to_string() + ')'
        return ret


class WriteCmd(Cmd):
    expr : Expr
    filename : str

    def __init__(self, _expr : Expr, _filename : str):
        self.expr = _expr
        self.filename = _filename

    def to_string(self):
        ret = '(WriteCmd ' + self.expr.to_string() + ' ' + self.filename + ')'
        return ret


class TypeCmd(Cmd):
    variable : Variable

    def __init__(self, _variable : Variable, _typeval):
        self.variable = _variable
        self.typeval = _typeval

    def to_string(self):
        self.typeval.to_string()
        ret = '(TypeCmd ' + self.variable.to_string() + ' ' + self.typeval.to_string() + ')'
        return ret


class LetCmd(Cmd):
    lvalue : ArgLValue
    expr : Expr

    def __init__(self, _lvalue : ArgLValue, _expr : Expr):
        self.lvalue = _lvalue
        self.expr = _expr

    def to_string(self):
        ret = '(LetCmd ' + self.lvalue.to_string() + ' ' + self.expr.to_string() + ')'
        return ret


class AssertCmd(Cmd):
    expr : Expr
    string : str

    def __init__(self, _expr : Expr, _string : str):
        self.expr = _expr
        self.string = _string

    def to_string(self):
        ret = '(AssertCmd ' + self.expr.to_string() + ' ' + self.string + ')'
        return ret


class PrintCmd(Cmd):
    string : str

    def __init__(self, _string : str):
        self.string = _string

    def to_string(self):
        ret = '(PrintCmd ' + self.string + ')'
        return ret


class ShowCmd(Cmd):
    expr : Expr

    def __init__(self, _expr : Expr):
        self.expr = _expr

    def to_string(self):
        ret = '(ShowCmd ' + self.expr.to_string() + ')'
        return ret


class Parser:
    tokens = []
    program = []

    def __init__(self, _tokens):
        self.tokens = _tokens


    def peek_tok(self, index):
        return self.tokens[index].t

    def expect_tok(self, index, toktype):
        if self.tokens[index].t != toktype:
            ret = 'No token of type ' + toktype + ' found at ' + str(index)
            raise ParserException(ret)
        return self.tokens[index].text

    def to_string(self):
        ret = ''
        for cmd in self.program:
            ret += cmd.to_string() + '\n'

        return ret[:-1]

    def parse(self):
        index = 0

        while True:
            if self.peek_tok(index) == 'END_OF_FILE':
                return self.program
            else:
                cmd, index = self.parse_cmd(index)
                # index += 1
                if self.peek_tok(index) != 'END_OF_FILE':
                    self.expect_tok(index, 'NEWLINE')
                    index += 1
                self.program.append(cmd)

    def parse_cmd(self, index):
        command = self.peek_tok(index)

        if command == 'READ':
            return self.parse_readcmd(index)
        elif command == 'WRITE':
            return self.parse_writecmd(index)
        elif command == 'TYPE':
            return self.parse_typecmd(index)
        elif command == 'LET':
            return self.parse_letcmd(index)
        elif command == 'ASSERT':
            return self.parse_assertcmd(index)
        elif command == 'PRINT':
            return self.parse_printcmd(index)
        elif command == 'SHOW':
            return self.parse_showcmd(index)
        else:
            ret = 'Command not found at : ' + str(index)
            raise ParserException(ret)

    # read image <string> to <argument>
    def parse_readcmd(self, index):
        self.expect_tok(index, 'READ')
        index += 1
        self.expect_tok(index, 'IMAGE')
        index += 1
        filename = self.expect_tok(index, 'STRING')
        index += 1
        self.expect_tok(index, 'TO')
        index += 1
        argument = self.parse_argument(index)
        index += 1
        ret = ReadCmd(filename, argument)
        return ret, index

    # write image <expr> to <string>
    def parse_writecmd(self, index):
        self.expect_tok(index, 'WRITE')
        index += 1
        self.expect_tok(index, 'IMAGE')
        index += 1
        expr = self.parse_expr(index)
        index += 1
        self.expect_tok(index, 'TO')
        index += 1
        filename = self.expect_tok(index, 'STRING')
        index += 1
        ret = WriteCmd(expr, filename)
        return ret, index

    # type <variable> = <type>
    def parse_typecmd(self, index):
        self.expect_tok(index, 'TYPE')
        index += 1
        var = self.parse_argument(index)
        index += 1
        self.expect_tok(index, 'EQUALS')
        index += 1
        typ = self.parse_type(index)
        index += 1
        ret = TypeCmd(var, typ)
        return ret, index

    # let <lvalue> = <expr>
    def parse_letcmd(self, index):
        self.expect_tok(index, 'LET')
        index += 1
        lval = self.parse_lvalue(index)
        index += 1
        self.expect_tok(index, 'EQUALS')
        index += 1
        expr = self.parse_expr(index)
        index += 1
        ret = LetCmd(lval, expr)
        return ret, index

    # assert <expr> , <string>
    def parse_assertcmd(self, index):
        self.expect_tok(index, 'ASSERT')
        index += 1
        expr = self.parse_expr(index)
        index += 1
        self.expect_tok(index, 'COMMA')
        index += 1
        string = self.expect_tok(index, 'STRING')
        index += 1
        ret = AssertCmd(expr, string)
        return ret, index

    # print <string>
    def parse_printcmd(self, index):
        self.expect_tok(index, 'PRINT')
        index += 1
        string = self.expect_tok(index, 'STRING')
        index += 1
        ret = PrintCmd(string)
        return ret, index

    # show <expr>
    def parse_showcmd(self, index):
        self.expect_tok(index, 'SHOW')
        index += 1
        expr = self.parse_expr(index)
        index += 1
        ret = ShowCmd(expr)
        return ret, index

    # TODO remove index math from these!!
    def parse_argument(self, index):
        vaarg = VarArg(Variable(self.expect_tok(index, 'VARIABLE')))
        return vaarg

    def parse_expr(self, index):
        varexp = VariableExpr(Variable(self.expect_tok(index, 'VARIABLE')))
        return varexp

    def parse_variable(self, index):
        var = Variable(self.expect_tok(index, 'VARIABLE'))
        return var

    def parse_type(self, index):
        tp = self.peek_tok(index)
        if tp == 'INT':
            return IntType()
        elif tp == 'FLOAT':
            return FloatType()
        elif tp == 'BOOL':
            return BoolType()
        elif tp == 'VARIABE':
            return self.parse_argument(index)
        else:
            ret = 'Could not find a type at ' + str(index)
            raise ParserException(ret)

    def parse_lvalue(self, index):
        var = self.expect_tok(index, 'VARIABLE')
        lvalue = ArgLValue(Variable(var))
        return lvalue









