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

        for expr in self.exprTree:
            expr.ty = self.type_of(expr, globaltable)

        return globaltable

    def to_string(self):
        ret = ''
        for expr in self.exprTree:
            ret += expr.to_string() + '\n'

        return ret[:-1]

    def addlval(self, lval: ArgLValue, table: SymbolTable, ty: ResolvedType):
        if issubclass(ArgLValue, type(lval)):
            if type(lval.variable) is VarArg:
                name = lval.variable.variable.variable
                table.addinfo(name, VariableInfo(ty))
            elif isinstance(lval.variable, ArrayArgument):
                name = lval.variable.var.variable
                table.addinfo(name, VariableInfo(ty))

    def addtuplelval(self, lval: TupleLValue, table: SymbolTable, ty: ResolvedType):
        for i in range(len(lval.variables)):
            if type(lval.variables[i]) is TupleLValue:
                self.addtuplelval(lval.variables[i], table, ty.tys[i])
            self.addlval(lval.variables[i], table, ty.tys[i])

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
            ty = self.type_of(baseexpr.expr, table)
            if baseexpr.op == '!' and type(ty) is not BoolResolvedType:
                ret = 'You cannot use boolean negation (!) on non bool types! (' + ty.to_string() + ')'
                raise TypeCheckerException(ret)
            elif baseexpr.op == '-' and (type(ty) is not FloatResolvedType and type(ty) is not IntResolvedType):
                ret = 'You cannot use mathematical negation (-) on non mathematical types! (' + ty.to_string() + ')'
                raise TypeCheckerException(ret)
            else:
                baseexpr.expr.ty = ty
                baseexpr.ty = ty
                return ty
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
                for ty in tylist:
                    ret += ty.to_string() + ', '
                raise TypeCheckerException(ret[:-2] + ')')

            return ArrayResolvedType(tylist[0], 1)    # TODO modular? for >1 rank arrays
        elif type(baseexpr) is TupleIndexExpr:
            ty = self.type_of(baseexpr.varxpr, table)
            size = len(ty.tys)
            if 0 < baseexpr.index > size - 1:
                ret = 'You cannot access outside of the tuple literals bounds (' + str(size) + \
                      ' is incompatible with ' + str(baseexpr.index) + ')'
                raise TypeCheckerException(ret)
            baseexpr.varxpr.ty = ty
            return ty.tys[baseexpr.index]
        elif type(baseexpr) is ArrayIndexExpr:
            valuetys = self.type_of(baseexpr.expr, table)
            baseexpr.expr.ty = valuetys
            if len(baseexpr.exprs) > valuetys.rank:
                ret = 'You cannot access an array of rank ' + str(valuetys.rank) + ' at rank ' + str(len(baseexpr.exprs))
                raise TypeCheckerException(ret)

            for val in baseexpr.exprs:
                ty = self.type_of(val, table)
                if type(ty) is not IntResolvedType:
                    ret = 'You cannot access an array using a non integer! (' + ty.to_string() + ')'
                    raise TypeCheckerException(ret)
                val.ty = ty

            return valuetys.ty
        elif type(baseexpr) is ArrayLoopExpr:
            arraytable = table.makechild()
            for pair in baseexpr.pairs:
                if type(pair[0]) is Variable:
                    arraytable.addinfo(pair[0].variable, VariableInfo(IntResolvedType()))
                ty = self.type_of(pair[1], arraytable)
                if type(ty) is not IntResolvedType:
                    raise TypeCheckerException('You cannot iterate through arrays with non int increments ' + ty.to_string())
                pair[1].ty = ty
            loopty = self.type_of(baseexpr.expr, arraytable)
            baseexpr.expr.ty = loopty
            return ArrayResolvedType(loopty, len(baseexpr.pairs))
        elif type(baseexpr) is SumLoopExpr:
            sumlooptable = table.makechild()
            for pair in baseexpr.pairs:
                if type(pair[0]) is Variable:
                    sumlooptable.addinfo(pair[0].variable, VariableInfo(IntResolvedType()))

                ty = self.type_of(pair[1], table)
                if type(ty) is not IntResolvedType:
                    raise TypeCheckerException(
                        'You cannot iterate through arrays with non int increments ' + ty.to_string())
                pair[1].ty = ty
            loopty = self.type_of(baseexpr.expr, sumlooptable)
            baseexpr.expr.ty = loopty
            return loopty
        # command checking
        elif type(baseexpr) is ShowCmd:
            showexpr = baseexpr.expr
            ty = self.type_of(showexpr, table)
            showexpr.ty = ty
            return ty
        # TODO iffy on these?
        elif type(baseexpr) is AssertCmd:
            assertexpr = baseexpr.expr
            ty = self.type_of(assertexpr, table)
            if type(ty) is not BoolResolvedType:
                raise TypeCheckerException('Assert must evaluate a boolean expression, not ' + ty.to_string())
            assertexpr.ty = ty
            return ty
        elif type(baseexpr) is TimeCmd:
            return self.type_of(baseexpr.cmd, table)
        elif type(baseexpr) is WriteCmd:
            writeexpr = baseexpr.expr
            ty = self.type_of(writeexpr, table)
            writeexpr.ty = ty
            return ty
        elif type(baseexpr) is LetCmd:
            letexpr = baseexpr.expr
            ty = self.type_of(letexpr, table)
            if type(baseexpr.lvalue) is TupleLValue:
                self.addtuplelval(baseexpr.lvalue, table, ty)
            else:
                self.addlval(baseexpr.lvalue, table, ty)
            letexpr.ty = ty
            return ty
        elif type(baseexpr) is ReadCmd:
            imgty = ArrayResolvedType(TupleResolvedType([FloatResolvedType(), FloatResolvedType(), FloatResolvedType(), FloatResolvedType()]), 2)
            table.addinfo(baseexpr.vararg.variable.variable, VariableInfo(imgty))
            return imgty
