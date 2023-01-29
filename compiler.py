import re
import sys
import mylexer

def main():

    flag = sys.argv[1]
    file_spec = sys.argv[2]

    if flag[0] != '-':
        temp = flag
        flag = file_spec
        file_spec = temp
    try:
        file_reader = open(file_spec, 'r')
        file = ''.join(file_reader.readlines())
        file_reader.close()
    except Exception:
        print("Compilation failed!")
        exit(0)

    if flag == '-l':
        try:
            # print(file)
            newlexer = mylexer.Lexer(file)
            newlexer.runner()
            for x in newlexer.tokens:
                # print('|',x.text,'|')
                # print('|', x.t , '|')
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
        exit(0)
    elif flag == '-t':
        exit(0)
    else:
        print('A flag (-l, -p, -t) is required')


if __name__ == '__main__':
    main()


