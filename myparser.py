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
    vairable: Variable

    def __init__(self, _variable: Variable):
        self.vairable = _variable

    def to_string(self):
        ret = '(VarType ' + self.vairable.to_string() + ')'
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
        num = 0
        for cmd in self.program:
            print(num)
            num += 1
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

    # time <cmd>
    def parse_timecmd(self, index):
        _, index = self.expect_tok(index, 'TIME')
        cmd, index = self.parse_cmd(index)
        return TimeCmd(cmd), index

    def parse_binding_tuple(self, index, vals : []):
        if self.peek_tok(index) == 'COMMA':
            _, index = self.expect_tok(index, 'COMMA')
            if self.peek_tok(index) == 'RCURLY':
                raise ParserException('You cannot have hanging comma on binding tuple at ' + str(index))
        if self.peek_tok(index) == 'RCURLY':
            _, index = self.expect_tok(index, 'RCURLY')
            return vals, index
        else:
            val, index = self.parse_binding(index)
            vals.append(val)
            return self.parse_binding_tuple(index, vals)

    def parse_binding(self, index):
        if self.peek_tok(index) == 'LCURLY':
            _, index = self.expect_tok(index, 'LCURLY')
            bndtp, index = self.parse_binding_tuple(index, [])
            return TupleBinding(bndtp), index
        arg, index = self.parse_argument(index)
        _, index = self.expect_tok(index, 'COLON')
        typ, index = self.parse_type(index)
        return VarBinding(arg, typ), index

    def parse_binding_seq_cont(self, index, vals : []):
        bnd, index = self.parse_binding(index)
        vals.append(bnd)

        if self.peek_tok(index) == 'COMMA':
            _, index = self.expect_tok(index, 'COMMA')
            return self.parse_binding_seq_cont(index, vals)
        if self.peek_tok(index) == 'RPAREN':
            _, index = self.expect_tok(index, 'RPAREN')
            return vals, index

    def parse_binding_seq(self, index):
        _, index = self.expect_tok(index, 'LPAREN')
        bnds, index = self.parse_binding_seq_cont(index, [])
        return bnds, index

    def parse_letstmt(self, index):
        _, index = self.expect_tok(index, 'LET')
        lval, index = self.parse_lvalue(index)
        _, index = self.expect_tok(index, 'EQUALS')
        expr, index = self.parse_expr(index)
        ret = LetStmt(lval, expr)
        return ret, index

    def parse_assertstmt(self, index):
        _, index = self.expect_tok(index, 'ASSERT')
        expr, index = self.parse_expr(index)
        _, index = self.expect_tok(index, 'COMMA')
        string, index = self.expect_tok(index, 'STRING')
        ret = AssertStmt(expr, string)
        return ret, index

    def parse_returnstmt(self, index):
        _, index = self.expect_tok(index, 'RETURN')
        expr, index = self.parse_expr(index)
        ret = ReturnStmt(expr)
        return ret, index

    def parse_stmt(self, index):
        t = self.peek_tok(index)

        if t == 'LET':
            return self.parse_letstmt(index)
        elif t == 'ASSERT':
            return self.parse_assertstmt(index)
        elif t == 'RETURN':
            return self.parse_returnstmt(index)
        else:
            raise ParserException('No statement could be found at ' + str(index))

    def parse_stmt_seq_cont(self, index, vals : []):
        if self.peek_tok(index) == 'RCURLY':
            return vals, index
        else:
            stmt, index = self.parse_stmt(index)
            _, index = self.expect_tok(index, 'NEWLINE')
            vals.append(stmt)
            return self.parse_stmt_seq_cont(index, vals)

    def parse_stmt_seq(self, index):
        x, y = self.parse_stmt_seq_cont(index, [])
        return x, y

    def parse_fncmd(self, index):
        _, index = self.expect_tok(index, 'FN')
        var, index = self.expect_tok(index, 'VARIABLE')
        var = Variable(var)                             # TODO which to chose?
        # var, index = self.parse_variable(index)
        bnds, index = self.parse_binding_seq(index)
        _, index = self.expect_tok(index, 'COLON')
        typ, index = self.parse_type(index)
        _, index = self.expect_tok(index, 'LCURLY')
        _, index = self.expect_tok(index, 'NEWLINE')
        stmts, index = self.parse_stmt_seq(index)
        _, index = self.expect_tok(index, 'RCURLY')
        return FnCmd(var, bnds, typ, stmts), index

    def parse_array_argument(self, vals : [], index : int):
        if self.peek_tok(index) == 'COMMA':
            _, index = self.expect_tok(index, 'COMMA')
            if self.peek_tok(index) == 'RSQUARE':
                raise ParserException('Cannot have hanging comma at ' + str(index))
        if self.peek_tok(index) == 'RSQUARE':
            _, index = self.expect_tok(index, 'RSQUARE')
            return vals, index
        else:
            var, index = self.parse_variable(index)
            vals.append(var)
            return self.parse_array_argument(vals, index)

    def parse_argument_cont(self, var : Variable, index : int):
        if self.peek_tok(index) == 'LSQUARE':
            _, index = self.expect_tok(index, 'LSQUARE')
            args, index = self.parse_array_argument([], index)
            ret = ArrayArgument(var, args)
            return ret, index
        else:
            return var, index

    def parse_argument(self, index):
        arg, index = self.expect_tok(index, 'VARIABLE')
        var = VarArg(Variable(arg))
        ret, index = self.parse_argument_cont(var, index)
        if type(ret) is ArrayArgument:
            ret.var = Variable(arg)
        return ret, index

    def parse_tuple_literal_seq(self, types : [], index : int):
        if self.peek_tok(index) == 'COMMA':
            index += 1
        if self.peek_tok(index) == 'RCURLY':
            index += 1
            return types, index
        else:
            typ, index = self.parse_expr(index)
            types.append(typ)
            # _, index = self.expect_tok(index, 'COMMA')
            return self.parse_tuple_literal_seq(types, index)

    def parse_intexpr(self, index):
        num, index = self.expect_tok(index, 'INTVAL')
        return self.parse_expr_cont(index, IntExpr(num))

    def parse_floatexpr(self, index):
        num, index = self.expect_tok(index, 'FLOATVAL')
        return self.parse_expr_cont(index, FloatExpr(num))

    def parse_call_seq(self, index, vals : []):
        val, index = self.parse_expr(index)
        vals.append(val)

        if self.peek_tok(index) == 'COMMA':
            _, index = self.expect_tok(index, 'COMMA')
            return self.parse_call_seq(index, vals)
        if self.peek_tok(index) == 'RPAREN':
            _, index = self.expect_tok(index, 'RPAREN')
            return vals, index

    def parse_callexpr(self, index, varxpr):
        if self.peek_tok(index) == 'LPAREN':
            _, index = self.expect_tok(index, 'LPAREN')
            if self.peek_tok(index) == 'RPAREN':
                _, index = self.expect_tok(index, 'RPAREN')
                return CallExpr(varxpr, []), index
            exprs, index = self.parse_call_seq(index, [])
            return CallExpr(varxpr, exprs), index

        return varxpr, index

    def parse_variableexpr_cont(self, index):
        string, index = self.expect_tok(index, 'VARIABLE')
        var = Variable(string)

        var, index = self.parse_callexpr(index, var)
        return var, index

    def parse_variableexpr(self, index):
        var, index = self.parse_variableexpr_cont(index)
        if type(var) is not CallExpr:
            var = VariableExpr(var)
        return self.parse_expr_cont(index, var)

    def parse_trueexpr(self, index):
        _, index = self.expect_tok(index, 'TRUE')
        return self.parse_expr_cont(index, TrueExpr())

    def parse_falseexpr(self, index):
        _, index = self.expect_tok(index, 'FALSE')
        return self.parse_expr_cont(index, FalseExpr())

    def parse_tuple_index_expr(self, index, vaarg):
        _, index = self.expect_tok(index, 'LCURLY')
        lookahead = index + 1
        if self.peek_tok(index) == 'INTVAL' and self.peek_tok(lookahead) == 'RCURLY':
            num, index = self.expect_tok(index, 'INTVAL')
            _, index = self.expect_tok(index, 'RCURLY')
            ret = TupleIndexExpr(int(num), vaarg)
            if self.peek_tok(index) == 'LCURLY':
                return self.parse_tuple_index_expr(index, ret)
            return ret, index

    def parse_array_index_expr_cont(self, index, vals: []):
        val, index = self.parse_expr(index)
        vals.append(val)

        if self.peek_tok(index) == 'COMMA':
            _, index = self.expect_tok(index, 'COMMA')
            return self.parse_array_index_expr_cont(index, vals)

        if self.peek_tok(index) == 'RSQUARE':
            _, index = self.expect_tok(index, 'RSQUARE')
            return vals, index

    def parse_array_index_expr(self, index, vaarg):
        _, index = self.expect_tok(index, 'LSQUARE')
        if self.peek_tok(index) == 'RSQUARE':
            _, index = self.expect_tok(index, 'RSQUARE')
            return ArrayIndexExpr(vaarg, []), index
        vals, index = self.parse_array_index_expr_cont(index, [])
        ret = ArrayIndexExpr(vaarg, vals)
        if self.peek_tok(index) == 'LSQUARE':
            return self.parse_array_index_expr(index, ret)
        return ret, index

    def parse_array_literal_expr(self, index):
        _, index = self.expect_tok(index, 'LSQUARE')
        if self.peek_tok(index) == 'RSQUARE':
            _, index = self.expect_tok(index, 'RSQUARE')
            return ArrayLiteralExpr([]), index
        vals, index = self.parse_array_index_expr_cont(index, [])
        ret = ArrayLiteralExpr(vals)
        return ret, index

    def parse_expr_cont(self, index, vaarg):
        if self.peek_tok(index) == 'LCURLY':
            return self.parse_tuple_index_expr(index, vaarg)
        elif self.peek_tok(index) == 'LSQUARE':
            return self.parse_array_index_expr(index, vaarg)
        return vaarg, index

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
            return self.parse_falseexpr(index)
        elif t == 'LCURLY':
            index += 1
            types, index = self.parse_tuple_literal_seq([], index)
            ret = TupleLiteralExpr(types)
            return ret, index
        elif t == 'LSQUARE':
            arlit, index = self.parse_array_literal_expr(index)
            return arlit, index
        elif t == 'LPAREN':
            _, index = self.expect_tok(index, 'LPAREN')
            expr, index = self.parse_expr(index)
            _, index = self.expect_tok(index, 'RPAREN')
            return expr, index
        else:
            ret = 'Unable to find an Expression at ' + str(index)
            raise ParserException(ret)

    def parse_array_type_seq(self, typ : Type, index : int, count : int):
        if self.peek_tok(index) == 'RSQUARE':
            _, index = self.expect_tok(index, 'RSQUARE')
            return ArrayType(typ, count), index
        elif self.peek_tok(index) == 'COMMA':
            index += 1
            count += 1
            return self.parse_array_type_seq(typ, index, count)

    def parse_tuple_type_seq(self, types : [], index : int):
        typ, index = self.parse_type(index)
        types.append(typ)

        if self.peek_tok(index) == 'COMMA':
            _, index = self.expect_tok(index, 'COMMA')
            return self.parse_tuple_type_seq(types, index)
        if self.peek_tok(index) == 'RCURLY':
            _, index = self.expect_tok(index, 'RCURLY')
            return types, index



    def parse_type_cont(self, typ : Type, index):
        if self.peek_tok(index) == 'LSQUARE':
            _, index = self.expect_tok(index, 'LSQUARE')
            return self.parse_array_type_seq(typ, index, 1)
        else:
            return typ, index

    def parse_inttype(self, index):
        _, index = self.expect_tok(index, 'INT')
        ret, index = self.parse_type_cont(IntType(), index)
        return ret, index

    def parse_floattype(self, index):
        _, index = self.expect_tok(index, 'FLOAT')
        ret, index = self.parse_type_cont(FloatType(), index)
        return ret, index

    def parse_booltype(self, index):
        _, index = self.expect_tok(index, 'BOOL')
        ret, index = self.parse_type_cont(BoolType(), index)
        return ret, index

    def parse_variable(self, index):
        string, index = self.expect_tok(index, 'VARIABLE')
        var = Variable(string)
        var, index = self.parse_type_cont(var, index)

        # ret, index = self.parse_type_cont(VarType(var), index)
        # return ret, index
        return var, index

    def parse_type(self, index):
        tp = self.peek_tok(index)
        if tp == 'INT':
            return self.parse_inttype(index)
        elif tp == 'FLOAT':
            return self.parse_floattype(index)
        elif tp == 'BOOL':
            return self.parse_booltype(index)
        elif tp == 'VARIABLE':
            var, index = self.parse_variable(index)
            if type(var) is not ArrayType:
                var = VarType(var)
            if type(var) is ArrayType:
                var.type = VarType(var.type)
            return var, index
        elif tp == 'LCURLY':
            index += 1
            types, index = self.parse_tuple_type_seq([], index)
            return TupleType(types), index
        else:
            ret = 'Could not find a type at ' + str(index)
            raise ParserException(ret)

    def parse_lvalue_cont(self, vals : [], index : int):
        if self.peek_tok(index) == 'COMMA':
            _, index = self.expect_tok(index, 'COMMA')
            if self.peek_tok(index) == 'RCURLY':
                raise ParserException('No hanging commas on your Tuples at: ' + str(index))
        if self.peek_tok(index) == 'RCURLY':
            _, index = self.expect_tok(index, 'RCURLY')
            return vals, index
        else:
            lval, index = self.parse_lvalue(index)
            vals.append(lval)
            return self.parse_lvalue_cont(vals, index)

    def parse_lvalue(self, index):
        t = self.peek_tok(index)
        if t == 'VARIABLE':
            val, index = self.parse_argument(index)
            ret = ArgLValue(val)
            return ret, index
        elif t == 'LCURLY':
            _, index = self.expect_tok(index, 'LCURLY')
            vals, index = self.parse_lvalue_cont([], index)
            return TupleLValue(vals), index












