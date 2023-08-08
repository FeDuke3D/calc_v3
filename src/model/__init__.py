"""model module, just a wrap for bound c++ model"""

from model.bound_core import *

if __name__ == '__main__':
    model = Model()
    model.change_expr('2+x')
    print(model.calc_proc(3) == 5)
