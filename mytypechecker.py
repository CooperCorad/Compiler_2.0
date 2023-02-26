from typecheckerheader import *
from parserheader import *
from symboltable import *

globaltable = SymbolTable()


class TypeChecker:
    exprTree: []

    def __init__(self, _exprtree):
        self.exprTree = _exprtree
        self.init_globaltable(globaltable)

    def init_globaltable(self, table: SymbolTable):
        table.addinfo('args', VariableInfo(ArrayResolvedType(IntResolvedType(), 1)))
        table.addinfo('argnum', VariableInfo(IntResolvedType()))

    def type_check(self):
        global globaltable
        # TODO command processing separation
        for expr in self.exprTree:
            expr.ty = self.type_of(expr, globaltable)

        return globaltable

    def to_string(self):
        ret = ''
        for expr in self.exprTree:
            ret += expr.to_string() + '\n'
        return ret[:-1]

    def type_of(self, baseexpr: Expr, table: SymbolTable):

        # literal checking
        if type(baseexpr) is FloatExpr:
            return FloatResolvedType()
        elif type(baseexpr) is IntExpr:
            return IntResolvedType()
        elif type(baseexpr) is TrueExpr:
            return BoolResolvedType()
        elif type(baseexpr) is FalseExpr:
            return BoolResolvedType()

        # Name Checking
        elif type(baseexpr) is VariableExpr:
            if table.hasinfo(baseexpr.variable.variable):
                info = table.getinfo(baseexpr.variable.variable)
                if type(info) is VariableInfo:
                    return info.rt
                else:
                    ret = 'This value is not a variable (' + type(info) + ')'
                    raise TypeCheckerException(ret)
            else:
                ret = 'Unknown variable ' + baseexpr.to_string()
                raise TypeCheckerException(ret)
        # compound checking
        elif type(baseexpr) is BinopExpr:
            lty = self.type_of(baseexpr.lexpr, table)
            rty = self.type_of(baseexpr.rexpr, table)
            if type(lty) is type(rty):
                baseexpr.lexpr.ty = lty
                baseexpr.rexpr.ty = rty
                if '+-/%*'.__contains__(baseexpr.op):
                    return lty
                else:
                    return BoolResolvedType()
            else:
                ret = 'You cannot have an expression that operates on two different types! (' \
                      + lty.to_string() + ' ' + baseexpr.op + ' ' + rty.to_string() + ')'
                raise TypeCheckerException(ret)
        elif type(baseexpr) is UnopExpr:
            expty = self.type_of(baseexpr.expr, table)
            if baseexpr.op == '!' and type(expty) is not BoolResolvedType:
                ret = 'You cannot use boolean negation (!) on non bool types! (' + expty.to_string() + ')'
                raise TypeCheckerException(ret)
            elif baseexpr.op == '-' and (type(expty) is not FloatResolvedType and type(expty) is not IntResolvedType):
                ret = 'You cannot use mathematical negation (-) on non mathematical types! (' + expty.to_string() + ')'
                raise TypeCheckerException(ret)
            else:
                baseexpr.expr.ty = expty
                baseexpr.ty = expty
                return expty
        elif type(baseexpr) is IfExpr:
            ifty = self.type_of(baseexpr.ifexp, table)
            if type(ifty) is not BoolResolvedType:
                ret = 'You must have a boolean expression as your first argument to an if expression (' \
                      + ifty.to_string() + ')'
                raise TypeCheckerException(ret)

            thenty = self.type_of(baseexpr.thenexp, table)
            elsety = self.type_of(baseexpr.elseexp, table)

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
                currty = self.type_of(val, table)
                tylist.append(currty)
                val.ty = currty
            return TupleResolvedType(tylist)
        elif type(baseexpr) is ArrayLiteralExpr:
            tylist = []
            keeper = []
            for val in baseexpr.types:
                currty = self.type_of(val, table)
                tylist.append(currty)
                val.ty = currty
                keeper.append(type(currty))

            uniqueness = set(keeper)
            if len(uniqueness) > 1:
                ret = 'You cannot have multiple types in an array literal declaration ('
                for expty in tylist:
                    ret += expty.to_string() + ', '
                raise TypeCheckerException(ret[:-2] + ')')

            return ArrayResolvedType(tylist[0], 1)    # TODO modular? for >1 rank arrays
        elif type(baseexpr) is TupleIndexExpr:
            expty = self.type_of(baseexpr.varxpr, table)
            size = len(expty.tys)
            if 0 < baseexpr.index > size - 1:
                ret = 'You cannot access outside of the tuple literals bounds (' + str(size) + \
                      ' is incompatible with ' + str(baseexpr.index) + ')'
                raise TypeCheckerException(ret)
            baseexpr.varxpr.ty = expty
            return expty.tys[baseexpr.index]
        elif type(baseexpr) is ArrayIndexExpr:
            valuetys = self.type_of(baseexpr.expr, table)
            baseexpr.expr.ty = valuetys
            if len(baseexpr.exprs) != valuetys.rank:
                ret = 'You cannot access an array of rank ' + str(valuetys.rank) + ' at access rank ' + str(len(baseexpr.exprs))
                raise TypeCheckerException(ret)

            for val in baseexpr.exprs:
                expty = self.type_of(val, table)
                if type(expty) is not IntResolvedType:
                    ret = 'You cannot access an array using a non integer! (' + expty.to_string() + ')'
                    raise TypeCheckerException(ret)
                val.ty = expty

            return valuetys.ty
        elif type(baseexpr) is ArrayLoopExpr:
            if len(baseexpr.pairs) < 1:
                ret = 'You cannot loop through a 0 rank array!'
                raise TypeCheckerException(ret)
            arraytable = table.makechild()
            for pair in baseexpr.pairs:
                expty = self.type_of(pair[1], arraytable)
                if type(expty) is not IntResolvedType:
                    raise TypeCheckerException('You cannot iterate through arrays with non int increments ' + expty.to_string())
                pair[1].ty = expty
            for pair in baseexpr.pairs:
                if type(pair[0]) is Variable:
                    arraytable.addinfo(pair[0].variable, VariableInfo(IntResolvedType()))
            loopty = self.type_of(baseexpr.expr, arraytable)
            baseexpr.expr.ty = loopty
            return ArrayResolvedType(loopty, len(baseexpr.pairs))
        elif type(baseexpr) is SumLoopExpr:
            if len(baseexpr.pairs) < 1:
                ret = 'You cannot loop through a 0 rank array!'
                raise TypeCheckerException(ret)
            sumlooptable = table.makechild()
            for pair in baseexpr.pairs:
                expty = self.type_of(pair[1], table)
                if type(expty) is not IntResolvedType:
                    raise TypeCheckerException(
                        'You cannot iterate through arrays with non int increments ' + expty.to_string())
                pair[1].ty = expty
            for pair in baseexpr.pairs:
                if type(pair[0]) is Variable:
                    sumlooptable.addinfo(pair[0].variable, VariableInfo(IntResolvedType()))
            loopty = self.type_of(baseexpr.expr, sumlooptable)
            if type(loopty) is not IntResolvedType and type(loopty) is not FloatResolvedType:
                ret = 'You cannot sum on non mathematical types (Int or Float) you are using ' + loopty.to_string() + ' ' + baseexpr.to_string()
                raise TypeCheckerException(ret)

            baseexpr.expr.ty = loopty

            return loopty
        # command checking
        elif type(baseexpr) is ShowCmd:
            showexpr = baseexpr.expr
            expty = self.type_of(showexpr, table)
            showexpr.ty = expty
            return expty
        # TODO iffy on these?
        elif type(baseexpr) is AssertCmd:
            assertexpr = baseexpr.expr
            expty = self.type_of(assertexpr, table)
            if type(expty) is not BoolResolvedType:
                raise TypeCheckerException('Assert must evaluate a boolean expression, not ' + expty.to_string())
            assertexpr.ty = expty
            return expty
        elif type(baseexpr) is TimeCmd:
            return self.type_of(baseexpr.cmd, table)
        elif type(baseexpr) is WriteCmd:
            writeexpr = baseexpr.expr
            expty = self.type_of(writeexpr, table)
            imgty = ArrayResolvedType(TupleResolvedType([FloatResolvedType(), FloatResolvedType(), FloatResolvedType(), FloatResolvedType()]), 2)
            if not imgty.equals(expty):
                ret = 'You cannot write a non {float, float, float, float}[,] to an image!'
                raise TypeCheckerException(ret
                                           )
            writeexpr.ty = expty
            return expty
        elif type(baseexpr) is LetCmd:
            letexpr = baseexpr.expr
            expty = self.type_of(letexpr, table)
            # TODO add to symtbl
            table.addlval(baseexpr.lvalue, expty)
            letexpr.ty = expty
            return expty
        elif type(baseexpr) is ReadCmd:
            imgty = ArrayResolvedType(TupleResolvedType([FloatResolvedType(), FloatResolvedType(), FloatResolvedType(), FloatResolvedType()]), 2)
            if type(baseexpr.vararg) is VarArg:
                table.addinfo(baseexpr.vararg.variable.variable, VariableInfo(imgty))
            elif type(baseexpr.vararg) is ArrayArgument:
                if len(baseexpr.vararg.arguments) != 2:
                    ret = 'Cannot bind image (type ' + imgty.to_string() + ') to ' + baseexpr.vararg.to_string() + ') (your array dimensions do not match!)'
                    raise TypeCheckerException(ret)
                for args in baseexpr.vararg.arguments:
                    table.addinfo(args.variable, VariableInfo(IntResolvedType()))
                table.addinfo(baseexpr.vararg.var.variable, VariableInfo(imgty))
            else:
                ret = 'Cannot bind image (type ' + imgty.to_string() + ') to ' + baseexpr.vararg.to_string()
                raise TypeCheckerException(ret)
            return imgty
