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


class Function:
    stack_size : int
    code : [str]
    name : str
    jumps: [str]

    def __init__(self, _asm, _name : str):
        self.asm = _asm
        self.stack_size = 8 # TODO start at 0 or 8, what to cmp with for adjust_stack()??
        self.code = []
        self.name = _name + ':\n_' + _name + ':\n'
        self.jumps = []

    def gen_intexpr(self, expr: IntExpr):
        out = []
        name = self.asm.add_const(expr)
        out.append('mov rax, [rel ' + name + '] ; ' + str(expr.intVal))
        self.push_reg(out, 'rax')
        self.code += out

    def gen_floatexpr(self, expr: FloatExpr):
        out = []
        name = self.asm.add_const(expr)
        out.append('mov rax, [rel ' + name + '] ; ' + str(expr.floatVal))
        self.push_reg(out, 'rax')
        self.code += out

    def gen_trueexpr(self, expr: TrueExpr):
        out = []
        name = self.asm.add_const(expr)
        out.append('mov rax, [rel ' + name + '] ; True')
        self.push_reg(out, 'rax')
        self.code += out

    def gen_falseexpr(self, expr: TrueExpr):
        out = []
        name = self.asm.add_const(expr)
        out.append('mov rax, [rel ' + name + '] ; False')
        self.push_reg(out, 'rax')
        self.code += out

    def gen_unopexpr(self, expr: UnopExpr):
        out = []
        self.gen_expr(expr.expr)
        if type(expr.ty) is not FloatResolvedType:
            out.append('pop rax')
            self.stack_size -= 8
            if expr.op == '-':
                out.append('neg rax')
            elif expr.op == '!':
                out.append('xor rax, 1')
            out.append('push rax')

        elif type(expr.ty) is FloatResolvedType:
            out.append('movsd xmm1, [rsp]')
            out.append('add rsp, 8')
            self.stack_size += 8
            out.append('pxor xmm0, xmm0')
            out.append('subsd xmm0, xmm1')
            out.append('sub rsp, 8')
            self.stack_size -= 8
            out.append('movsd [rsp], xmm0')
            self.stack_size += 8

        self.stack_size += 8
        self.code += out

    def gen_binopexpr(self, expr: BinopExpr):
        out = []
        self.gen_expr(expr.rexpr)
        self.gen_expr(expr.lexpr)

        if type(expr.lexpr.ty) is not FloatResolvedType:
            self.pop_reg(out, 'rax')
            self.pop_reg(out, 'r10')

            op = expr.op
            if op == '+':
                out.append('add rax, r10')
            elif op == '-':
                out.append('sub rax, r10')
            elif op == '*':
                out.append('imul rax, r10')
            elif op in ['/', '%']:
                out.append('cmp r10, 0')
                jumpnum = self.asm.add_jump()
                out.append('jne .jump' + str(jumpnum))

                word = 'divide'
                if op == '%':
                    word = 'mod'
                name = self.asm.add_const_string(word + ' by zero')
                adjusted = self.adjust_stack(out)
                out.append('lea rdi, [rel ' + name + '] ; ' + word + ' by zero')
                out.append('call _fail_assertion')
                if adjusted:
                    self.unadjust_stack(out)

                out.append('.jump' + str(jumpnum) + ':')
                out.append('cqo')
                out.append('idiv r10')
                if op == '%':
                    out.append('mov rax, rdx')

            elif op in ['==', '!=', '>=', '<=', '<', '>']:
                out.append('cmp rax, r10')
                if op == '==':
                    out.append('sete al')
                elif op == '!=':
                    out.append('setne al')
                elif op == '>=':
                    out.append('setge al')
                elif op == '<=':
                    out.append('setle al')
                elif op == '<':
                    out.append('setl al')
                elif op == '>':
                    out.append('setg al')
                out.append('and rax, 1')
            self.push_reg(out, 'rax')

        else:
            out.append('movsd xmm0, [rsp]')
            out.append('add rsp, 8')
            self.stack_size += 8
            out.append('movsd xmm1, [rsp]')
            out.append('add rsp, 8')
            self.stack_size += 8

            op = expr.op
            if op == '+':
                out.append('addsd xmm0, xmm1')
            elif op == '-':
                out.append('subsd xmm0, xmm1')
            elif op == '*':
                out.append('mulsd xmm0, xmm1')
            elif op == '/':
                out.append('divsd xmm0, xmm1')
            elif op == '%':
                # adjusted = self.adjust_stack(out)
                out.append('call _fmod')
                # if adjusted:
                #     self.unadjust_stack(out)
            elif op in ['==', '!=', '>=', '<=', '<', '>']:
                if op == '==':
                    out.append('cmpeqsd xmm0, xmm1')
                elif op == '!=':
                    out.append('cmpneqsd xmm0, xmm1')
                elif op == '<=':
                    out.append('cmplesd xmm0, xmm1')
                elif op == '>=':
                    out.append('cmplesd xmm1, xmm0')
                elif op == '<':
                    out.append('cmpltsd xmm0, xmm1')
                elif op == '>':
                    out.append('cmpltsd xmm1, xmm0')

            if op in ['>=', '>']:
                out.append('movq rax, xmm1')
                out.append('and rax, 1')
                self.push_reg(out, 'rax')
            elif op in ['<=', '<', '==', '!=']:
                out.append('movq rax, xmm0')
                out.append('and rax, 1')
                self.push_reg(out, 'rax')
            else:
                out.append('sub rsp, 8')
                self.stack_size -= 8
                out.append('movsd [rsp], xmm0')

        self.code += out

    def get_resolvedtypesize(self, ty: ResolvedType, size: int):
        if type(ty) is TupleResolvedType:
            for rtys in ty.tys:
                size += self.get_resolvedtypesize(rtys, 0)
            return size
        elif type(ty) is ArrayResolvedType:
            return (ty.rank + 1) * 8
        else:
            return 8

    def gen_tupleindexexpr(self, expr: TupleIndexExpr):
        out = []
        wholesize = self.get_resolvedtypesize(expr.varxpr.ty, 0)
        uptosize = 0
        for i in range(expr.index):
            uptosize += self.get_resolvedtypesize(expr.varxpr.ty.tys[i], 0)
        movesize = self.get_resolvedtypesize(expr.varxpr.ty.tys[expr.index], 0)
        out.append('; Moving ' + str(movesize) + ' bytes from rsp + ' + str(uptosize) + ' to rsp + ' + str(wholesize - movesize))
        for i in reversed(range(int(movesize/8))):
            out.append('\tmov r10, [rsp + ' + str(uptosize) + ' + ' + str(8 * i) + ']')
            out.append('\tmov [rsp + ' + str(wholesize - movesize) + ' + ' + str(8 * i) + '], r10')
        out.append('add rsp, ' + str(wholesize - movesize))
        self.stack_size += (wholesize - movesize)
        self.code += out

    def gen_arrayliteralexpr(self, expr: ArrayLiteralExpr):
        out = []
        movesize = self.get_resolvedtypesize(expr.types[0].ty, 0) * len(expr.types)
        out.append('mov rdi, ' + str(movesize))
        adjusted = self.adjust_stack(out)
        if adjusted:
            self.code += out
            out = []
        out.append('call _jpl_alloc')
        self.stack_size += movesize
        if adjusted:
            self.unadjust_stack(out)
        out.append('; Moving ' + str(movesize) + ' bytes from rsp to rax')
        for i in reversed(range(int(movesize/8))):
            increment = str(i * 8)
            out.append('\tmov r10, [rsp + ' + increment + ']')
            out.append('\tmov [rax + ' + increment + '], r10')
        out.append('add rsp, ' + str(movesize))
        self.push_reg(out, 'rax')
        out.append('mov rax, ' + str(len(expr.types)))
        self.push_reg(out, 'rax')
        self.code += out

    def gen_expr(self, expr : Expr):
        if type(expr) is IntExpr:
            return self.gen_intexpr(expr)
        elif type(expr) is FloatExpr:
            return self.gen_floatexpr(expr)
        elif type(expr) is TrueExpr:
            return self.gen_trueexpr(expr)
        elif type(expr) is FalseExpr:
            return self.gen_falseexpr(expr)
        elif type(expr) is UnopExpr:
            return self.gen_unopexpr(expr)
        elif type(expr) is BinopExpr:
            return self.gen_binopexpr(expr)
        elif type(expr) is TupleLiteralExpr:
            for typ in reversed(expr.types):
                self.gen_expr(typ)
        elif type(expr) is TupleIndexExpr:
            self.gen_expr(expr.varxpr)
            self.gen_tupleindexexpr(expr)
        elif type(expr) is ArrayLiteralExpr:
            for typ in reversed(expr.types):
                self.gen_expr(typ)
            self.gen_arrayliteralexpr(expr)

    def adjust_stack(self, stackinfo: []):
        if self.stack_size % 16 != 0:
            stackinfo.append('sub rsp, 8 ; Align stack')
            self.stack_size -= 8
            return True
        return False

    def unadjust_stack(self, stackinfo: []):
        stackinfo.append('add rsp, 8 ; Remove alignment')
        self.stack_size += 8

    def gen_showcmd(self, cmd: ShowCmd):
        out = []

        stackadjust = self.get_resolvedtypesize(cmd.expr.ty, 0)
        if type(cmd.expr.ty) is ArrayResolvedType:
            stackadjust = (cmd.expr.ty.rank + 1) * 8
        self.stack_size += stackadjust
        adjusted = self.adjust_stack(out)
        self.stack_size -= stackadjust
        if adjusted:
            self.code += out
            out = []
        self.gen_expr(cmd.expr)
        name = self.asm.add_const_type(cmd.expr.ty)
        out.append('lea rdi, [rel ' + name + '] ; ' + cmd.expr.ty.to_string())
        out.append('lea rsi, [rsp]')
        out.append('call _show')
        out.append('add rsp, ' + str(stackadjust))
        self.stack_size += stackadjust
        if adjusted:
            self.unadjust_stack(out)
        self.code += out

    def gen_cmd_code(self):
        for cmd in self.asm.exprTree:
            if type(cmd) is ShowCmd:
                self.gen_showcmd(cmd)

    def gen_main(self):
        self.gen_preample()
        self.gen_global_callee_save()
        self.gen_cmd_code()
        self.gen_global_callee_unsave()
        self.gen_postamble()

    def gen_preample(self):
        out = ['push rbp', 'mov rbp, rsp']
        self.stack_size += 8
        self.code += out

    def gen_postamble(self):
        out = ['pop rbp', 'ret']
        self.stack_size -= 8
        self.code += out

    def gen_global_callee_save(self):
        out = ['push r12', 'mov r12, rbp']
        self.stack_size += 8
        self.code += out

    def gen_global_callee_unsave(self):
        out = []
        self.pop_reg(out, 'r12')
        self.code += out

    def to_string(self):
        string = ''
        string += self.name
        for x in self.code:
            if x.startswith('.jump'):
                string += x + '\n'
            else:
                string += '\t' + x + '\n'
        return string[:-1]

    def pop_reg(self, codeblock: [], reg: str):
        codeblock.append('pop ' + reg)
        self.stack_size -= 8

    def push_reg(self, codeblock: [], reg: str):
        codeblock.append('push ' + reg)
        self.stack_size += 8
