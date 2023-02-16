from typecheckerheader import *
from parserheader import *


class TypeChecker:
    exprTree: []

    def __init__(self, _exprTree):
        self.exprTree = _exprTree

    def verify_program(self):
        for expr in self.exprTree:
            expr.ty = self.type_check(expr)

    def to_string(self):
        ret = ''
        for expr in self.exprTree:
            ret += expr.to_string() + '\n'

        return ret[:-1]

    def type_check(self, baseexpr: Expr):
        # literal checking
        if type(baseexpr) is FloatExpr:
            return FloatTy()
        elif type(baseexpr) is IntExpr:
            return IntTy()
        elif type(baseexpr) is TrueExpr:
            return BoolTy()
        elif type(baseexpr) is FalseExpr:
            return BoolTy()

        # compound checking
        elif type(baseexpr) is BinopExpr:
            lty = self.type_check(baseexpr.lexpr)
            rty = self.type_check(baseexpr.rexpr)
            if type(lty) is type(rty):
                baseexpr.lexpr.ty = lty
                baseexpr.rexpr.ty = rty

                if '+-/%*'.__contains__(baseexpr.op):
                    return lty
                else:
                    return BoolTy()

            else:
                ret = 'You cannot have an expression that operates on two different types! (' \
                      + lty.to_string() + ' ' + baseexpr.op + ' ' + rty.to_string() + ')'
                raise TypeCheckerException(ret)
        elif type(baseexpr) is UnopExpr:
            ty = self.type_check(baseexpr.expr)
            if baseexpr.op == '!' and type(ty) is not BoolTy:
                ret = 'You cannot use boolean negation (!) on non bool types! (' + ty.to_string() + ')'
                raise TypeCheckerException(ret)
            elif baseexpr.op == '-' and (type(ty) is not FloatTy and type(ty) is not IntTy):
                ret = 'You cannot use mathematical negation (-) on non mathematical types! (' + ty.to_string() + ')'
                raise TypeCheckerException(ret)
            else:
                baseexpr.expr.ty = ty
                baseexpr.ty = ty
                return ty
        elif type(baseexpr) is IfExpr:
            ifty = self.type_check(baseexpr.ifexp)
            if type(ifty) is not BoolTy:
                ret = 'You must have a boolean expression as your first argument to an if expression (' \
                      + ifty.to_string() + ')'
                raise TypeCheckerException(ret)

            thenty = self.type_check(baseexpr.thenexp)
            elsety = self.type_check(baseexpr.elseexp)
            #TODO: probably insufficient
            if not thenty.equals(elsety):
                ret = 'Your then and else expressions must have the same type! (' \
                      + thenty.to_string() + ' ' + elsety.to_string() + ')'
                raise TypeCheckerException(ret)

            baseexpr.ifexp.ty = ifty
            baseexpr.thenexp.ty = thenty
            baseexpr.elseexp.ty = elsety
            return thenty
        elif type(baseexpr) is TupleLiteralExpr:
            tylist = []
            for val in baseexpr.types:
                currty = self.type_check(val)
                tylist.append(currty)
                val.ty = currty
            return TupleTy(tylist)
        elif type(baseexpr) is ArrayLiteralExpr:
            tylist = []
            keeper = []
            for val in baseexpr.types:
                currty = self.type_check(val)
                tylist.append(currty)
                val.ty = currty
                keeper.append(type(currty))

            uniquness = set(keeper)
            if len(uniquness) > 1:
                ret = 'You cannot have multiple types in an array literal declaration ('
                for ty in tylist:
                    ret += ty.to_string() + ', '
                raise TypeCheckerException(ret[:-2] + ')')

            return ArrayTy(tylist[0], 1)    # TODO modular? for >1 rank arrays
        elif type(baseexpr) is TupleIndexExpr:
            ty = self.type_check(baseexpr.varxpr)
            size = len(ty.tys)
            if 0 < baseexpr.index > size - 1:
                ret = 'You cannot access outside of the tuple literals bounds (' + str(size) + \
                      ' is incompatible with ' + str(baseexpr.index - 1) + ')'
                raise TypeCheckerException(ret)
            baseexpr.varxpr.ty = ty
            return ty.tys[baseexpr.index]
        elif type(baseexpr) is ArrayIndexExpr:
            valuetys = self.type_check(baseexpr.expr)

            baseexpr.expr.ty = valuetys

            if len(baseexpr.exprs) > valuetys.rank:
                ret = 'You cannot access an array of rank ' + str(valuetys.rank) + ' at rank ' + str(len(baseexpr.exprs))
                raise TypeCheckerException(ret)

            for val in baseexpr.exprs:
                ty = self.type_check(val)
                if type(ty) is not IntTy:
                    ret = 'You cannot access an array using a non integer! (' + ty.to_string() + ')'
                    raise TypeCheckerException(ret)
                val.ty = ty

            return valuetys.ty
        elif type(baseexpr) is VariableExpr and baseexpr.variable.to_string() == 'pict.':
            return ArrayTy(TupleTy([FloatTy(), FloatTy(), FloatTy(), FloatTy()]), 2)

        # command checking
        elif type(baseexpr) is ShowCmd:
            showexpr = baseexpr.expr
            ty = self.type_check(showexpr)
            showexpr.ty = ty
            return ty
