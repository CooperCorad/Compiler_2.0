from symboltable import *


class TypeChecker:
    exprTree: []
    globaltable = SymbolTable()

    def __init__(self, _exprtree):
        self.exprTree = _exprtree
        self.init_globaltable()

    def init_globaltable(self):
        self.globaltable.addinfo('args', VariableInfo(ArrayResolvedType(IntResolvedType(), 1)))
        self.globaltable.addinfo('argnum', VariableInfo(IntResolvedType()))
        fl1_fl1_info = FunctionInfo([FloatResolvedType()], FloatResolvedType(), None)
        fl1_fl1_names = ["sqrt", "exp", "sin", "cos", "tan", "asin", "acos", "atan", "log"]
        for name in fl1_fl1_names:
            self.globaltable.addinfo(name, fl1_fl1_info)
        fl2_fl1_info = FunctionInfo([FloatResolvedType(), FloatResolvedType()], FloatResolvedType(), None)
        fl2_fl1_names = ['pow', 'atan2']
        for name in fl2_fl1_names:
            self.globaltable.addinfo(name, fl2_fl1_info)
        self.globaltable.addinfo('to_float', FunctionInfo([IntResolvedType()], FloatResolvedType(), None))
        self.globaltable.addinfo('to_int', FunctionInfo([FloatResolvedType()], IntResolvedType(), None))

    def type_check(self):
        for cmd in self.exprTree:
            self.type_cmd(cmd, self.globaltable)
        return self.globaltable

    def to_string(self):
        ret = ''
        for expr in self.exprTree:
            ret += expr.to_string() + '\n'
        return ret[:-1]

    def bind_to_lval(self, binding, table):
        if type(binding) is VarBinding:
            return ArgLValue(binding.argument), self.type_of(binding.type, table)
        elif type(binding) is TupleBinding:
            lvals = []
            rtys = []
            for bind in binding.bindings:
                lval, rty = self.bind_to_lval(bind, table)
                lvals.append(lval)
                rtys.append(rty)
            return TupleLValue(lvals), TupleResolvedType(rtys)

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

        # type to resolvedtype
        elif type(baseexpr) is IntType:
            return IntResolvedType()
        elif type(baseexpr) is FloatType:
            return FloatResolvedType()
        elif type(baseexpr) is BoolType:
            return BoolResolvedType()
        elif type(baseexpr) is TupleType:
            tys = []
            for typs in baseexpr.types:
                tys.append(self.type_of(typs, table))
            return TupleResolvedType(tys)
        elif type(baseexpr) is ArrayType:
            ty = self.type_of(baseexpr.type, table)
            return ArrayResolvedType(ty, baseexpr.count)

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
        # TODO even necessary?
        elif type(baseexpr) is VarType:
            if table.hasinfo(baseexpr.variable.variable):
                info = table.getinfo(baseexpr.variable.variable)
                if type(info) is TypeInfo:
                    return info.rt
                else:
                    ret = 'This value is not a type (' + type(info) + ')'
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
                elif type(lty) is BoolResolvedType and baseexpr.op in ['<=', '>=', '>', '<']:
                    ret = 'You cannot mathematically compare booleans!'
                    raise TypeCheckerException(ret)
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
            return ArrayResolvedType(tylist[0], 1)

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

        elif type(baseexpr) is CallExpr:
            name = baseexpr.variable.variable
            if table.hasinfo(name):
                info = table.getinfo(name)
                if type(info) is not FunctionInfo:
                    ret = 'You cannot use ' + info.rt.to_string() + ' as a function'
                    raise TypeCheckerException(ret)
                if len(baseexpr.exprs) != len(info.argtys):
                    ret = 'You must have ' + str(len(info.argtys)) + ' arguments for ' + name + ' call, you have ' + str(len(baseexpr.exprs))
                    raise TypeCheckerException(ret)
                for i in range(len(baseexpr.exprs)):
                    expty = self.type_of(baseexpr.exprs[i], table)
                    if not expty.equals(info.argtys[i]):
                        ret = 'Your \"' + name + '\" function argument types do not match: ' + expty.to_string() + ' is not expected ' + info.argtys[i].to_string()
                        raise TypeCheckerException(ret)
                    baseexpr.exprs[i].ty = expty
                return info.retty
            else:
                ret = 'Uknown function call on ' + baseexpr.to_string()
                raise TypeCheckerException(ret)

    def type_stmt(self, stmt: Stmt, table: SymbolTable):
        if type(stmt) is AssertStmt:
            assertexpr = stmt.expr
            expty = self.type_of(assertexpr, table)
            if type(expty) is not BoolResolvedType:
                ret = 'Assert statements must evaluate to a boolean expression, not ' + expty.to_string()
                raise TypeCheckerException(ret)
            assertexpr.ty = expty
            return expty

        elif type(stmt) is ReturnStmt:
            retty = self.type_of(stmt.expr, table)
            stmt.expr.ty = retty
            return retty

        elif type(stmt) is LetStmt:
            letexpr = stmt.expr
            expty = self.type_of(letexpr, table)
            table.addlval(stmt.lval, expty)
            letexpr.ty = expty
            return expty

    def type_cmd(self, cmd: Cmd, table: SymbolTable):
        if type(cmd) is ShowCmd:
            showexpr = cmd.expr
            expty = self.type_of(showexpr, table)
            showexpr.ty = expty
        elif type(cmd) is AssertCmd:
            assertexpr = cmd.expr
            expty = self.type_of(assertexpr, table)
            if type(expty) is not BoolResolvedType:
                raise TypeCheckerException('Assert must evaluate a boolean expression, not ' + expty.to_string())
            assertexpr.ty = expty
        elif type(cmd) is WriteCmd:
            writeexpr = cmd.expr
            expty = self.type_of(writeexpr, table)
            imgty = ArrayResolvedType(TupleResolvedType([FloatResolvedType(), FloatResolvedType(), FloatResolvedType(), FloatResolvedType()]), 2)
            if not imgty.equals(expty):
                ret = 'You cannot write a non {float, float, float, float}[,] to an image!'
                raise TypeCheckerException(ret)
            writeexpr.ty = expty

        elif type(cmd) is LetCmd:
            letexpr = cmd.expr
            expty = self.type_of(letexpr, table)
            table.addlval(cmd.lvalue, expty)
            letexpr.ty = expty

        elif type(cmd) is ReadCmd:
            imgty = ArrayResolvedType(TupleResolvedType([FloatResolvedType(), FloatResolvedType(), FloatResolvedType(), FloatResolvedType()]), 2)
            if type(cmd.vararg) is VarArg:
                table.addinfo(cmd.vararg.variable.variable, VariableInfo(imgty))
            elif type(cmd.vararg) is ArrayArgument:
                if len(cmd.vararg.arguments) != 2:
                    ret = 'Cannot bind image (type ' + imgty.to_string() + ') to ' + cmd.vararg.to_string() + ') (your array dimensions do not match!)'
                    raise TypeCheckerException(ret)
                for args in cmd.vararg.arguments:
                    table.addinfo(args.variable, VariableInfo(IntResolvedType()))
                table.addinfo(cmd.vararg.var.variable, VariableInfo(imgty))
            else:
                ret = 'Cannot bind image (type ' + imgty.to_string() + ') to ' + cmd.vararg.to_string()
                raise TypeCheckerException(ret)

        elif type(cmd) is TimeCmd:
            self.type_cmd(cmd.cmd, table)

        elif type(cmd) is TypeCmd:
            typety = self.type_of(cmd.typeval, table)
            table.addinfo(cmd.variable.variable, TypeInfo(typety))

        elif type(cmd) is FnCmd:
            fnname = cmd.variable.variable
            fnscope = table.makechild()
            argtys = []
            for bind in cmd.bindings:
                lval, varty = self.bind_to_lval(bind, fnscope)
                argtys.append(varty)
                fnscope.addlval(lval, varty)

            retty = self.type_of(cmd.typ, table)
            fninf = FunctionInfo(argtys, retty, fnscope)
            table.addinfo(fnname, fninf)

            emptyret = False
            retfound = False
            if type(retty) is TupleResolvedType and retty.rank == 0:
                emptyret = True
            for stmt in cmd.stmts:
                stmtty = self.type_stmt(stmt, fnscope)
                if type(stmt) is ReturnStmt:
                    retfound = True
                    if not retty.equals(stmtty):
                        ret = 'Your return types do not match ' + stmtty.to_string() + ' is not previously declared ' + retty.to_string()
                        raise TypeCheckerException(ret)
            if not retfound and not emptyret:
                ret = 'You have declared return type ' + retty.to_string() + ' but do no return'
                raise TypeCheckerException(ret)
