from parserheader import *
from typecheckerheader import *

ref_header = 'global jpl_main\n\
global _jpl_main\n\
extern _fail_assertion\n\
extern _jpl_alloc\n\
extern _get_time\n\
extern _show\n\
extern _print\n\
extern _print_time\n\
extern _read_image\n\
extern _write_image\n\
extern _fmod\n\
extern _sqrt\n\
extern _exp\n\
extern _sin\n\
extern _cos\n\
extern _tan\n\
extern _asin\n\
extern _acos\n\
extern _atan\n\
extern _log\n\
extern _pow\n\
extern _atan2\n\
extern _to_int\n\
extern _to_float\n\
'


class AsmGenException(Exception):
    def __init__(self, _message):
        self.message = _message
        super().__init__(self.message)


class StackDescription:
    stacksize: int
    nameloc: dict
    localvarsize: int

    def __init__(self):
        self.stacksize = 0
        self.nameloc = dict()
        self.localvarsize = 0

    def addlval(self, lval, size):
        self.localvarsize += size
        if type(lval) is Variable:
            name = lval.variable
        # elif type(lval) is ArgLValue:
        #     name = lval.variable.var.variable
        else:
            name = lval.variable.variable.variable
        self.nameloc[name] = (8 + self.localvarsize)

    def get_resolvedtypesize(self, ty: ResolvedType, size: int):
        if type(ty) is TupleResolvedType:
            for rtys in ty.tys:
                size += self.get_resolvedtypesize(rtys, 0)
            return size
        elif type(ty) is ArrayResolvedType:
            return (ty.rank + 1) * 8
        else:
            return 8

    def insertarg(self, arg, ty):
        if type(arg) is VarArg:
            size = self.get_resolvedtypesize(ty, 0)
            self.localvarsize += size
            self.nameloc[arg.variable.variable] = self.localvarsize + 8  # TODO size not 8?
        elif type(arg) is ArrayArgument:
            self.localvarsize += 8  # pointer to mem
            for argu in reversed(arg.arguments):
                self.localvarsize += 8  # 8B int for size
                self.nameloc[argu.variable] = (8 + self.localvarsize)
            self.nameloc[arg.variable.variable] = (8 + self.localvarsize)

    def insertlval(self, lval, ty):
        tyty = type(ty)

        if type(lval) is TupleLValue:
            for i in reversed(range(len(lval.variables))):
                tvar = lval.variables[i]
                tty = ty.tys[i]
                self.insertlval(tvar, tty)
        elif tyty is IntResolvedType or tyty is FloatResolvedType or tyty is BoolResolvedType or tyty is TupleResolvedType:
            size = self.get_resolvedtypesize(ty, 0)
            self.localvarsize += size
            self.nameloc[lval.variable.variable.variable] = (8 + self.localvarsize)
        elif tyty is ArrayResolvedType:
            self.insertarg(lval.variable, ty)







    def addargument(self, name, size):
        self.localvarsize += size
        self.nameloc[name] = (8 + self.localvarsize)


class ValLoc:
    pass


class RegVal(ValLoc):
    reg: str

    def __init__(self, _reg):
        self.reg = _reg

    def equals(self, reg):
        return reg.reg == self.reg


class StackVal(ValLoc):
    pass


class CallingConvention:

    params: []
    returnty: ResolvedType
    stackdesc: StackDescription

    intreg_names: []
    intreg_c: int
    floatreg_c: int

    reglocs: []
    stacklocs: []

    returnloc: ValLoc

    def __init__(self, _params: [], _return: ResolvedType, _sd: StackDescription):
        self.params = _params
        self.stackdesc = _sd
        self.returnty = _return
        self.reglocs = []
        self.regnames = [''] * len(_params)
        self.stacklocs = []
        self.intreg_c = 0
        self.floatreg_c = 0
        self.intreg_names = ['rdi', 'rsi', 'rdx', 'rcx', 'r8', 'r9']

        self.calc_return()
        self.calc_pos()

    def calc_return(self):
        if type(self.returnty) is TupleResolvedType:
            self.returnloc = StackVal()
            # self.reglocs.append(0)
            # self.regnames[0] = self.intreg_names[self.intreg_c]
            self.intreg_c += 1
        elif type(self.returnty) is FloatResolvedType:
            self.returnloc = RegVal('xmm0')
        else:
            self.returnloc = RegVal('rax')

    def calc_pos(self):
        for i in (range(len(self.params))):
            param = self.params[i]
            paramty = type(param)

            if paramty is IntResolvedType or paramty is BoolResolvedType:
                if self.intreg_c < 6:
                    self.reglocs.append(i)
                    self.regnames[i] = self.intreg_names[self.intreg_c]
                else:
                    self.stacklocs.append(i)
                self.intreg_c += 1
            elif paramty is FloatResolvedType:
                if self.floatreg_c < 8:
                    self.reglocs.append(i)
                    self.regnames[i] = 'xmm' + str(self.floatreg_c)
                else:
                    self.stacklocs.append(i)
                self.floatreg_c += 1
            elif paramty is TupleResolvedType:
                self.stacklocs.append(i)






