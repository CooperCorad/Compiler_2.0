

class Ty:
    def to_string(self):
        return ''


class IntTy(Ty):
    def to_string(self):
        return '(IntType)'

    def equals(self, otherty):
        return type(otherty) is IntTy


class FloatTy(Ty):
    def to_string(self):
        return '(FloatType)'

    def equals(self, otherty):
        return type(otherty) is FloatTy


class BoolTy(Ty):
    def to_string(self):
        return '(BoolType)'

    def equals(self, otherty):
        return type(otherty) is BoolTy


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

    def equals(self, otherty):
        if type(otherty) is not TupleTy or self.rank != otherty.rank:
            return False
        for i in range(len(self.tys)):
            if not self.tys[i].equals(otherty.tys[i]):
                return False
        return True



class ArrayTy(Ty):
    def __init__(self, _ty, _rank: int):
        self.ty = _ty
        self.rank = _rank

    def to_string(self):
        ret = '(ArrayType ' + self.ty.to_string() + ' ' + str(self.rank) + ')'
        return ret

    def equals(self, otherty):
        if type(otherty) is not ArrayTy:
            return False
        return type(self.ty) is type(otherty.ty) and self.rank == otherty.rank


class TypeCheckerException(Exception):
    def __init__(self, _message):
        self.message = _message
        super().__init__(self.message)
