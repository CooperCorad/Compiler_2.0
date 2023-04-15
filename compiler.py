import sys
import mylexer
import myparser
import mytypechecker
import myasmgenerator

def main():

    flag = sys.argv[1]
    file_spec = sys.argv[2]
    optimization = 0
    if len(sys.argv) == 4:
        optimization = int(sys.argv[2][2:])
        file_spec = sys.argv[3]
    #
    # flag = '-s'
    # file_spec = 'test.jpl'
    # optimization = 2
    # optimization = 1
    # optimization = 0

    if flag[0] != '-':
        temp = flag
        flag = file_spec
        file_spec = temp
    try:
        file_reader = open(file_spec, 'r')
        file = ''.join(file_reader.readlines())
        file_reader.close()
    except Exception as error:
        print("Compilation failed! " + error.__str__())
        exit(0)

    if flag == '-l':
        try:
            newlexer = mylexer.Lexer(file)
            newlexer.runner()
            for x in newlexer.tokens:
                if x.t == 'NEWLINE':
                    print('NEWLINE')
                elif x.t == 'END_OF_FILE':
                    print('END_OF_FILE')
                else:
                    res = x.t + ' \'' + x.text + '\''
                    print(res)
            print('Compilation succeeded: lexical analysis complete')

        except mylexer.LexerError as error:
            print(error.message)
            exit(0)

    elif flag == '-p':

        try:
            newlexer = mylexer.Lexer(file)
            newlexer.runner()

            newparser = myparser.Parser(newlexer.tokens)
            newparser.parse()
            print(newparser.to_string())
            print('\nCompilation succeeded')
        except Exception as exception:
            # print('Compilation failed ' + exception.__str__())
            print('Compilation failed: ' + exception.__str__())
            exit(0)

    elif flag == '-t':
        try:
            newlexer = mylexer.Lexer(file)
            newlexer.runner()

            newparser = myparser.Parser(newlexer.tokens)
            newparser.parse()

            newtypechecker = mytypechecker.TypeChecker(newparser.program)
            newtypechecker.type_check()
            print(newtypechecker.to_string())
            print('\nCompilation succeeded')

        except Exception as exception:
            # print('Compilation failed ' + exception.__str__())
            print('Compilation failed: ' + exception.__str__())
            exit(0)

    elif flag == '-s':
        try:
            newlexer = mylexer.Lexer(file)
            newlexer.runner()

            newparser = myparser.Parser(newlexer.tokens)
            newparser.parse()

            newtypechecker = mytypechecker.TypeChecker(newparser.program)
            newtypechecker.type_check()

            if optimization > 1:
                newconstantpropagator = mytypechecker.ConstantPropogation(newtypechecker.exprTree)
                newconstantpropagator.prop_constants()

            newasmgen = myasmgenerator.AsmGenerator(newtypechecker.exprTree)
            newasmgen.oplvl = optimization
            newasmgen.generate_code()
            string = newasmgen.to_string()
            print(string)
            print('\nCompilation succeeded: assembly complete')

        except Exception as exception:
            # print('Compilation failed ' + exception.__str__())
            print('Compilation failed: ' + exception.__str__())
            exit(0)
    else:
        print('Valid flags: \n\t\'-l\': lex the program\n \t\'-p\': parse the program\n \t\'-t\': typecheck the program'
              '\n\t\'-s\': compile the program')


if __name__ == '__main__':
    main()


