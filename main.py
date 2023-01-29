import re

toktype = {"array": "ARRAY", "assert" : "ASSERT", "bool" : "BOOL", "else" : "ELSE", "false" : "FALSE",
       "float" : "FLOAT", "fn" : "FN", "if" : "IF", "image" : "IMAGE", "int" : "INT", "let" : "LET", "print" : "PRINT",
       "return" : "RETURN", "show" : "SHOW", "sum" : "SUM", "then" : "THEN", "time" : "TIME", "to" : "TO",
       "true" : "TRUE", "type" : "TYPE", "write" : "WRITE", ":" : "COLON", "{" : "LCURLY", "}" : "RCURLY",
       "(" : "LPAREN", ")" : "RPAREN", "," : "COMMA", "[" : "LSQUARE",  "]" : "RSQUARE", "=" : "EQUALS",
       "string" : "STRING", "intval" : "INTVAL", "floatval" : "FLOATVAL", "var" : "VARIABLE", "op" : "OP",
       "read" : "READ", "nl" : "NEWLINE", "eof" : "END_OF_FILE"}


class Token:
    def __init__(self, _t : str, _start : int, _text : str):
        self.t = _t
        self.start = _start
        self.text = _text


class LexerError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class Lexer:
    def __init__(self, _file):
        self.file = _file
        self.file_size = len(_file)
        self.tokens = []


    def lex_white_space(self, index : int):
        has_newline = False

        while index < self.file_size:
            if self.file[index] == ' ':
                index += 1
            elif self.file[index] == '/':
                if index + 1 == self.file_size:
                    break
                next_char = self.file[index + 1]
                if next_char == '/':
                    while index < self.file_size and self.file[index] != '\n':
                        index += 1
                    if not has_newline:
                        has_newline = True
                        self.tokens.append(Token(toktype['nl'], index, 'NEWLINE'))
                    index += 1
                elif next_char == '*':
                    index += 2
                    while index < self.file_size:
                        if index == self.file_size - 1:
                            raise LexerError("No end to multiline comment!")
                        if self.file[index] == '*' and self.file[index + 1] == '/':
                            if not has_newline:
                                has_newline = True
                                self.tokens.append(Token(toktype['nl'], index, 'NEWLINE'))
                            index += 1
                            break
                        index += 1
                    index += 2
                else:
                    break
            elif self.file[index] == '\\':
                has_newline = True
                index += 1
            elif self.file[index] == '\n':
                if not has_newline:
                    has_newline = True
                    self.tokens.append(Token(toktype['nl'], index, 'nl'))
                    index += 1
                index += 1
            elif index == self.file_size:
                self.tokens.append(Token(toktype['eof'], index, 'EOF'))
                break
            else:
                break
        return index

    def lex_punct(self, index : int):
        reg_punct = '^[\\:\\{\\}\\(\\)\\[\\],=]'

        search = re.search(reg_punct, self.file[index:])
        if search is None:
            raise LexerError("Unable to find punctuation at :" + str(index))

        tokstr = search[0]
        return Token(toktype[tokstr], index, tokstr), index + len(tokstr)

    def lex_string(self, index : int):
        tokstr = ''

        if self.file[index] != '\"':
            raise LexerError("Unable to find string at: " + str(index))
        else:
            tokstr += '\"'
            index += 1

        while index < self.file_size and (32 <= ord(self.file[index]) <= 126) and self.file[index] != '\"':
            if self.file[index] == '\n' or ord(self.file[index]) == 4:
                raise LexerError("You cannot have a newline\\eof in your string!")
            tokstr += self.file[index]
            index += 1

        if index == self.file_size:
            raise LexerError("You've reached the end of the file without string termination")

        tokstr += '\"'
        index += 1

        return Token(toktype["string"], index, tokstr), index

    def lex_variable(self, index: int):
        reg_variable = '^[a-zA-Z]+[a-zA-Z0-9_\\.]*'

        search = re.search(reg_variable, self.file[index:])
        if search is None:
            error = "Unable to find variable at : " + str(index)
            raise LexerError(error)

        tokstr = search[0]

        if tokstr in toktype.keys():
            return Token(toktype[tokstr], index, tokstr), index + len(tokstr)
        return Token(toktype["var"], index, tokstr), index + len(tokstr)

    def lex_operator(self, index: int):
        reg_operator = '^((&&)|(\\|\\|)|(<=)|(>=)|(<)|(>)|(==)|(!=)|(\\+)|(-)|(\\*)|(/)|(%)|(!))'

        search = re.search(reg_operator, self.file[index:])
        if search is None:
            error = "Unable to find operator at : " + str(index)
            raise LexerError(error)

        tokstr = search[0]
        return Token(toktype['op'], index, tokstr), index + len(tokstr)

    # TODO perhaps unnecessary??
    def lex_keyword(self, index : int):
        reg_keyword = '^((array)|(assert)|(bool)|(else)|(false)|(float)|(fn)|(if)|(image)|(int)' \
                      '|(let)|(print)|(read)|(return)|(show)|(sum)|(then)|(time)|(to)|(true)|(type)|(write))'

        search = re.search(reg_keyword, self.file[index:])
        if search is None:
            error = "Unable to find keyword at : " + str(index)
            raise LexerError(error)

        tokstr = search[0]
        return Token(toktype[tokstr], index, tokstr), index + len(tokstr)

    def lex_number(self, index : int):
        reg_float = '(^[0-9]+\\.[0-9]*)|(^[0-9]*\\.[0-9]+)'
        reg_int = '^[0-9]+'

        search = re.search(reg_float, self.file[index:])
        if search is None:
            search = re.search(reg_int, self.file[index:])

            if search is None:
                error = "Unable to find number at : " + str(index)
                raise LexerError(error)

            tokstr = search[0]

            return Token(toktype['intval'], index, tokstr), index + len(tokstr)

        tokstr = search[0]
        return Token(toktype['floatval'], index, tokstr), index + len(tokstr)

    def try_lex(self, index : int):
        if index >= self.file_size:
            raise LexerError("end of file uncerimoniously reached!")

        ret = tuple()
        try:
            ret = self.lex_number(index)
        except LexerError as error:
            try:
                ret = self.lex_variable(index)
            except LexerError as error:
                try:
                    ret = self.lex_keyword(index)
                except LexerError as error:
                    try:
                        ret = self.lex_operator(index)
                    except LexerError as error:
                        try:
                            ret = self.lex_punct(index)
                        except LexerError as error:
                            try:
                                ret = self.lex_string(index)
                            except LexerError as error:
                                raise LexerError(error.message)

        return ret

    def runner(self):
        index = 0

        while index < self.file_size:
            try:
                index = self.lex_white_space(index)
                print(self.file[index:])
                tok, index = self.try_lex(index)
                self.tokens.append(tok)

            except LexerError as error:
                print("Compilation failed ", error.message)
                exit(0)

        if len(self.tokens) == 0 or (len(self.tokens) > 0 and self.tokens[len(self.tokens) - 1].t is not toktype['eof']):
            self.tokens.append(Token(toktype['eof'], index, 'EOF'))


def main():

    # flag = sys.argv[1]
    # file_spec = sys.argv[2]
    flag = '-l'
    file_spec = 'C:\\Users\\coope\\PycharmProjects\\testzone\\venv\\test.jpl'

    if flag[0] != '-':
        temp = flag
        flag = file_spec
        file_spec = temp
    file_reader = open(file_spec, 'r')
    file = ''.join(file_reader.readlines())
    file_reader.close()
    # print(file)

    if flag == '-l':
        try:
            print(file)
            lexer = Lexer(file)
            lexer.runner()
            for x in lexer.tokens:
                print("type ", x.t, " text ", x.text)

        except LexerError as error:
            print(error.message)
            exit(0)

    elif flag == '-p':
        exit(0)
    elif flag == '-t':
        exit(0)
    else:
        print('A flag (-l, -p, -t) is required')




if __name__ == '__main__':
    main()


