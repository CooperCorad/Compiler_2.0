from asmgenheader import *
from parserheader import *


class AsmGenerator:
    exprTree: []
    consts: {}
    links: []
    fxns: []
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

    def add_const_name(self, const):
        const = 'dq ' + str(const)
        if const not in self.consts.keys():
            name = 'const' + str(len(self.consts))
            self.consts[const] = name
            return name
        return self.consts[const]

    def add_const_string(self, const):
        if issubclass(type(const), ResolvedType):
            const = const.to_string()
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
            ret += func.to_string() + '\n\n'
        return ret[:-2]


class Function:
    stackdesc: StackDescription
    code : [str]
    name : str
    jumps: [str]

    def __init__(self, _asm, _name : str):
        self.asm = _asm
        self.code = []
        self.name = _name + ':\n_' + _name + ':\n'
        self.jumps = []
        self.stackdesc = StackDescription()

    def gen_intexpr(self, expr: IntExpr, out):
        name = self.asm.add_const(expr)
        out.append('mov rax, [rel ' + name + '] ; ' + str(expr.intVal))
        self.push_reg(out, 'rax')

    def gen_floatexpr(self, expr: FloatExpr, out):
        name = self.asm.add_const(expr)
        out.append('mov rax, [rel ' + name + '] ; ' + str(expr.floatVal))
        self.push_reg(out, 'rax')

    def gen_trueexpr(self, expr: TrueExpr, out):
        name = self.asm.add_const(expr)
        out.append('mov rax, [rel ' + name + '] ; True')
        self.push_reg(out, 'rax')

    def gen_falseexpr(self, expr: TrueExpr, out):
        name = self.asm.add_const(expr)
        out.append('mov rax, [rel ' + name + '] ; False')
        self.push_reg(out, 'rax')

    def gen_unopexpr(self, expr: UnopExpr, out):
        self.gen_expr(expr.expr, out)
        if type(expr.ty) is not FloatResolvedType:
            self.pop_reg(out, 'rax')
            if expr.op == '-':
                out.append('neg rax')
            elif expr.op == '!':
                out.append('xor rax, 1')
            self.push_reg(out, 'rax')

        elif type(expr.ty) is FloatResolvedType:
            out.append('movsd xmm1, [rsp]')
            out.append('add rsp, 8')
            self.stackdesc.stacksize -= 8
            out.append('pxor xmm0, xmm0')
            out.append('subsd xmm0, xmm1')
            out.append('sub rsp, 8')
            self.stackdesc.stacksize += 8
            out.append('movsd [rsp], xmm0')
            # self.stackdesc.stacksize += 8

        # self.stackdesc.stacksize += 8

    def gen_shortcut(self, expr: BinopExpr, out):
        self.gen_expr(expr.lexpr, out)
        self.pop_reg(out, 'rax')
        out.append('cmp rax, 0')

        shortjump = str(self.asm.add_jump())
        if expr.op == '||':
            out.append('jne .jump' + shortjump)
        else:
            out.append('je .jump' + shortjump)
        self.gen_expr(expr.rexpr, out)
        self.pop_reg(out, 'rax')
        out.append('.jump' + shortjump + ':')
        self.push_reg(out, 'rax')

    def gen_binopexpr(self, expr: BinopExpr, out):
        if expr.op in ['&&', '||']:
            self.gen_shortcut(expr, out)
            return

        self.gen_expr(expr.rexpr, out)
        self.gen_expr(expr.lexpr, out)

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
            self.stackdesc.stacksize -= 8
            out.append('movsd xmm1, [rsp]')
            out.append('add rsp, 8')
            self.stackdesc.stacksize -= 8

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
                self.stackdesc.stacksize += 8
                out.append('movsd [rsp], xmm0')

    def get_resolvedtypesize(self, ty: ResolvedType, size: int):
        if type(ty) is TupleResolvedType:
            for rtys in ty.tys:
                size += self.get_resolvedtypesize(rtys, 0)
            return size
        elif type(ty) is ArrayResolvedType:
            return (ty.rank + 1) * 8
        else:
            return 8

    def gen_tupleindexexpr(self, expr: TupleIndexExpr, out):

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

        self.stackdesc.stacksize -= (wholesize - movesize)

    def gen_arrayliteralexpr(self, expr: ArrayLiteralExpr, out):
        movesize = self.get_resolvedtypesize(expr.types[0].ty, 0) * len(expr.types)
        if movesize < -pow(2, 63) or movesize > ((pow(2, 63)) - 1):
            raise AsmGenException('You cannot allocate more memory than MAX_INT (2^63 - 1)')
        out.append('mov rdi, ' + str(movesize))

        # self.stackdesc.stacksize += movesize
        adjusted = self.adjust_stack(out)
        # self.stackdesc.stacksize -= movesize
        out.append('call _jpl_alloc')
        if adjusted:
            self.unadjust_stack(out)

        out.append('; Moving ' + str(movesize) + ' bytes from rsp to rax')
        for i in reversed(range(int(movesize/8))):
            increment = str(i * 8)
            out.append('\tmov r10, [rsp + ' + increment + ']')
            out.append('\tmov [rax + ' + increment + '], r10')
        out.append('add rsp, ' + str(movesize))
        self.stackdesc.stacksize -= movesize
        self.push_reg(out, 'rax')
        out.append('mov rax, ' + str(len(expr.types)))
        self.push_reg(out, 'rax')

    def gen_varexpr(self, expr: VariableExpr, out):
        movesize = self.get_resolvedtypesize(expr.ty, 0)
        out.append('sub rsp, ' + str(movesize))
        self.stackdesc.stacksize += movesize
        varloc = self.stackdesc.nameloc[expr.variable.variable]
        out.append('; Moving ' + str(movesize) + ' bytes from rbp - ' + str(varloc) + ' to rsp')
        for i in range(int(movesize/8)):
            increment = (i + 1) * 8
            out.append('\tmov r10, [rbp - ' + str(varloc) + ' + ' + str(movesize - increment) + ']')
            out.append('\tmov [rsp + ' + str(movesize - increment) + '], r10')

    def gen_callexpr(self, expr: CallExpr, out):

        paramtys = []
        for exp in expr.exprs:
            paramtys.append(exp.ty)
        cc = CallingConvention(paramtys, expr.ty)

        if type(expr.ty) is ArrayResolvedType or (type(expr.ty) is TupleResolvedType and expr.ty.rank > 0):
            returnspace = self.get_resolvedtypesize(expr.ty, 0)
            out.append('sub rsp, ' + str(returnspace))
            self.stackdesc.stacksize += returnspace
            tempstack = self.stackdesc.stacksize
        # if type(expr.ty) is ArrayResolvedType:
        adjusted = self.adjust_stack(out)

        for i in reversed(cc.stacklocs):
            self.gen_expr(expr.exprs[i], out)

        pops = []
        popadjust = 0
        for i in reversed(cc.reglocs):
            currexpr = expr.exprs[i]
            currexprty = type(currexpr.ty)
            self.gen_expr(currexpr, out)

            if currexprty is IntResolvedType or currexprty is BoolResolvedType:
                pops.insert(0, 'pop ' + cc.regnames[i])
                popadjust -= 8
            elif currexprty is FloatResolvedType:
                pops.insert(0, 'add rsp, 8')
                popadjust -= 8
                pops.insert(0, 'movsd ' + cc.regnames[i] + ', [rsp]')

        out += pops
        self.stackdesc.stacksize += popadjust

        if type(expr.ty) is ArrayResolvedType or (type(expr.ty) is TupleResolvedType and expr.ty.rank > 0):
            out.append('lea rdi, [rsp + ' + str((self.stackdesc.stacksize - tempstack)) + ']')

        out.append('call _' + expr.variable.variable)

        for i in cc.stacklocs:
            size = self.get_resolvedtypesize(expr.exprs[i].ty, 0)
            out.append('add rsp, ' + str(size))
            self.stackdesc.stacksize -= size

        if adjusted:
            self.unadjust_stack(out)

        returnty = type(expr.ty)
        if returnty is FloatResolvedType:
            out.append('sub rsp, 8')
            self.stackdesc.stacksize += 8
            out.append('movsd [rsp], xmm0')
        elif returnty is IntResolvedType or returnty is BoolResolvedType:
            self.push_reg(out, 'rax')
        elif returnty is TupleResolvedType:
            pass

    def gen_ifexpr(self, expr: IfExpr, out):
        self.gen_expr(expr.ifexp, out)
        self.pop_reg(out, 'rax')
        out.append('cmp rax, 0')
        elsejmp = self.asm.add_jump()
        out.append('je .jump' + str(elsejmp))
        returnflowjmp = self.asm.add_jump()
        self.gen_expr(expr.thenexp, out)
        out.append('jmp .jump' + str(returnflowjmp))
        out.append('.jump' + str(elsejmp) + ':')
        self.stackdesc.stacksize -= self.get_resolvedtypesize(expr.ty, 0)
        # TODO ^ here so the production of else is not affected by then? ^
        self.gen_expr(expr.elseexp, out)
        out.append('.jump' + str(returnflowjmp) + ':')

    def get_arrindex_loc(self, expr: ArrayIndexExpr):
        if type(expr.expr) is ArrayLiteralExpr:
            return 0
        elif type(expr.expr) is VariableExpr:
            return self.stackdesc.nameloc[expr.expr.variable.variable]
        elif type(expr.expr) is ArrayIndexExpr:
            return self.get_arrindex_loc(expr.expr)

    def gen_arrindexexpr(self, expr: ArrayIndexExpr, out):
        if type(expr.expr) is not VariableExpr:
            self.gen_expr(expr.expr, out)
        arrsize = self.get_resolvedtypesize(expr.expr.ty, 0)


        arrloc = self.get_arrindex_loc(expr)
        if type(expr.expr) is not ArrayIndexExpr and arrloc != 0 and arrloc is not None:
            out.append('sub rsp, ' + str(arrsize))
            self.stackdesc.stacksize += arrsize
            out.append('; Moving ' + str(arrsize) + ' bytes from rbp - ' + str(arrloc) + ' to rsp')
            for i in reversed(range(int(arrsize/8))):
                increment = str(i * 8)
                out.append('\tmov r10, [rbp - ' + str(arrloc) + ' + ' + increment + ']')
                out.append('\tmov [rsp + ' + increment + '], r10')

        for exp in reversed(expr.exprs):
            self.gen_expr(exp, out)

        indexcount = len(expr.exprs)

        for i in range(indexcount):
            offset = (i * 8)
            out.append('mov rax, [rsp + ' + str(offset) + ']')
            out.append('cmp rax, 0')
            negindexjmp = str(self.asm.add_jump())
            out.append('jge .jump' + negindexjmp)

            adjusted = self.adjust_stack(out)
            name = self.asm.add_const_string('negative array index')
            out.append('lea rdi, [rel ' + name + '] ; negative array index')
            out.append('call _fail_assertion')
            if adjusted:
                self.unadjust_stack(out)

            out.append('.jump' + negindexjmp + ':')
            out.append('cmp rax, [rsp + ' + str(offset + 8 * indexcount) + ']')
            # out.append('cmp rax, 0')
            outofboundsjump = str(self.asm.add_jump())
            out.append('jl .jump' + outofboundsjump)
            adjusted = self.adjust_stack(out)
            name = self.asm.add_const_string('index too large')
            out.append('lea rdi, [rel ' + name + '] ; index too large')
            out.append('call _fail_assertion')
            if adjusted:
                self.unadjust_stack(out)

            out.append('.jump' + outofboundsjump + ':')

        out.append('mov rax, 0')

        for i in range(indexcount):
            offset = i * 8
            out.append('imul rax, [rsp + ' + str(offset + (indexcount * 8)) + '] ; No overflow if indices in bounds')
            out.append('add rax, [rsp + ' + str(offset) + ']')

        sizeofitems = self.get_resolvedtypesize(expr.ty, 0)
        out.append('imul rax, ' + str(sizeofitems))   # TODO what is this?
        out.append('add rax, [rsp + ' + str(arrsize - 8 + indexcount * 8) + ']')

        for i in range(indexcount):
            out.append('add rsp, 8')
            self.stackdesc.stacksize -= 8
        out.append('add rsp, ' + str(arrsize))
        self.stackdesc.stacksize -= arrsize
        out.append('sub rsp, ' + str(sizeofitems))    # TODO same as 'what is this?'
        self.stackdesc.stacksize += sizeofitems

        out.append('; Moving ' + str(sizeofitems) + ' bytes from rax to rsp')
        for i in reversed(range(int(sizeofitems/8))):
            offset = str(i * 8)
            out.append('\tmov r10, [rax + ' + offset + ']')
            out.append('\tmov [rsp + ' + offset + '], r10')

    def gen_loopexpr(self, expr, out):
        sumloop = False
        if type(expr) is SumLoopExpr:
            sumloop = True

        out.append('sub rsp, 8')
        self.stackdesc.stacksize += 8

        numbinds = len(expr.pairs)

        # Same for any loop
        for pair in reversed(expr.pairs):
            self.gen_expr(pair[1], out)
            out.append('mov rax, [rsp]')
            out.append('cmp rax, 0')
            positivejump = str(self.asm.add_jump())
            out.append('jg .jump' + positivejump)
            adjusted = self.adjust_stack(out)
            error = 'non-positive loop bound'
            name = self.asm.add_const_string(error)
            out.append('lea rdi, [rel ' + name + '] ; ' + error)
            out.append('call _fail_assertion')
            if adjusted:
                self.unadjust_stack(out)
            out.append('.jump' + positivejump + ':')
        # ~~ end ~~

        if sumloop:
            out.append('mov rax, 0')
            out.append('mov [rsp + ' + str(8 * numbinds) + '], rax')
        else:
            out.append('; Computing total size of heap memory to allocate')
            elmtsize = self.get_resolvedtypesize(expr.expr.ty, 0)
            out.append('mov rdi, ' + str(elmtsize) + ' ; sizeof ' + expr.expr.ty.to_string())

            error = 'overflow computing array size'
            name = self.asm.add_const_string(error)

            for i in range(numbinds):
                increment = str(i * 8)
                out.append('imul rdi, [rsp + 0 + ' + increment + ']')
                nooverflowjmp = str(self.asm.add_jump())
                out.append('jno .jump' + nooverflowjmp)
                adjusted = self.adjust_stack(out)
                out.append('lea rdi, [rel ' + name + '] ; ' + error)
                out.append('call _fail_assertion')
                if adjusted:
                    self.unadjust_stack(out)
                out.append('.jump' + nooverflowjmp + ':')

            adjusted = self.adjust_stack(out)
            out.append('call _jpl_alloc ; Put pointer to heap space in RAX')
            if adjusted:
                self.unadjust_stack(out)

            out.append('mov [rsp + ' + str(8 * numbinds) + '], rax ; Move to pre-allocated space')

        # Same for any loop
        for i in reversed(range(numbinds)):
            out.append('mov rax, 0')
            self.push_reg(out, 'rax')
            name = expr.pairs[i][0].variable
            self.stackdesc.nameloc[name] = self.stackdesc.stacksize
        # ~~ end ~~

        loopbodjump = str(self.asm.add_jump())
        out.append('.jump' + loopbodjump + ': ; Begin body of loop')

        self.gen_expr(expr.expr, out)

        if sumloop:
            if type(expr.ty) is not FloatResolvedType:
                self.pop_reg(out, 'rax')
                out.append('add [rsp + ' + str(16 * numbinds) + '], rax ; Add loop body to sum')
            else:
                sumsize = str(16 * numbinds)
                out.append('movsd xmm0, [rsp]')
                out.append('add rsp, 8')
                self.stackdesc.stacksize -= 8
                out.append('addsd xmm0, [rsp + ' + sumsize + '] ; Load sum')
                out.append('movsd [rsp + ' + sumsize + '], xmm0 ; Save sum')
        else:
            out.append('; Index to store in')
            out.append('mov rax, 0')

            for i in range(numbinds):
                boundoffset = str(((i + numbinds) * 8) + elmtsize)
                increment = str((i * 8) + elmtsize)
                out.append('imul rax, [rsp + ' + boundoffset + '] ; No overflow if indices in bounds')
                out.append('add rax, [rsp + ' + increment + ']')

            out.append('imul rax, ' + str(elmtsize))
            out.append('add rax, [rsp + ' + str((16 * numbinds) + elmtsize) + ']')

            out.append('; Move body (' + str(elmtsize) + ' bytes) to index')
            out.append('; Moving ' + str(elmtsize) + ' bytes from rsp to rax')
            for i in reversed(range(int(elmtsize/8))):
                increment = str(i * 8)
                out.append('\tmov r10, [rsp + ' + increment + ']')
                out.append('\tmov [rax + ' + increment + '], r10')

            out.append('add rsp, ' + str(elmtsize))
            self.stackdesc.stacksize -= elmtsize

        # Here on same for any loop
        out.append('; Increment ' + expr.pairs[numbinds - 1][0].variable)
        out.append('add qword [rsp + ' + str(8 * (numbinds - 1)) + '], 1')

        for i in reversed(range(1, numbinds)):
            varname = expr.pairs[i][0].variable
            varoffset = str(i * 8)
            boundoffset = str((i + numbinds) * 8)
            out.append('; Compare ' + varname + ' to its bound')
            out.append('mov rax, [rsp + ' + varoffset + ']')
            out.append('cmp rax, [rsp + ' + boundoffset + ']')
            out.append('jl .jump' + loopbodjump + ' ; If ' + varname + ' < bound, next iter')
            out.append('mov qword [rsp + ' + varoffset + '], 0 ; ' + varname + ' = 0')
            out.append('add qword [rsp + ' + str((i - 1) * 8) + '], 1 ; ' + expr.pairs[i - 1][0].variable + '++')

        lastvarname = expr.pairs[0][0].variable
        out.append('; Compare ' + lastvarname + ' to its bound')
        out.append('mov rax, [rsp + 0]')
        out.append('cmp rax, [rsp + ' + str(numbinds * 8) + ']')
        out.append('jl .jump' + loopbodjump + ' ; If ' + lastvarname + ' < bound, next iter')
        out.append('; End body of loop')

        out.append('; Free all loop variables')
        out.append('add rsp, ' + str(numbinds * 8))
        self.stackdesc.stacksize -= numbinds * 8
        out.append('; Free all loop bounds')
        if sumloop:
            out.append('add rsp, ' + str(numbinds * 8))
            self.stackdesc.stacksize -= numbinds * 8
            out.append('; sum left on stack')

        # self.stackdesc.localvarsize = localvarelim




    def gen_expr(self, expr : Expr, out):
        if type(expr) is IntExpr:
            return self.gen_intexpr(expr, out)
        elif type(expr) is FloatExpr:
            return self.gen_floatexpr(expr, out)
        elif type(expr) is TrueExpr:
            return self.gen_trueexpr(expr, out)
        elif type(expr) is FalseExpr:
            return self.gen_falseexpr(expr, out)
        elif type(expr) is UnopExpr:
            return self.gen_unopexpr(expr, out)
        elif type(expr) is BinopExpr:
            return self.gen_binopexpr(expr, out)
        elif type(expr) is TupleLiteralExpr:
            for typ in reversed(expr.types):
                self.gen_expr(typ, out)
        elif type(expr) is TupleIndexExpr:
            self.gen_expr(expr.varxpr, out)
            self.gen_tupleindexexpr(expr, out)
        elif type(expr) is ArrayLiteralExpr:
            for typ in reversed(expr.types):
                self.gen_expr(typ, out)
            self.gen_arrayliteralexpr(expr, out)
        elif type(expr) is VariableExpr:
            self.gen_varexpr(expr, out)
        elif type(expr) is CallExpr:
            self.gen_callexpr(expr, out)
        elif type(expr) is IfExpr:
            self.gen_ifexpr(expr, out)
        elif type(expr) is ArrayIndexExpr:
            self.gen_arrindexexpr(expr, out)
        elif type(expr) is SumLoopExpr or type(expr) is ArrayLoopExpr:
            self.gen_loopexpr(expr, out)
        # elif type(expr) is AssertCmd

    def gen_showcmd(self, cmd: ShowCmd, out):

        stackadjust = self.get_resolvedtypesize(cmd.expr.ty, 0)
        # if type(cmd.expr.ty) is ArrayResolvedType or type(cmd.expr.ty) is TupleResolvedType:
        #     stackadjust = 0
        self.stackdesc.stacksize -= stackadjust
        adjusted = self.adjust_stack(out)
        self.stackdesc.stacksize += stackadjust
        self.gen_expr(cmd.expr, out)
        name = self.asm.add_const_string(cmd.expr.ty)
        out.append('lea rdi, [rel ' + name + '] ; ' + cmd.expr.ty.to_string())
        out.append('lea rsi, [rsp]')
        out.append('call _show')
        out.append('add rsp, ' + str(stackadjust))
        self.stackdesc.stacksize -= stackadjust
        if adjusted:
            self.unadjust_stack(out)

    def gen_letcmd(self, cmd: LetCmd, out):
        self.gen_expr(cmd.expr, out)
        self.stackdesc.insertlval(cmd.lvalue, cmd.expr.ty)

    def gen_readcmd(self, cmd: ReadCmd, out):
        out.append('sub rsp, 24')
        self.stackdesc.stacksize += 24
        imgty = ArrayResolvedType(TupleResolvedType([FloatResolvedType(), FloatResolvedType(), FloatResolvedType(), FloatResolvedType()]), 2)
        self.stackdesc.insertarg(cmd.vararg, imgty)

        out.append('lea rdi, [rsp]')
        adjusted = self.adjust_stack(out)

        name = self.asm.add_const_string(cmd.filename[1:-1])
        out.append('lea rsi, [rel ' + name + '] ; ' + cmd.filename[1:-1])
        out.append('call _read_image')
        if adjusted:
            self.unadjust_stack(out)

    def gen_retstmt(self, stmt: ReturnStmt, out):
        self.gen_expr(stmt.expr, out)
        retty = type(stmt.expr.ty)
        if retty is IntResolvedType:
            self.pop_reg(out, 'rax')
        elif retty is FloatResolvedType:
            out.append('movsd xmm0, [rsp]')
            out.append('add rsp, 8')
            self.stackdesc.stacksize -= 8
        elif retty is TupleResolvedType:
            if stmt.expr.ty.rank == 0:
                return
            else:
                out.append('mov rax, [rbp - 8] ; Address to write return value into')
                size = self.get_resolvedtypesize(stmt.expr.ty, 0)
                out.append('; Moving ' + str(size) + ' bytes from rsp to rax')
                for i in reversed(range((int(size / 8)))):
                    increment = i * 8
                    out.append('\tmov r10, [rsp + ' + str(increment) + ']')
                    out.append('\tmov [rax + ' + str(increment) + '], r10')
        elif retty is ArrayResolvedType:
            out.append('mov rax, [rbp - 8] ; Address to write return value into')
            size = self.get_resolvedtypesize(stmt.expr.ty, 0)
            out.append('; Moving 16 bytes from rsp to rax')
            for i in reversed(range((int(size/8)))):
                increment = i * 8
                out.append('\tmov r10, [rsp + ' + str(increment) + ']')
                out.append('\tmov [rax + ' + str(increment)  + '], r10')

    def gen_letstmt(self, stmt: LetStmt, out):
        self.gen_expr(stmt.expr, out)
        self.stackdesc.insertlval(stmt.lval, stmt.expr.ty)

    def gen_stmts(self, stmts, out):
        for stmt in stmts:
            stmtty = type(stmt)
            if stmtty is ReturnStmt:
                self.gen_retstmt(stmt, out)
                return
            elif stmtty is LetStmt:
                self.gen_letstmt(stmt, out)

    def gen_fnpreamble(self, cmd: FnCmd, out):
        retty = type(cmd.typ)
        returnextra = False
        i = 0
        f = 0
        if (retty is TupleType and len(cmd.typ.types) > 0) or retty is ArrayType:
            self.push_reg(out, 'rdi')
            self.stackdesc.localvarsize += 8  # TODO necessary?
            # returnextra = True
            i = 1

        intreg_names = ['rdi', 'rsi', 'rdx', 'rcx', 'r8', 'r9']
        loc = 0
        stackpushsize = -8
        for bnd in cmd.bindings:
            bndty = type(bnd.ty)
            if bndty in [BoolResolvedType, IntResolvedType]:
                self.push_reg(out, intreg_names[i])
                i += 1
                self.stackdesc.insertarg(cmd.bindings[loc].argument, cmd.bindings[loc].ty)

            elif bndty is FloatResolvedType:
                out.append('sub rsp, ' + str(8))
                self.stackdesc.stacksize += 8
                out.append('movsd [rsp], xmm' + str(f))
                f += 1
                self.stackdesc.insertarg(cmd.bindings[loc].argument, cmd.bindings[loc].ty)

            # self.stackdesc.localvarsize += 8
            elif bndty is TupleResolvedType:
                size = self.get_resolvedtypesize(bndty, 0)
                stackpushsize -= size
                self.stackdesc.nameloc[cmd.bindings[loc].argument.variable.variable] = stackpushsize
                # self.stackdesc

            loc += 1

        # #
        # #
        #
        # exprtys = []
        # for binds in cmd.bindings:
        #     exprtys.append(binds.ty)
        #
        # tt = IntResolvedType
        # if retty is TupleType or retty is ArrayType:
        #     tt = TupleResolvedType
        #
        # cc = CallingConvention(exprtys, tt)
        # for i in cc.reglocs:
        #     reg = cc.regnames[i]
        #     size = self.get_resolvedtypesize(cmd.bindings[i].ty, 0)
        #     if reg[0] == 'r':
        #         self.push_reg(out, reg)
        #     else:
        #         out.append('sub rsp, ' + str(size))
        #         self.stackdesc.stacksize += size
        #         out.append('movsd [rsp], ' + reg)
        #     self.stackdesc.localvarsize += 8    # TODO necessary?
        #
        #     self.stackdesc.insertarg(cmd.bindings[i].argument, cmd.bindings[i].ty)

    def gen_fnpostamble(self, out):
        post = 'add rsp, ' + str(self.stackdesc.stacksize)
        self.stackdesc.stacksize -= self.stackdesc.stacksize
        if self.stackdesc.localvarsize > 0:
            post += ' ; Local variables'
        out.append(post)

    def gen_fnspace(self, cmd: FnCmd):
        out = []
        self.gen_preample(out)
        self.gen_fnpreamble(cmd, out)

        self.gen_stmts(cmd.stmts, out)
        self.gen_fnpostamble(out)
        self.gen_postamble(out)
        self.code += out

    def gen_fncmd(self, cmd: FnCmd):
        func = Function(self.asm, cmd.variable.variable)
        func.gen_fnspace(cmd)
        self.asm.fxns.append(func)

    def gen_assertcmd(self, cmd: AssertCmd, out: []):
        self.gen_expr(cmd.expr, out)
        self.pop_reg(out, 'rax')
        out.append('cmp rax, 0')
        nofailjump = str(self.asm.add_jump())
        out.append('jne .jump' + nofailjump)
        adjusted = self.adjust_stack(out)
        name = self.asm.add_const_string(cmd.string[1:-1])
        out.append('lea rdi, [rel ' + name + '] ; ' + cmd.string[1:-1])
        out.append('call _fail_assertion')
        if adjusted:
            self.unadjust_stack(out)
        out.append('.jump' + nofailjump + ':')

    def gen_printcmd(self, cmd: PrintCmd, out: []):
        adjusted = self.adjust_stack(out)
        name = self.asm.add_const_string(cmd.string[1:-1])
        out.append('lea rdi, [rel ' + name + '] ; ' + cmd.string[1:-1])
        out.append('call _print')
        if adjusted:
            self.unadjust_stack(out)

    def gen_writecmd(self, cmd: WriteCmd, out: []):
        self.stackdesc.stacksize -= 24
        adjusted = self.adjust_stack(out)
        self.stackdesc.stacksize += 24
        self.gen_expr(cmd.expr, out)
        name = self.asm.add_const_string(cmd.filename[1:-1])
        out.append('lea rdi, [rel ' + name + '] ; ' + cmd.filename[1:-1])
        out.append('call _write_image')
        out.append('add rsp, 24')
        self.stackdesc.stacksize -= 24
        if adjusted:
            self.unadjust_stack(out)

    def gen_timecall(self, out: []):
        adjusted = self.adjust_stack(out)
        out.append('call _get_time')
        if adjusted:
            self.unadjust_stack(out)
        out.append('sub rsp, 8')
        self.stackdesc.stacksize += 8
        out.append('movsd [rsp], xmm0')

    def gen_timecmd(self, cmd: TimeCmd, out: [], i: int):
        self.stackdesc.localvarsize += 8
        self.gen_timecall(out)
        ctr = cmd
        x = 0
        while type(ctr.cmd) is TimeCmd:
            ctr = ctr.cmd
            x += 8
        if type(ctr.cmd) not in [ShowCmd, TypeCmd, WriteCmd, AssertCmd, PrintCmd, ShowCmd]:
            x += self.get_resolvedtypesize(ctr.cmd.expr.ty, 0)

        if type(cmd.cmd) is TimeCmd:
            self.gen_timecmd(cmd.cmd, out, x)
        else:
            self.gen_cmd_code([cmd.cmd], out)
        self.gen_timecall(out)
        if i == 0:
            i = x + 8

        out.append('movsd xmm0, [rsp]')
        out.append('add rsp, 8')
        self.stackdesc.stacksize -= 8
        out.append('movsd xmm1, [rsp + ' + str(i - 8) + ']')
        out.append('subsd xmm0, xmm1')
        adjusted = self.adjust_stack(out)
        out.append('call _print_time')
        if adjusted:
            self.unadjust_stack(out)
        # out.append('\n\n')

    def gen_cmd_code(self, tree, out):
        for cmd in tree:
            if type(cmd) is ShowCmd:
                self.gen_showcmd(cmd, out)
            elif type(cmd) is LetCmd:
                self.gen_letcmd(cmd, out)
            elif type(cmd) is ReadCmd:
                self.gen_readcmd(cmd, out)
            elif type(cmd) is FnCmd:
                self.gen_fncmd(cmd)
            elif type(cmd) is AssertCmd:
                self.gen_assertcmd(cmd, out)
            elif type(cmd) is PrintCmd:
                self.gen_printcmd(cmd, out)
            elif type(cmd) is WriteCmd:
                self.gen_writecmd(cmd, out)
            elif type(cmd) is TimeCmd:
                self.gen_timecmd(cmd, out, 0)

    def gen_main(self):
        out = []
        self.gen_preample(out)
        self.gen_global_callee_save(out)
        self.gen_cmd_code(self.asm.exprTree, out)
        self.gen_global_callee_unsave(out)
        self.gen_postamble(out)
        self.code += out

    def gen_preample(self, out):
        out += ['push rbp', 'mov rbp, rsp']
        self.stackdesc.stacksize = 0

    def gen_postamble(self, out):
        out += ['pop rbp', 'ret']
        self.stackdesc.stacksize -= 8

    def gen_global_callee_save(self, out):
        out += ['push r12', 'mov r12, rbp']
        self.stackdesc.stacksize += 8
        self.stackdesc.localvarsize += 8

    def gen_global_callee_unsave(self, out):
        self.stackdesc.localvarsize -= 8
        if self.stackdesc.localvarsize > 0:
            out.append('add rsp, ' + str(self.stackdesc.localvarsize) + ' ; Local variables')
            self.stackdesc.stacksize -= self.stackdesc.localvarsize
        self.pop_reg(out, 'r12')

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
        self.stackdesc.stacksize -= 8

    def push_reg(self, codeblock: [], reg: str):
        codeblock.append('push ' + reg)
        self.stackdesc.stacksize += 8

    def adjust_stack(self, stackinfo: []):
        if self.stackdesc.stacksize % 16 != 0:
            stackinfo.append('sub rsp, 8 ; Align stack')
            self.stackdesc.stacksize += 8
            return True
        return False

    def unadjust_stack(self, stackinfo: []):
        stackinfo.append('add rsp, 8 ; Remove alignment')
        self.stackdesc.stacksize -= 8


