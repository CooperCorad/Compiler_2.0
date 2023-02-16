import math

from typecheckerheader import Ty

precedence = [['array', 'sum', 'if'],
                ['&&', '||'],
                ['<', '<=', '==', '!=', '>=', '>'],
                ['+', '-'],
                ['*', '/', '%'],
                ['!', '-'],
                ['{', '[']]



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
    ty = None

    def __init__(self, _intVal: str):
        self.intVal = int(_intVal)
        if self.intVal < -pow(2, 63) or self.intVal > ((pow(2, 63)) - 1):
            raise ParserException("You cannot have an int beyond the ranges -2^63 <-> 2^63 - 1")

    def to_string(self):
        typestr = ''
        if self.ty is not None:
            typestr = self.ty.to_string() + ' '
        ret = '(IntExpr ' + typestr + str(self.intVal) + ')'
        return ret


class FloatExpr(Expr):
    floatVal: float
    ty = None

    def __init__(self, _floatVal: str):
        self.floatVal = float(_floatVal)
        if math.isnan(self.floatVal) or math.isinf(self.floatVal):
            raise ParserException("You cannot have an infinite or NaN float (likely a divide by Zero issue!")

    def to_string(self):
        typestr = ''
        if self.ty is not None:
            typestr = self.ty.to_string() + ' '
        ret = '(FloatExpr ' + typestr + str(int(self.floatVal)) + ')'
        return ret


class TrueExpr(Expr):
    ty = None

    def to_string(self):
        typestr = ''
        if self.ty is not None:
            typestr = ' ' + self.ty.to_string()
        ret = '(TrueExpr' + typestr + ')'
        return ret


class FalseExpr(Expr):
    ty = None

    def to_string(self):
        typestr = ''
        if self.ty is not None:
            typestr = ' ' + self.ty.to_string()
        ret = '(FalseExpr' + typestr + ')'
        return ret


class VariableExpr(Expr):
    variable: Variable
    ty = None

    def __init__(self, _variable: Variable):
        self.variable = _variable

    def to_string(self):
        typestr = ''
        if self.ty is not None:
            typestr = ' ' + self.ty.to_string()
        ret = '(VarExpr ' + typestr + self.variable.to_string() + ')'
        return ret


class TupleIndexExpr(Expr):
    index : int
    varxpr : Expr
    ty = None

    def __init__(self, _index : int, _varxpr : Expr):
        self.index = _index
        self.varxpr = _varxpr

    def to_string(self):
        typestr = ''
        if self.ty is not None:
            typestr = ' ' + self.ty.to_string()
        ret = '(TupleIndexExpr ' + typestr + self.varxpr.to_string() + ' ' + str(self.index) + ')'
        return ret


class ArrayIndexExpr(Expr):
    expr : Expr
    exprs : []
    ty = None

    def __init__(self, _expr : Expr, _exprs : []):
        self.expr = _expr
        self.exprs = _exprs

    def to_string(self):
        typestr = ''
        if self.ty is not None:
            typestr = self.ty.to_string() + ' '
        ret = '(ArrayIndexExpr ' + typestr
        if self.expr is not None:
            ret += self.expr.to_string() + ' '
        for exp in self.exprs:
            ret += exp.to_string() + ' '
        ret = ret[:-1] + ')'
        return ret


class CallExpr(Expr):
    exprs : []
    ty = None

    def __init__(self, _variable, _vals : []):
        self.variable = _variable
        self.exprs = _vals

    def to_string(self):
        typestr = ''
        if self.ty is not None:
            typestr = self.ty.to_string() + ' '
        ret = '(CallExpr ' + typestr + self.variable.to_string() + ' '
        for exp in self.exprs:
            ret += exp.to_string() + ' '
        ret = ret[:-1] + ')'
        return ret


class UnopExpr(Expr):
    op : str
    expr : Expr
    ty = None

    def __init__(self, _op : str, _expr : Expr):
        self.op = _op
        self.expr = _expr

    def to_string(self):
        typestr = ''
        if self.ty is not None:
            typestr = self.ty.to_string() + ' '
        ret = '(UnopExpr ' + typestr + self.op + ' ' + self.expr.to_string() + ')'
        return ret


class BinopExpr(Expr):
    op: str
    lexpr: Expr
    rexpr: Expr
    ty = None

    def __init__(self, _op: str, _lexpr: Expr, _rexpr: Expr):
        self.op = _op
        self.lexpr = _lexpr
        self.rexpr = _rexpr

    def to_string(self):
        typestr = ''
        if self.ty is not None:
            typestr = self.ty.to_string() + ' '
        ret = '(BinopExpr ' + typestr + self.lexpr.to_string() + ' ' + self.op + ' ' + self.rexpr.to_string() + ')'
        return ret


class IfExpr(Expr):
    ifexp : Expr
    thenexp : Expr
    elseexp: Expr
    ty = None

    def __init__(self, _ifexp : Expr, _thenexp : Expr, _elseexp : Expr):
        self.ifexp = _ifexp
        self.thenexp = _thenexp
        self.elseexp = _elseexp

    def to_string(self):
        typestr = ''
        if self.ty is not None:
            typestr = self.ty.to_string() + ' '
        ret = '(IfExpr ' + typestr + self.ifexp.to_string() + ' ' + self.thenexp.to_string() + ' ' + self.elseexp.to_string() + ')'
        return ret


class ArrayLoopExpr(Expr):
    pairs : [(Variable, Expr)]
    expr : Expr
    ty = None

    def __init__(self, _pairs : [(Variable, Expr)], _expr : Expr):
        self.pairs = _pairs
        self.expr = _expr

    def to_string(self):
        typestr = ''
        if self.ty is not None:
            typestr = self.ty.to_string()
        ret = '(ArrayLoopExpr ' + typestr
        for pair in self.pairs:
            ret += pair[0].to_string() + ' ' + pair[1].to_string() + ' '
        ret = ret[:-1] + ' ' + self.expr.to_string() + ')'
        return ret


class SumLoopExpr(Expr):
    pairs : [(Variable, Expr)]
    expr : Expr
    ty = None

    def __init__(self, _pairs : [(Variable, Expr)], _expr : Expr):
        self.pairs = _pairs
        self.expr = _expr

    def to_string(self):
        typestr = ''
        if self.ty is not None:
            typestr = self.ty.to_string()
        ret = '(SumLoopExpr ' + typestr
        for pair in self.pairs:
            ret += pair[0].to_string() + ' ' + pair[1].to_string() + ' '
        ret = ret[:-1] + ' ' + self.expr.to_string() + ')'
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
    ty = None

    def __init__(self, _types : []):
        self.types = _types

    def to_string(self):
        typestr = ''
        if self.ty is not None:
            typestr = self.ty.to_string() + ' '
        ret = '(TupleLiteralExpr ' + typestr
        for typ in self.types:
            ret += typ.to_string() + ' '
        ret = ret[:-1] + ')'
        return ret


class ArrayLiteralExpr(Expr):
    types : []
    ty = None

    def __init__(self, _types : []):
        self.types = _types

    def to_string(self):
        typestr = ''
        if self.ty is not None:
            typestr = self.ty.to_string() + ' '
        ret = '(ArrayLiteralExpr ' + typestr
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

