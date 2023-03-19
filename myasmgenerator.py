from asmgenheader import *
from parserheader import *

class AsmGenerator:
    exprTree: []
    consts: {}
    links: []
    fxns: [Function]
    jmp_counter: int

    def __init__(self, _exptree: []):
        self.exprTree = _exptree
        self.jmp_counter = 0
        self.links = []
        self.links.append(ref_header)
        self.fxns = []
        self.consts = {}

    def generate_code(self):

        mainfunc = Function(self, 'jpl_main')
        mainfunc.gen_main()
        self.fxns.append(mainfunc)

    def add_const(self, expr: Expr):
        exptyp = type(expr)
        if exptyp is FloatExpr:
            const = expr.floatVal
            name = self.add_const_name(const)
        elif exptyp is IntExpr:
            const = expr.intVal
            name = self.add_const_name(const)
        elif exptyp is TrueExpr:
            const = 1
            name = self.add_const_name(const)
        elif exptyp is FalseExpr:
            const = 0
            name = self.add_const_name(const)
        return name

    def add_const_type(self, ty: ResolvedType):
        const = 'db `' + ty.to_string() + '`, 0'
        if const not in self.consts.keys():
            name = 'const' + str(len(self.consts))
            self.consts[const] = name
        return self.consts[const]

    def add_const_name(self, const):
        const = 'dq ' + str(const)
        if const not in self.consts.keys():
            name = 'const' + str(len(self.consts))
            self.consts[const] = name
            return name
        return self.consts[const]

    def add_const_string(self, const):
        const = 'db `' + const + '`, 0'
        if const not in self.consts.keys():
            name = 'const' + str(len(self.consts))
            self.consts[const] = name
        return self.consts[const]

    def add_jump(self):
        self.jmp_counter += 1
        return self.jmp_counter

    def to_string(self):
        ret = ''
        for link in self.links:
            ret += link + '\n'

        ret += 'section .data\n'
        for const in self.consts:
            ret += self.consts[const] + ': ' + const + '\n'

        ret += '\nsection .text\n'
        for func in self.fxns:
            ret += func.to_string()
        return ret



