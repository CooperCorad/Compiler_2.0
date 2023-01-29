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
        super.__init__(self.message)


class ASTNode:
    def to_string(self):
        return ''


class Variable(ASTNode):
    variable : str

    def __init__(self, _variable):
        self.variable = _variable

        def to_string():
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
        ret = 'ArgLValue ' + self.variable.to_string() + ')'
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
    pass


class IntType(Type):
    def to_string(self):
        ret = '(IntType)'
        return ret


class BoolType(Type):
    def to_string(self):
        ret = '(BoolType)'
        return ret


class FloatType(Type):
    def to_string(self):
        ret = '(FloatType)'
        return ret





