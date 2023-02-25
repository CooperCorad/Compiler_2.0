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

    def addlval(self, lval: ArgLValue, info: NameInfo):
        if isinstance(lval.variable, VarArg):
            name = lval.variable.variable.variable
            self.addinfo(name, info)

