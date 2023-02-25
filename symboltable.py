from typecheckerheader import *


class NameInfo:
    pass


class VariableInfo(NameInfo):
    rt: ResolvedType

    def __init__(self, _rt: ResolvedType):
        self.rt = _rt


class SymbolTable:
    parent = None
    table = dict()

    def create(self):
        child = SymbolTable()
        child.parent = self
        return child

    def hasinfo(self, _name: str):
        if _name in self.table:
            return True
        else:
            if self.parent is None:
                return False
            else:
                return self.parent.has(_name)

    def getinfo(self, _name: str):
        if _name in self.table:
            return self.table[_name]
        else:
            if self.parent is None:
                return None
            else:
                return self.parent.getinfo(_name)

    def addinfo(self, name: str, info: NameInfo):
        if self.hasinfo(name):
            raise TypeCheckerException('You cannot shadow ' + name)
        self.table[name] = info
