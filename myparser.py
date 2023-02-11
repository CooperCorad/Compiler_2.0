from parserheader import *


class Parser:
    tokens = []
    program = []

    def __init__(self, _tokens):
        self.tokens = _tokens

    def peek_tok(self, index):
        return self.tokens[index].t

    def expect_tok(self, index, toktype):
        if self.tokens[index].t != toktype:
            ret = 'No token of type ' + toktype + ' found at ' + str(index)
            raise ParserException(ret)
        ret = self.tokens[index].text
        index += 1
        return ret, index

    def to_string(self):
        ret = ''
        for cmd in self.program:
            ret += cmd.to_string() + '\n'

        return ret[:-1]

    def parse(self):
        index = 0

        while True:
            if self.peek_tok(index) == 'END_OF_FILE':
                return self.program
            else:
                cmd, index = self.parse_cmd(index)
                # if self.peek_tok(index) != 'END_OF_FILE':
                #     self.expect_tok(index, 'NEWLINE')
                #     index += 1
                _, index = self.expect_tok(index, 'NEWLINE')
                self.program.append(cmd)

    def parse_cmd(self, index):
        command = self.peek_tok(index)

        if command == 'READ':
            return self.parse_readcmd(index)
        elif command == 'WRITE':
            return self.parse_writecmd(index)
        elif command == 'TYPE':
            return self.parse_typecmd(index)
        elif command == 'LET':
            return self.parse_letcmd(index)
        elif command == 'ASSERT':
            return self.parse_assertcmd(index)
        elif command == 'PRINT':
            return self.parse_printcmd(index)
        elif command == 'SHOW':
            return self.parse_showcmd(index)
        elif command == 'TIME':
            return self.parse_timecmd(index)
        elif command == 'FN':
            return self.parse_fncmd(index)
        else:
            ret = 'Command not found at : ' + str(index)
            raise ParserException(ret)

    # read image <string> to <argument>
    def parse_readcmd(self, index):
        _, index = self.expect_tok(index, 'READ')
        _, index = self.expect_tok(index, 'IMAGE')
        filename, index = self.expect_tok(index, 'STRING')
        _, index = self.expect_tok(index, 'TO')
        argument, index = self.parse_argument(index)
        ret = ReadCmd(filename, argument)
        return ret, index

    # write image <expr> to <string>
    def parse_writecmd(self, index):
        _, index = self.expect_tok(index, 'WRITE')
        _, index = self.expect_tok(index, 'IMAGE')
        expr, index = self.parse_expr_lvl0(index)
        _, index = self.expect_tok(index, 'TO')
        filename, index = self.expect_tok(index, 'STRING')
        ret = WriteCmd(expr, filename)
        return ret, index

    # type <variable> = <type>
    def parse_typecmd(self, index):
        _, index = self.expect_tok(index, 'TYPE')
        var, index = self.parse_variable(index)
        _, index = self.expect_tok(index, 'EQUALS')
        typ, index = self.parse_type(index)
        ret = TypeCmd(var, typ)
        return ret, index

    # let <lvalue> = <expr>
    def parse_letcmd(self, index):
        _, index = self.expect_tok(index, 'LET')
        lval, index = self.parse_lvalue(index)
        _, index = self.expect_tok(index, 'EQUALS')
        expr, index = self.parse_expr_lvl0(index)
        ret = LetCmd(lval, expr)
        return ret, index

    # assert <expr> , <string>
    def parse_assertcmd(self, index):
        _, index = self.expect_tok(index, 'ASSERT')
        expr, index = self.parse_expr_lvl0(index)
        _, index = self.expect_tok(index, 'COMMA')
        string, index = self.expect_tok(index, 'STRING')
        ret = AssertCmd(expr, string)
        return ret, index

    # print <string>
    def parse_printcmd(self, index):
        _, index = self.expect_tok(index, 'PRINT')
        string, index = self.expect_tok(index, 'STRING')
        ret = PrintCmd(string)
        return ret, index

    # show <expr>
    def parse_showcmd(self, index):
        _, index = self.expect_tok(index, 'SHOW')
        expr, index = self.parse_expr_lvl0(index)
        ret = ShowCmd(expr)
        return ret, index

    def parse_timecmd(self, index):
        _, index = self.expect_tok(index, 'TIME')
        cmd, index = self.parse_cmd(index)
        return TimeCmd(cmd), index

    def parse_tuplebinding(self, index, bnds):
        bnd, index = self.parse_binding(index)
        bnds.append(bnd)

        if self.peek_tok(index) == 'COMMA':
            _, index = self.expect_tok(index, 'COMMA')
            return self.parse_tuplebinding(index, bnds)
        if self.peek_tok(index) == 'RCURLY':
            _, index = self.expect_tok(index, 'RCURLY')
            return bnds, index

    def parse_binding(self, index):
        if self.peek_tok(index) == 'LCURLY':
            _, index = self.expect_tok(index, 'LCURLY')
            if self.peek_tok(index) == 'RCURLY':
                _, index = self.expect_tok(index, 'RCURLY')
                return TupleBinding([]), index
            else:
                bnds, index = self.parse_tuplebinding(index, [])
                return TupleBinding(bnds), index
        else:
            arg, index = self.parse_argument(index)
            _, index = self.expect_tok(index, 'COLON')
            typ, index = self.parse_type(index)
            return VarBinding(arg, typ), index

    def parse_binding_seq(self, index, bnds):
        bnd, index = self.parse_binding(index)
        bnds.append(bnd)

        if self.peek_tok(index) == 'COMMA':
            _, index = self.expect_tok(index, 'COMMA')
            return self.parse_binding_seq(index, bnds)
        if self.peek_tok(index) == 'RPAREN':
            _, index = self.expect_tok(index, 'RPAREN')
            return bnds, index

    def parse_fnbindings(self, index):
        _, index = self.expect_tok(index, 'LPAREN')

        if self.peek_tok(index) == 'RPAREN':
            _, index = self.expect_tok(index, 'RPAREN')
            return [], index

        bnds, index = self.parse_binding_seq(index, [])
        return bnds, index

    def parse_letstmt(self, index):
        _, index = self.expect_tok(index, 'LET')
        lval, index = self.parse_lvalue(index)
        _, index = self.expect_tok(index, 'EQUALS')
        expr, index = self.parse_expr_lvl0(index)
        return LetStmt(lval, expr), index

    def parse_assertstmt(self, index):
        _, index = self.expect_tok(index, 'ASSERT')
        expr, index = self.parse_expr_lvl0(index)
        _, index = self.expect_tok(index, 'COMMA')
        string, index = self.expect_tok(index, 'STRING')
        return AssertStmt(expr, string), index

    def parse_returnstmt(self, index):
        _, index = self.expect_tok(index, 'RETURN')
        expr, index = self.parse_expr_lvl0(index)
        return ReturnStmt(expr), index

    def parse_stmt(self, index):
        t = self.peek_tok(index)

        if t == 'LET':
            return self.parse_letstmt(index)
        if t == 'ASSERT':
            return self.parse_assertstmt(index)
        if t == 'RETURN':
            return self.parse_returnstmt(index)
        else:
            raise ParserException('Could not find stmt at index ' + str(index))

    def parse_stmt_seq(self, index, stmts):
        stmt, index = self.parse_stmt(index)
        stmts.append(stmt)

        if self.peek_tok(index) == 'NEWLINE':
            _, index = self.expect_tok(index, 'NEWLINE')
            if self.peek_tok(index) == 'RCURLY':
                _, index = self.expect_tok(index, 'RCURLY')
                return stmts, index
            return self.parse_stmt_seq(index, stmts)

    def parse_stmt_list(self, index):
        while self.peek_tok(index) == 'NEWLINE':
            _, index = self.expect_tok(index, 'NEWLINE')
        if self.peek_tok(index) == 'RCURLY':
            _, index = self.expect_tok(index, 'RCURLY')
            return [], index
        return self.parse_stmt_seq(index, [])

    def parse_fncmd(self, index):
        _, index = self.expect_tok(index, 'FN')
        var, index = self.parse_variable(index)
        bnds, index = self.parse_fnbindings(index)
        _, index = self.expect_tok(index, 'COLON')
        typ, index = self.parse_type(index)
        _, index = self.expect_tok(index, 'LCURLY')
        _, index = self.expect_tok(index, 'NEWLINE')
        stmts, index = self.parse_stmt_list(index)

        return FnCmd(var, bnds, typ, stmts), index

    def parse_arrayargument_seq(self, index, vals):
        var, index = self.parse_variable(index)
        vals.append(var)

        if self.peek_tok(index) == 'COMMA':
            _, index = self.expect_tok(index, 'COMMA')
            return self.parse_arrayargument_seq(index, vals)
        if self.peek_tok(index) == 'RSQUARE':
            _, index = self.expect_tok(index, 'RSQUARE')
            return vals, index

    def parse_arrayargument(self, index, var):
        _, index = self.expect_tok(index, 'LSQUARE')
        if self.peek_tok(index) == 'RSQUARE':
            _, index = self.expect_tok(index, 'RSQUARE')
            return ArrayArgument(var, []), index
        else:
            vrs, index = self.parse_arrayargument_seq(index, [])
            return ArrayArgument(var, vrs), index

    def parse_argument(self, index):
        var, index = self.parse_variable(index)
        if self.peek_tok(index) == 'LSQUARE':
            return self.parse_arrayargument(index, var)
        vaarg = VarArg(var)
        return vaarg, index

    def parse_callexpr_seq(self, index, vals):
        val, index = self.parse_expr_lvl0(index)
        vals.append(val)

        if self.peek_tok(index) == 'COMMA':
            _, index = self.expect_tok(index, 'COMMA')
            return self.parse_callexpr_seq(index, vals)
        if self.peek_tok(index) == 'RPAREN':
            _, index = self.expect_tok(index, 'RPAREN')
            return vals, index

    def parse_callexpr(self, index, var):
        _, index = self.expect_tok(index, 'LPAREN')
        if self.peek_tok(index) == 'RPAREN':
            _, index = self.expect_tok(index, 'RPAREN')
            return CallExpr(var, []), index
        else:
            exprs, index = self.parse_callexpr_seq(index, [])
            return CallExpr(var, exprs), index

    def parse_arrayindexexpr_seq(self, index, exprs : []):
        val, index = self.parse_expr_lvl0(index)
        exprs.append(val)

        if self.peek_tok(index) == 'COMMA':
            _, index = self.expect_tok(index, 'COMMA')
            return self.parse_arrayindexexpr_seq(index, exprs)
        if self.peek_tok(index) == 'RSQUARE':
            _, index = self.expect_tok(index, 'RSQUARE')
            return exprs, index

    def parse_arrayindexexpr(self, index, expr):
        _, index = self.expect_tok(index, 'LSQUARE')
        if self.peek_tok(index) == 'RSQUARE':
            _, index = self.expect_tok(index, 'RSQUARE')
            return ArrayIndexExpr(expr, []), index
        else:
            exprs, index = self.parse_arrayindexexpr_seq(index, [])
            return ArrayIndexExpr(expr, exprs), index

    def parse_tupleindexexpr(self, index, expr):
        _, index = self.expect_tok(index, 'LCURLY')
        num, index = self.expect_tok(index, 'INTVAL')
        _, index = self.expect_tok(index, 'RCURLY')
        return TupleIndexExpr(int(num), expr), index

    def parse_tupleliteralexpr_seq(self, index, vals):
        val, index = self.parse_expr_lvl0(index)
        vals.append(val)

        if self.peek_tok(index) == 'COMMA':
            _, index = self.expect_tok(index, 'COMMA')
            return self.parse_tupleliteralexpr_seq(index, vals)
        if self.peek_tok(index) == 'RCURLY':
            _, index = self.expect_tok(index, 'RCURLY')
            return vals, index

    def parse_arrayliteralexpr_seq(self, index, vals):
        val, index = self.parse_expr_lvl0(index)
        vals.append(val)

        if self.peek_tok(index) == 'COMMA':
            _, index = self.expect_tok(index, 'COMMA')
            return self.parse_arrayliteralexpr_seq(index, vals)
        if self.peek_tok(index) == 'RSQUARE':
            _, index = self.expect_tok(index, 'RSQUARE')
            return vals, index

    def parse_expr_lvl6_cont(self, index, expr):
        t = self.peek_tok(index)
        if t == 'LCURLY':
            expr, index = self.parse_tupleindexexpr(index, expr)
            return self.parse_expr_lvl6_cont(index, expr)
        if t == 'LSQUARE':
            expr, index = self.parse_arrayindexexpr(index, expr)
            return self.parse_expr_lvl6_cont(index, expr)
        return expr, index

    def parse_expr_lvl6(self, index):
        expr, index = self.parse_expr_literal(index)
        return self.parse_expr_lvl6_cont(index, expr)

    def parse_expr_lvl5_cont(self, index, expr):
        if self.peek_tok(index) == 'OP' and type(expr) != UnopExpr:
            op, mbindex = self.expect_tok(index, 'OP')
            if op in precedence[5]:
                index = mbindex
                expr, index = self.parse_expr_lvl6(index)
                finalexpr = UnopExpr(op, expr)
                return self.parse_expr_lvl5_cont(index, finalexpr)
        return expr, index

    def parse_expr_lvl5(self, index):
        if self.peek_tok(index) == 'OP':
            op, mbindex = self.expect_tok(index, 'OP')
            if op in precedence[5]:
                index = mbindex
                expr, index = self.parse_expr_lvl5(index)
                finalexpr = UnopExpr(op, expr)
                return self.parse_expr_lvl5_cont(index, finalexpr)
        return self.parse_expr_lvl6(index)

    def parse_expr_lvl4_cont(self, index, expr):
        if self.peek_tok(index) == 'OP':
            op, mbindex = self.expect_tok(index, 'OP')
            if op in precedence[4]:
                index = mbindex
                expr2, index = self.parse_expr_lvl5(index)
                finalexpr = BinopExpr(op, expr, expr2)
                return self.parse_expr_lvl4_cont(index, finalexpr)
        return expr, index

    # <expr> [*,/,%] <expr>
    def parse_expr_lvl4(self, index):
        expr, index = self.parse_expr_lvl5(index)
        return self.parse_expr_lvl4_cont(index, expr)

    def parse_expr_lvl3_cont(self, index, expr):
        if self.peek_tok(index) == 'OP':
            op, mbindex = self.expect_tok(index, 'OP')
            if op in precedence[3]:
                index = mbindex
                expr2, index = self.parse_expr_lvl4(index)
                finalexpr = BinopExpr(op, expr, expr2)
                return self.parse_expr_lvl3_cont(index, finalexpr)
        return expr, index

    # <expr> [+,-] <expr> todo finish
    def parse_expr_lvl3(self, index):
        nexpr, index = self.parse_expr_lvl4(index)
        return self.parse_expr_lvl3_cont(index, nexpr)

    def parse_expr_lvl2_cont(self, index, expr):
        if self.peek_tok(index) == 'OP':
            op, mbindex = self.expect_tok(index, 'OP')
            if op in precedence[2]:
                index = mbindex
                expr2, index = self.parse_expr_lvl3(index)
                finalexpr = BinopExpr(op, expr, expr2)
                return self.parse_expr_lvl2_cont(index, finalexpr)
        return expr, index

    def parse_expr_lvl2(self, index):
        expr, index = self.parse_expr_lvl3(index)
        return self.parse_expr_lvl2_cont(index, expr)

    def parse_expr_lvl1_cont(self, index, expr):
        if self.peek_tok(index) == 'OP':
            op, mbindex = self.expect_tok(index, 'OP')
            if op in precedence[1]:
                index = mbindex
                expr2, index = self.parse_expr_lvl2(index)
                finalexpr = BinopExpr(op, expr, expr2)
                return self.parse_expr_lvl1_cont(index, finalexpr)
        return expr, index

    def parse_expr_lvl1(self, index):
        expr, index = self.parse_expr_lvl2(index)
        return self.parse_expr_lvl1_cont(index, expr)

    def parse_loop_binds_seq(self, index, vals : []):
        var, index = self.parse_variable(index)
        _, index = self.expect_tok(index, 'COLON')
        expr, index = self.parse_expr_lvl0(index)
        vals.append((var, expr))

        if self.peek_tok(index) == 'RSQUARE':
            _, index = self.expect_tok(index, 'RSQUARE')
            return vals, index
        else:
            _, index = self.expect_tok(index, 'COMMA')
            return self.parse_loop_binds_seq(index, vals)

    def parse_loop_binds(self, index):
        _, index = self.expect_tok(index, 'LSQUARE')
        if self.peek_tok(index) == 'RSQUARE':
            _, index = self.expect_tok(index, 'RSQUARE')
            return [], index
        else:
            return self.parse_loop_binds_seq(index, [])

    def parse_expr_lvl0(self, index):
        return self.parse_expr_lvl1(index)

    def parse_expr_literal(self, index):
        t = self.peek_tok(index)
        if t == 'INTVAL':
            num, index = self.expect_tok(index, 'INTVAL')
            return IntExpr(num), index
        elif t == 'FLOATVAL':
            num, index = self.expect_tok(index, 'FLOATVAL')
            return FloatExpr(num), index
        elif t == 'VARIABLE':
            var, index = self.parse_variable(index)
            if self.peek_tok(index) == 'LPAREN':
                return self.parse_callexpr(index, var)
            return VariableExpr(var), index
        elif t == 'TRUE':
            _, index = self.expect_tok(index, 'TRUE')
            return TrueExpr(), index
        elif t == 'FALSE':
            _, index = self.expect_tok(index, 'FALSE')
            return FalseExpr(), index
        # { <expr> , ... } --> Tuple Literal
        elif t == 'LCURLY':
            _, index = self.expect_tok(index, 'LCURLY')
            if self.peek_tok(index) == 'RCURLY':
                _, index = self.expect_tok(index, 'RCURLY')
                return TupleLiteralExpr([]), index
            else:
                exprs, index = self.parse_tupleliteralexpr_seq(index, [])
                return TupleLiteralExpr(exprs), index
        # [ <expr> , ... ] --> Array Literal
        elif t == 'LSQUARE':
            _, index = self.expect_tok(index, 'LSQUARE')
            if self.peek_tok(index) == 'RSQUARE':
                _, index = self.expect_tok(index, 'RSQUARE')
                return ArrayLiteralExpr([]), index
            else:
                exprs, index = self.parse_arrayliteralexpr_seq(index, [])
                return ArrayLiteralExpr(exprs), index
        # ( <expr> ) --> Parenthasized expr
        elif t == 'LPAREN':
            _, index = self.expect_tok(index, 'LPAREN')
            expr, index = self.parse_expr_lvl0(index)   # TODO move this to
            _, index = self.expect_tok(index, 'RPAREN')
            return expr, index
        # TODO unsure of this!
        elif t == 'ARRAY':
            _, index = self.expect_tok(index, 'ARRAY')
            binds, index = self.parse_loop_binds(index)
            expr, index = self.parse_expr_lvl0(index)
            finalexpr = ArrayLoopExpr(binds, expr)
            return finalexpr, index

        elif t == 'SUM':
            _, index = self.expect_tok(index, 'SUM')
            binds, index = self.parse_loop_binds(index)
            expr, index = self.parse_expr_lvl0(index)
            finalexpr = SumLoopExpr(binds, expr)
            return finalexpr, index
        elif t == 'IF':
            _, index = self.expect_tok(index, 'IF')
            ifexp, index = self.parse_expr_lvl0(index)
            _, index = self.expect_tok(index, 'THEN')
            thenexp, index = self.parse_expr_lvl0(index)
            _, index = self.expect_tok(index, 'ELSE')
            elsexp, index = self.parse_expr_lvl0(index)
            finalexpr = IfExpr(ifexp, thenexp, elsexp)
            return finalexpr, index
        else:
            ret = 'Cannot find literal expression at ' + str(index)
            raise ParserException(ret)

    def parse_inttype(self, index):
        _, index = self.expect_tok(index, 'INT')
        return self.parse_type_cont(index, IntType())

    def parse_floattype(self, index):
        _, index = self.expect_tok(index, 'FLOAT')
        return self.parse_type_cont(index, FloatType())

    def parse_booltype(self, index):
        _, index = self.expect_tok(index, 'BOOL')
        return self.parse_type_cont(index, BoolType())

    def parse_variabletype(self, index):
        var, index = self.parse_variable(index)
        return self.parse_type_cont(index, VarType(var))

    def parse_array_type_seq(self, index, count):
        _, index = self.expect_tok(index, 'COMMA')
        count += 1

        if self.peek_tok(index) == 'RSQUARE':
            _, index = self.expect_tok(index, 'RSQUARE')
            return count, index
        else:
            return self.parse_array_type_seq(index, count)

    def parse_array_type(self, index, in_type):
        _, index = self.expect_tok(index, 'LSQUARE')
        if self.peek_tok(index) == 'RSQUARE':
            _, index = self.expect_tok(index, 'RSQUARE')
            return ArrayType(in_type, 1), index
        else:
            count, index = self.parse_array_type_seq(index, 1)
            return ArrayType(in_type, count), index

    def parse_tuple_type_seq(self, index, typs : []):
        typ, index = self.parse_type(index)
        typs.append(typ)

        if self.peek_tok(index) == 'COMMA':
            _, index = self.expect_tok(index, 'COMMA')
            return self.parse_tuple_type_seq(index, typs)
        if self.peek_tok(index) == 'RCURLY':
            _, index = self.expect_tok(index, 'RCURLY')
            return typs, index

    def parse_tuple_type(self, index):
        _, index = self.expect_tok(index, 'LCURLY')
        if self.peek_tok(index) == 'RCURLY':
            _, index = self.expect_tok(index, 'RCURLY')
            return self.parse_type_cont(index, TupleType([]))
        else:
            res, index = self.parse_tuple_type_seq(index, [])
            return self.parse_type_cont(index, TupleType(res))

    def parse_type_cont(self, index, in_type):
        t = self.peek_tok(index)
        # <type> [ , ... ] --> Array type
        if t == 'LSQUARE':
            res, index = self.parse_array_type(index, in_type)
            return self.parse_type_cont(index, res)
        return in_type, index

    def parse_type(self, index):
        tp = self.peek_tok(index)
        if tp == 'INT':
            return self.parse_inttype(index)
        elif tp == 'FLOAT':
            return self.parse_floattype(index)
        elif tp == 'BOOL':
            return self.parse_booltype(index)
        elif tp == 'VARIABLE':
            return self.parse_variabletype(index)
        # { <type> , ... }  --> Tuple type
        elif tp == 'LCURLY':
            return self.parse_tuple_type(index)
        else:
            ret = 'Could not find a type at ' + str(index) + ' got ' + tp
            raise ParserException(ret)

    def parse_lvalue_tuple_seq(self, index, vals):
        val, index = self.parse_lvalue(index)
        vals.append(val)

        if self.peek_tok(index) == 'COMMA':
            _, index = self.expect_tok(index, 'COMMA')
            return self.parse_lvalue_tuple_seq(index, vals)
        if self.peek_tok(index) == 'RCURLY':
            _, index = self.expect_tok(index, 'RCURLY')
            return vals, index

    def parse_lvaluetuple(self, index):
        _, index = self.expect_tok(index, 'LCURLY')
        if self.peek_tok(index) == 'RCURLY':
            _, index = self.expect_tok(index, 'RCURLY')
            return TupleLValue([]), index

        vals, index = self.parse_lvalue_tuple_seq(index, [])
        return TupleLValue(vals), index

    def parse_lvalue(self, index):
        if self.peek_tok(index) == 'LCURLY':
            return self.parse_lvaluetuple(index)
        arg, index = self.parse_argument(index)
        lvalue = ArgLValue(arg)
        return lvalue, index

    def parse_variable(self, index):
        var, index = self.expect_tok(index, 'VARIABLE')
        return Variable(var), index
