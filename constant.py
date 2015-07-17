__author__ = 'nmg'

class ConstError(TypeError):
    pass

class ConstCaseError(ConstError):
    pass

class Const(object):

    def __setattr__(self, key, value):
        if key in self.__dict__:
            raise ConstError()

        self.__dict__[key] = value


import sys
sys.modules[__name__] = Const()
import constant
print(sys.modules[__name__])

