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
    variable: str

    def __init__(self, _variable):
        self.variable = _variable

    def to_string(self):
        return self.variable


class Argument(ASTNode):
    pass


class VarArg(Argument):
    variable: Variable

    def __init__(self, _variable: Variable):
        self.variable = _variable

    def to_string(self):
        ret = '(VarArgument ' + self.variable.to_string() + ')'
        return ret


class ArgLValue(Argument):

    def __init__(self, _variable):
        self.variable = _variable

    def to_string(self):
        ret = '(ArgLValue ' + self.variable.to_string() + ')'
        return ret


class TupleLValue(Argument):
    variables: []

    def __init__(self, _variables: []):
        self.variables = _variables

    def to_string(self):
        ret = '(TupleLValue '
        for variables in self.variables:
            ret += variables.to_string() + ' '
        ret = ret[:-1] + ')'
        return ret


class ArrayArgument(Argument):
    var : Variable
    arguments : []

    def __init__(self, _var : Variable, _arguments : []):
        self.var = _var
        self.arguments = _arguments

    def to_string(self):
        ret = '(ArrayArgument ' + self.var.to_string() + ' '
        for arg in self.arguments:
            ret += arg.to_string() + ' '
        ret = ret[:-1] + ')'
        return ret

# expr : <integer>
#      | <float>
#      | true
#      | false
#      | <variable>
class Expr(ASTNode):
    pass


class IntExpr(Expr):
    intVal: int

    def __init__(self, _intVal: str):
        self.intVal = int(_intVal)
        if self.intVal < -pow(2, 63) or self.intVal > ((pow(2, 63)) - 1):
            raise ParserException("You cannot have an int beyond the ranges -2^63 <-> 2^63 - 1")

    def to_string(self):
        ret = '(IntExpr ' + str(self.intVal) + ')'
        return ret


class FloatExpr(Expr):
    floatVal: float

    def __init__(self, _floatVal: str):
        self.floatVal = float(_floatVal)
        if math.isnan(self.floatVal) or math.isinf(self.floatVal):
            raise ParserException("You cannot have an infinite or NaN float (likely a divide by Zero issue!")

    def to_string(self):
        ret = '(FloatExpr ' + str(int(self.floatVal)) + ')'
        return ret


class TrueExpr(Expr):
    def to_string(self):
        ret = '(TrueExpr)'
        return ret


class FalseExpr(Expr):
    def to_string(self):
        ret = '(FalseExpr)'
        return ret


class VariableExpr(Expr):
    variable: Variable

    def __init__(self, _variable: Variable):
        self.variable = _variable

    def to_string(self):
        ret = '(VarExpr ' + self.variable.to_string() + ')'
        return ret


class TupleIndexExpr(Expr):
    index : int
    varxpr : Expr

    def __init__(self, _index : int, _varxpr : Expr):
        self.index = _index
        self.varxpr = _varxpr

    def to_string(self):
        ret = '(TupleIndexExpr ' + self.varxpr.to_string() + ' ' +str(self.index) + ')'
        return ret


class ArrayIndexExpr(Expr):
    expr : Expr
    exprs : []

    def __init__(self, _expr : Expr, _exprs : []):
        self.expr = _expr
        self.exprs = _exprs

    def to_string(self):
        ret = '(ArrayIndexExpr '
        if self.expr is not None:
            ret += self.expr.to_string() + ' '
        for exp in self.exprs:
            ret += exp.to_string() + ' '
        ret = ret[:-1] + ')'
        return ret


class CallExpr(Expr):
    exprs : []

    def __init__(self, _variable, _vals : []):
        self.variable = _variable
        self.exprs = _vals

    def to_string(self):
        ret = '(CallExpr ' + self.variable.to_string() + ' '
        for exp in self.exprs:
            ret += exp.to_string() + ' '
        ret = ret[:-1] + ')'
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
    variable : Variable

    def __init__(self, _variable: Variable):
        self.variable = _variable

    def to_string(self):
        ret = '(VarType ' + self.variable.to_string() + ')'
        return ret


class TupleType(Type):
    types = []

    def __init__(self, _types : []):
        self.types = _types

    def to_string(self):
        ret = '(TupleType '
        for typ in self.types:
            ret += typ.to_string() + ' '
        ret = ret[:-1] + ')'
        return ret


class ArrayType(Type):
    type : Type
    count : int

    def __init__(self, _type : Type, _count : int):
        self.type = _type
        self.count = _count

    def to_string(self):
        ret = '(ArrayType ' + self.type.to_string() + ' ' + str(self.count) + ')'
        return ret


class TupleLiteralExpr(Expr):
    types : []

    def __init__(self, _types : []):
        self.types = _types

    def to_string(self):
        ret = '(TupleLiteralExpr '
        for typ in self.types:
            ret += typ.to_string() + ' '
        ret = ret[:-1] + ')'
        return ret

class ArrayLiteralExpr(Expr):
    types : []

    def __init__(self, _types : []):
        self.types = _types

    def to_string(self):
        ret = '(ArrayLiteralExpr '
        for typ in self.types:
            ret += typ.to_string() + ' '
        ret = ret[:-1] + ')'
        return ret


# cmd  : time <cmd>
#      | fn <variable> ( <binding> , ... ) : <type> { ;
#            <stmt> ; ... ;
#      }
class Cmd(ASTNode):
    pass


class ReadCmd(Cmd):
    filename: str
    vararg: VarArg

    def __init__(self, _filename: str, _vararg: VarArg):
        self.filename = _filename
        self.vararg = _vararg

    def to_string(self):
        ret = '(ReadCmd ' + self.filename + ' '
        ret += self.vararg.to_string() + ')'
        return ret


class WriteCmd(Cmd):
    expr: Expr
    filename: str

    def __init__(self, _expr: Expr, _filename: str):
        self.expr = _expr
        self.filename = _filename

    def to_string(self):
        ret = '(WriteCmd ' + self.expr.to_string() + ' ' + self.filename + ')'
        return ret


class TypeCmd(Cmd):
    variable: Variable

    def __init__(self, _variable: Variable, _typeval):
        self.variable = _variable
        self.typeval = _typeval

    def to_string(self):
        self.typeval.to_string()
        ret = '(TypeCmd ' + self.variable.to_string() + ' ' + self.typeval.to_string() + ')'
        return ret


class LetCmd(Cmd):
    lvalue: ArgLValue
    expr: Expr

    def __init__(self, _lvalue: ArgLValue, _expr: Expr):
        self.lvalue = _lvalue
        self.expr = _expr

    def to_string(self):
        ret = '(LetCmd ' + self.lvalue.to_string() + ' ' + self.expr.to_string() + ')'
        return ret


class AssertCmd(Cmd):
    expr: Expr
    string: str

    def __init__(self, _expr: Expr, _string: str):
        self.expr = _expr
        self.string = _string

    def to_string(self):
        ret = '(AssertCmd ' + self.expr.to_string() + ' ' + self.string + ')'
        return ret


class PrintCmd(Cmd):
    string: str

    def __init__(self, _string: str):
        self.string = _string

    def to_string(self):
        ret = '(PrintCmd ' + self.string + ')'
        return ret


class ShowCmd(Cmd):
    expr: Expr

    def __init__(self, _expr: Expr):
        self.expr = _expr

    def to_string(self):
        ret = '(ShowCmd ' + self.expr.to_string() + ')'
        return ret


class TimeCmd(Cmd):
    cmd: Cmd

    def __init__(self, _cmd : Cmd):
        self.cmd = _cmd

    def to_string(self):
        ret = '(TimeCmd ' + self.cmd.to_string() + ')'
        return ret


# fn <variable> ( <binding> , ... ) : <type> { ;
#            <stmt> ; ... ;
#        }
class FnCmd(Cmd):
    variable : Variable
    bindings : []
    typ : Type
    stmts : []

    def __init__(self, _variable : Variable, _bindings : [], _typ : Type, _stmts : []):
        self.variable = _variable
        self.bindings = _bindings
        self.typ = _typ
        self.stmts = _stmts

    #TODO ???
    def to_string(self):
        ret = '(FnCmd ' + self.variable.to_string() + ' '
        ret += '('
        for bnd in self.bindings:
            ret += bnd.to_string() + ' '
        if len(self.bindings) == 0:
            ret += ' '
        ret = ret[:-1] + ') ' + self.typ.to_string() + ' '
        for stmt in self.stmts:
            ret += stmt.to_string() + ' '
        ret = ret[:-1] + ')'
        return ret



class Stmt(ASTNode):
    pass


# let <lvalue> = <expr>
class LetStmt(Stmt):
    lval : ArgLValue
    expr : Expr

    def __init__(self, _lval : ArgLValue, _expr : Expr):
        self.lval = _lval
        self.expr = _expr

    def to_string(self):
        ret = '(LetStmt ' + self.lval.to_string() + ' ' + self.expr.to_string() + ')'
        return ret


class AssertStmt(Stmt):
    expr : Expr
    string : str

    def __init__(self, _expr : Expr, _string : str):
        self.expr = _expr
        self.string = _string

    def to_string(self):
        ret = '(AssertStmt ' + self.expr.to_string() + ' ' + self.string + ')'
        return ret

class ReturnStmt(Stmt):
    expr : Expr

    def __init__(self, _expr : Expr):
        self.expr = _expr

    def to_string(self):
        ret = '(ReturnStmt ' + self.expr.to_string() + ')'
        return ret

class Binding(ASTNode):
    pass


# <argument> : <type>
class VarBinding(Binding):
    argument : Argument
    type : Type

    def __init__(self, _argument : Argument, _type : Type):
        self.argument = _argument
        self.type = _type

    def to_string(self):
        ret = '(VarBinding ' + self.argument.to_string() + ' ' + self.type.to_string() + ')'
        return ret


# { <binding> , ... }
class TupleBinding(Binding):
    bindings : []

    def __init__(self, _bindings : []):
        self.bindings = _bindings

    def to_string(self):
        ret = '(TupleBinding '
        for bnd in self.bindings:
            ret += bnd.to_string() + ' '
        ret = ret[:-1] + ')'
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
        ret = self.tokens[index].text
        index += 1
        return ret, index

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
                # if self.peek_tok(index) != 'END_OF_FILE':
                #     self.expect_tok(index, 'NEWLINE')
                #     index += 1
                _, index = self.expect_tok(index, 'NEWLINE')
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
        elif command == 'TIME':
            return self.parse_timecmd(index)
        elif command == 'FN':
            return self.parse_fncmd(index)
        else:
            ret = 'Command not found at : ' + str(index)
            raise ParserException(ret)

    # read image <string> to <argument>
    def parse_readcmd(self, index):
        _, index = self.expect_tok(index, 'READ')
        _, index = self.expect_tok(index, 'IMAGE')
        filename, index = self.expect_tok(index, 'STRING')
        _, index = self.expect_tok(index, 'TO')
        argument, index = self.parse_argument(index)
        ret = ReadCmd(filename, argument)
        return ret, index

    # write image <expr> to <string>
    def parse_writecmd(self, index):
        _, index = self.expect_tok(index, 'WRITE')
        _, index = self.expect_tok(index, 'IMAGE')
        expr, index = self.parse_expr(index)
        _, index = self.expect_tok(index, 'TO')
        filename, index = self.expect_tok(index, 'STRING')
        ret = WriteCmd(expr, filename)
        return ret, index

    # type <variable> = <type>
    def parse_typecmd(self, index):
        _, index = self.expect_tok(index, 'TYPE')
        var, index = self.parse_variable(index)
        _, index = self.expect_tok(index, 'EQUALS')
        typ, index = self.parse_type(index)
        ret = TypeCmd(var, typ)
        return ret, index

    # let <lvalue> = <expr>
    def parse_letcmd(self, index):
        _, index = self.expect_tok(index, 'LET')
        lval, index = self.parse_lvalue(index)
        _, index = self.expect_tok(index, 'EQUALS')
        expr, index = self.parse_expr(index)
        ret = LetCmd(lval, expr)
        return ret, index

    # assert <expr> , <string>
    def parse_assertcmd(self, index):
        _, index = self.expect_tok(index, 'ASSERT')
        expr, index = self.parse_expr(index)
        _, index = self.expect_tok(index, 'COMMA')
        string, index = self.expect_tok(index, 'STRING')
        ret = AssertCmd(expr, string)
        return ret, index

    # print <string>
    def parse_printcmd(self, index):
        _, index = self.expect_tok(index, 'PRINT')
        string, index = self.expect_tok(index, 'STRING')
        ret = PrintCmd(string)
        return ret, index

    # show <expr>
    def parse_showcmd(self, index):
        _, index = self.expect_tok(index, 'SHOW')
        expr, index = self.parse_expr(index)
        ret = ShowCmd(expr)
        return ret, index

    def parse_timecmd(self, index):
        _, index = self.expect_tok(index, 'TIME')
        cmd, index = self.parse_cmd(index)
        return TimeCmd(cmd), index

    def parse_tuplebinding(self, index, bnds):
        bnd, index = self.parse_binding(index)
        bnds.append(bnd)

        if self.peek_tok(index) == 'COMMA':
            _, index = self.expect_tok(index, 'COMMA')
            return self.parse_tuplebinding(index, bnds)
        if self.peek_tok(index) == 'RCURLY':
            _, index = self.expect_tok(index, 'RCURLY')
            return bnds, index

    def parse_binding(self, index):
        if self.peek_tok(index) == 'LCURLY':
            _, index = self.expect_tok(index, 'LCURLY')
            if self.peek_tok(index) == 'RCURLY':
                _, index = self.expect_tok(index, 'RCURLY')
                return TupleBinding([]), index
            else:
                bnds, index = self.parse_tuplebinding(index, [])
                return TupleBinding(bnds), index
        else:
            arg, index = self.parse_argument(index)
            _, index = self.expect_tok(index, 'COLON')
            typ, index = self.parse_type(index)
            return VarBinding(arg, typ), index

    def parse_binding_seq(self, index, bnds):
        bnd, index = self.parse_binding(index)
        bnds.append(bnd)

        if self.peek_tok(index) == 'COMMA':
            _, index = self.expect_tok(index, 'COMMA')
            return self.parse_binding_seq(index, bnds)
        if self.peek_tok(index) == 'RPAREN':
            _, index = self.expect_tok(index, 'RPAREN')
            return bnds, index

    def parse_fnbindings(self, index):
        _, index = self.expect_tok(index, 'LPAREN')

        if self.peek_tok(index) == 'RPAREN':
            _, index = self.expect_tok(index, 'RPAREN')
            return [], index

        bnds, index = self.parse_binding_seq(index, [])
        return bnds, index

    def parse_letstmt(self, index):
        _, index = self.expect_tok(index, 'LET')
        lval, index = self.parse_lvalue(index)
        _, index = self.expect_tok(index, 'EQUALS')
        expr, index = self.parse_expr(index)
        return LetStmt(lval, expr), index

    def parse_assertstmt(self, index):
        _, index = self.expect_tok(index, 'ASSERT')
        expr, index = self.parse_expr(index)
        _, index = self.expect_tok(index, 'COMMA')
        string, index = self.expect_tok(index, 'STRING')
        return AssertStmt(expr, string), index

    def parse_returnstmt(self, index):
        _, index = self.expect_tok(index, 'RETURN')
        expr, index = self.parse_expr(index)
        return ReturnStmt(expr), index

    def parse_stmt(self, index):
        t = self.peek_tok(index)

        if t == 'LET':
            return self.parse_letstmt(index)
        if t == 'ASSERT':
            return self.parse_assertstmt(index)
        if t == 'RETURN':
            return self.parse_returnstmt(index)
        else:
            raise ParserException('Could not find stmt at index ' + str(index))

    def parse_stmt_seq(self, index, stmts):
        stmt, index = self.parse_stmt(index)
        stmts.append(stmt)

        if self.peek_tok(index) == 'NEWLINE':
            _, index = self.expect_tok(index, 'NEWLINE')
            if self.peek_tok(index) == 'RCURLY':
                _, index = self.expect_tok(index, 'RCURLY')
                return stmts, index
            return self.parse_stmt_seq(index, stmts)

    def parse_stmt_list(self, index):
        while self.peek_tok(index) == 'NEWLINE':
            _, index = self.expect_tok(index, 'NEWLINE')
        if self.peek_tok(index) == 'RCURLY':
            _, index = self.expect_tok(index, 'RCURLY')
            return [], index
        return self.parse_stmt_seq(index, [])

    def parse_fncmd(self, index):
        _, index = self.expect_tok(index, 'FN')
        var, index = self.parse_variable(index)
        bnds, index = self.parse_fnbindings(index)
        _, index = self.expect_tok(index, 'COLON')
        typ, index = self.parse_type(index)
        _, index = self.expect_tok(index, 'LCURLY')
        stmts, index = self.parse_stmt_list(index)

        return FnCmd(var, bnds, typ, stmts), index

    def parse_arrayargument_seq(self, index, vals):
        var, index = self.parse_variable(index)
        vals.append(var)

        if self.peek_tok(index) == 'COMMA':
            _, index = self.expect_tok(index, 'COMMA')
            return self.parse_arrayargument_seq(index, vals)
        if self.peek_tok(index) == 'RSQUARE':
            _, index = self.expect_tok(index, 'RSQUARE')
            return vals, index

    def parse_arrayargument(self, index, var):
        _, index = self.expect_tok(index, 'LSQUARE')
        if self.peek_tok(index) == 'RSQUARE':
            _, index = self.expect_tok(index, 'RSQUARE')
            return ArrayArgument(var, []), index
        else:
            vrs, index = self.parse_arrayargument_seq(index, [])
            return ArrayArgument(var, vrs), index

    def parse_argument(self, index):
        var, index = self.parse_variable(index)
        if self.peek_tok(index) == 'LSQUARE':
            return self.parse_arrayargument(index, var)
        vaarg = VarArg(var)
        return vaarg, index

    def parse_intexpr(self, index):
        num, index = self.expect_tok(index, 'INTVAL')
        return self.parse_expr_cont(index, IntExpr(num))

    def parse_floatexpr(self, index):
        num, index = self.expect_tok(index, 'FLOATVAL')
        return self.parse_expr_cont(index, FloatExpr(num))

    def parse_variableexpr(self, index):
        var, index = self.parse_variable(index)
        varexp = VariableExpr(var)
        return self.parse_expr_cont(index, varexp)

    def parse_trueexpr(self, index):
        expr, index = self.expect_tok(index, 'TRUE')
        return self.parse_expr_cont(index, TrueExpr())

    def parse_falseexper(self, index):
        expr, index = self.expect_tok(index, 'FALSE')
        return self.parse_expr_cont(index, FalseExpr())

    def parse_callexpr_seq(self, index, vals):
        val, index = self.parse_expr(index)
        vals.append(val)

        if self.peek_tok(index) == 'COMMA':
            _, index = self.expect_tok(index, 'COMMA')
            return self.parse_callexpr_seq(index, vals)
        if self.peek_tok(index) == 'RPAREN':
            _, index = self.expect_tok(index, 'RPAREN')
            return vals, index

    def parse_callexpr(self, index, var):
        _, index = self.expect_tok(index, 'LPAREN')
        if self.peek_tok(index) == 'RPAREN':
            _, index = self.expect_tok(index, 'RPAREN')
            return CallExpr(var, []), index
        else:
            exprs, index = self.parse_callexpr_seq(index, [])
            return CallExpr(var, exprs), index

    def parse_arrayindexexpr_seq(self, index, exprs : []):
        val, index = self.parse_expr(index)
        exprs.append(val)

        if self.peek_tok(index) == 'COMMA':
            _, index = self.expect_tok(index, 'COMMA')
            return self.parse_arrayindexexpr_seq(index, exprs)
        if self.peek_tok(index) == 'RSQUARE':
            _, index = self.expect_tok(index, 'RSQUARE')
            return exprs, index

    def parse_arrayindexexpr(self, index, expr):
        _, index = self.expect_tok(index, 'LSQUARE')
        if self.peek_tok(index) == 'RSQUARE':
            _, index = self.expect_tok(index, 'RSQUARE')
            return ArrayIndexExpr(expr, []), index
        else:
            exprs, index = self.parse_arrayindexexpr_seq(index, [])
            return ArrayIndexExpr(expr, exprs), index

    def parse_tupleindexexpr(self, index, expr):
        _, index = self.expect_tok(index, 'LCURLY')
        num, index = self.expect_tok(index, 'INTVAL')
        _, index = self.expect_tok(index, 'RCURLY')
        return TupleIndexExpr(int(num), expr), index

    def parse_tupleliteralexpr_seq(self, index, vals):
        val, index = self.parse_expr(index)
        vals.append(val)

        if self.peek_tok(index) == 'COMMA':
            _, index = self.expect_tok(index, 'COMMA')
            return self.parse_tupleliteralexpr_seq(index, vals)
        if self.peek_tok(index) == 'RCURLY':
            _, index = self.expect_tok(index, 'RCURLY')
            return vals, index

    def parse_tupleliteralexpr(self, index):
        _, index = self.expect_tok(index, 'LCURLY')
        if self.peek_tok(index) == 'RCURLY':
            _, index = self.expect_tok(index, 'RCURLY')
            return self.parse_expr_cont(index, TupleLiteralExpr([]))
        else:
            exprs, index = self.parse_tupleliteralexpr_seq(index, [])
            return self.parse_expr_cont(index, TupleLiteralExpr(exprs))

    def parse_arrayliteralexpr_seq(self, index, vals):
        val, index = self.parse_expr(index)
        vals.append(val)

        if self.peek_tok(index) == 'COMMA':
            _, index = self.expect_tok(index, 'COMMA')
            return self.parse_arrayliteralexpr_seq(index, vals)
        if self.peek_tok(index) == 'RSQUARE':
            _, index = self.expect_tok(index, 'RSQUARE')
            return vals, index

    def parse_arrayliteralexpr(self, index):
        _, index = self.expect_tok(index, 'LSQUARE')
        if self.peek_tok(index) == 'RSQUARE':
            _, index = self.expect_tok(index, 'RSQUARE')
            return self.parse_expr_cont(index, ArrayLiteralExpr([]))
        else:
            exprs, index = self.parse_arrayliteralexpr_seq(index, [])
            return self.parse_expr_cont(index, ArrayLiteralExpr(exprs))

    def parse_parenexpr(self, index):
        _, index = self.expect_tok(index, 'LPAREN')
        expr, index = self.parse_expr(index)
        _, index = self.expect_tok(index, 'RPAREN')
        return self.parse_expr_cont(index, expr)

    def parse_expr_cont(self, index, expr):
        t = self.peek_tok(index)
        # <variable> ( <expr> , ... ) --> Call Expr
        if t == 'LPAREN' and type(expr) is VariableExpr:
            expr = expr.variable
            call, index = self.parse_callexpr(index, expr)
            return self.parse_expr_cont(index, call)
        # <expr> { <integer> }  --> Tuple Indexer
        elif t == 'LCURLY':
            tie, index = self.parse_tupleindexexpr(index, expr)
            return self.parse_expr_cont(index, tie)
        # <expr> [ <expr> , ... ] --> Array indexer
        elif t == 'LSQUARE':
            aie, index = self.parse_arrayindexexpr(index, expr)
            return self.parse_expr_cont(index, aie)
        return expr, index

    def parse_expr(self, index):
        t = self.peek_tok(index)
        if t == 'INTVAL':
            return self.parse_intexpr(index)
        elif t == 'FLOATVAL':
            return self.parse_floatexpr(index)
        elif t == 'VARIABLE':
            return self.parse_variableexpr(index)
        elif t == 'TRUE':
            return self.parse_trueexpr(index)
        elif t == 'FALSE':
            return self.parse_falseexper(index)
        # { <expr> , ... } --> Tuple Literal
        elif t == 'LCURLY':
            return self.parse_tupleliteralexpr(index)
        # [ <expr> , ... ] --> Array Literal
        elif t == 'LSQUARE':
            return self.parse_arrayliteralexpr(index)
        # ( <expr> ) --> Parenthasized expr
        elif t == 'LPAREN':
            return self.parse_parenexpr(index)
        else:
            ret = 'Unable to find an Expression at ' + str(index)
            raise ParserException(ret)

    def parse_inttype(self, index):
        _, index = self.expect_tok(index, 'INT')
        return self.parse_type_cont(index, IntType())

    def parse_floattype(self, index):
        _, index = self.expect_tok(index, 'FLOAT')
        return self.parse_type_cont(index, FloatType())

    def parse_booltype(self, index):
        _, index = self.expect_tok(index, 'BOOL')
        return self.parse_type_cont(index, BoolType())

    def parse_variabletype(self, index):
        var, index = self.parse_variable(index)
        return self.parse_type_cont(index, VarType(var))

    def parse_array_type_seq(self, index, count):
        _, index = self.expect_tok(index, 'COMMA')
        count += 1

        if self.peek_tok(index) == 'RSQUARE':
            _, index = self.expect_tok(index, 'RSQUARE')
            return count, index
        else:
            return self.parse_array_type_seq(index, count)

    def parse_array_type(self, index, in_type):
        _, index = self.expect_tok(index, 'LSQUARE')
        if self.peek_tok(index) == 'RSQUARE':
            _, index = self.expect_tok(index, 'RSQUARE')
            return ArrayType(in_type, 1), index
        else:
            count, index = self.parse_array_type_seq(index, 1)
            return ArrayType(in_type, count), index

    def parse_tuple_type_seq(self, index, typs : []):
        typ, index = self.parse_type(index)
        typs.append(typ)

        if self.peek_tok(index) == 'COMMA':
            _, index = self.expect_tok(index, 'COMMA')
            return self.parse_tuple_type_seq(index, typs)
        if self.peek_tok(index) == 'RCURLY':
            _, index = self.expect_tok(index, 'RCURLY')
            return typs, index

    def parse_tuple_type(self, index):
        _, index = self.expect_tok(index, 'LCURLY')
        if self.peek_tok(index) == 'RCURLY':
            _, index = self.expect_tok(index, 'RCURLY')
            return self.parse_type_cont(index, TupleType([]))
        else:
            res, index = self.parse_tuple_type_seq(index, [])
            return self.parse_type_cont(index, TupleType(res))

    def parse_type_cont(self, index, in_type):
        t = self.peek_tok(index)
        # <type> [ , ... ] --> Array type
        if t == 'LSQUARE':
            res, index = self.parse_array_type(index, in_type)
            return self.parse_type_cont(index, res)
        return in_type, index

    def parse_type(self, index):
        tp = self.peek_tok(index)
        if tp == 'INT':
            return self.parse_inttype(index)
        elif tp == 'FLOAT':
            return self.parse_floattype(index)
        elif tp == 'BOOL':
            return self.parse_booltype(index)
        elif tp == 'VARIABLE':
            return self.parse_variabletype(index)
        # { <type> , ... }  --> Tuple type
        elif tp == 'LCURLY':
            return self.parse_tuple_type(index)
        else:
            ret = 'Could not find a type at ' + str(index) + ' got ' + tp
            raise ParserException(ret)

    def parse_lvalue_tuple_seq(self, index, vals):
        val, index = self.parse_lvalue(index)
        vals.append(val)

        if self.peek_tok(index) == 'COMMA':
            _, index = self.expect_tok(index, 'COMMA')
            return self.parse_lvalue_tuple_seq(index, vals)
        if self.peek_tok(index) == 'RCURLY':
            _, index = self.expect_tok(index, 'RCURLY')
            return vals, index

    def parse_lvaluetuple(self, index):
        _, index = self.expect_tok(index, 'LCURLY')
        if self.peek_tok(index) == 'RCURLY':
            _, index = self.expect_tok(index, 'RCURLY')
            return TupleLValue([]), index

        vals, index = self.parse_lvalue_tuple_seq(index, [])
        return TupleLValue(vals), index

    def parse_lvalue(self, index):
        if self.peek_tok(index) == 'LCURLY':
            return self.parse_lvaluetuple(index)
        arg, index = self.parse_argument(index)
        lvalue = ArgLValue(arg)
        return lvalue, index

    def parse_variable(self, index):
        var, index = self.expect_tok(index, 'VARIABLE')
        return Variable(var), index
