

class Ty:
    def to_string(self):
        return ''


class IntTy(Ty):
    def to_string(self):
        return '(IntType)'


class FloatTy(Ty):
    def to_string(self):
        return '(FloatType)'


class BoolTy(Ty):
    def to_string(self):
        return '(BoolType)'


class TupleTy(Ty):
    tys: []

    def __init__(self, _tys: []):
        self.tys = _tys
        self.rank = len(_tys)

    def to_string(self):
        ret = '(TupleType '
        for typs in self.tys:
            ret += typs.to_string() + ' '
        return ret[:-1] + ')'


class ArrayTy(Ty):
    def __init__(self, _ty, _rank: int):
        self.ty = _ty
        self.rank = _rank

    def to_string(self):
        ret = '(ArrayType ' + self.ty.to_string() + ' ' + str(self.rank) + ')'
        return ret

class TypeCheckerException(Exception):
    def __init__(self, _message):
        self.message = _message
        super().__init__(self.message)
