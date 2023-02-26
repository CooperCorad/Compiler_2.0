from typecheckerheader import *
from parserheader import *


class NameInfo:
    pass


class VariableInfo(NameInfo):
    rt: ResolvedType

    def __init__(self, _rt: ResolvedType):
        self.rt = _rt


class SymbolTable:

    def __init__(self):
        self.parent = None
        self.table = dict()

    def makechild(self):
        child = SymbolTable()
        child.parent = self
        return child

    def hasinfo(self, name: str):
        if name in self.table:
            return True
        else:
            if self.parent is None:
                return False
            else:
                return self.parent.hasinfo(name)

    def getinfo(self, name: str):
        if name in self.table:
            return self.table[name]
        else:
            if self.parent is None:
                return None
            else:
                return self.parent.getinfo(name)

    def addinfo(self, name: str, info: NameInfo):
        if self.hasinfo(name):
            raise TypeCheckerException('You cannot shadow ' + name)
        self.table[name] = info

    def addarg(self, arg, typ):
        if type(arg.variable) is VarArg:
            name = arg.variable.variable.variable
            self.addinfo(name, VariableInfo(typ))
        elif type(arg.variable) is ArrayArgument:
            if typ.rank != len(arg.variable.arguments):
                ret = 'You cannot bind a rank ' + str(typ.rank) + ' array to a rank ' + str(len(arg.variable.arguments)) + ' array'
                raise TypeCheckerException(ret)
            name = arg.variable.var.variable
            self.addinfo(name, VariableInfo(typ))
            for args in arg.variable.arguments:
                argname = args.variable
                self.addinfo(argname, VariableInfo(IntResolvedType()))

    def addlval(self, lval, typ):
        if type(lval) is TupleLValue:
            if len(lval.variables) != typ.rank:
                ret = 'You cannot bind rank ' + str(typ.rank) + ' tuple to rank ' + str(len(lval.variables)) + ' tuple'
                raise TypeCheckerException(ret)
            for i in range(len(lval.variables)):
                self.addlval(lval.variables[i], typ.tys[i])
        else:
            self.addarg(lval, typ)






