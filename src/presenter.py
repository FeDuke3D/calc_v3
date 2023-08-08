"""presenter module, the middle-man connecting view and model"""

import model


class Presenter:
    """the only class, used in view"""
    def __init__(self):
        """init method, loads model"""
        self._model = model.Model()
        self._param = 0

    @property
    def param(self):
        """parameter for simple calculation is kept here"""
        return self._param

    @param.setter
    def param(self, value):
        self._param = value

    def change_expression(self, formula):
        """sends new formula to model for parsing, returns True or False
        depending on syntax errors found by model"""
        try:
            self._model.change_expr(formula)
        except RuntimeError:
            return False
        return True

    def calculate(self) -> str:
        """runs calculation in model with current parameter's value"""
        try:
            return str(round(self._model.calc_proc(self._param), 7))
        except RuntimeError:
            return 'error'

    def calc_graph(self, coord_x_list):
        """runs a series of calculations"""
        try:
            return [self._model.calc_proc(i) for i in coord_x_list]
        except RuntimeError:
            pass

    def has_var_x(self) -> bool:
        """asks model if there is variable x in currently parsed expression"""
        return self._model.has_var_x()
