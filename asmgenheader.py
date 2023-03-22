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
        self.nameloc[lval.variable.variable.variable] = (8 + self.localvarsize)


    def haslval(self, lval: ArgLValue):
        return lval.variable.variable.variable in self.nameloc.keys()


class AsmGenException(Exception):
    def __init__(self, _message):
        self.message = _message
        super().__init__(self.message)


