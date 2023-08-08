import model
import pytest


class TestClass:
    @staticmethod
    def test_parse_exceptions():
        m = model.Model()
        with pytest.raises(RuntimeError):
            m.change_expr('1qwer')
        with pytest.raises(RuntimeError):
            m.change_expr('1+2)(3-4)')
        with pytest.raises(RuntimeError):
            m.change_expr('(1+2')
        with pytest.raises(RuntimeError):
            m.change_expr('sincos')

    @staticmethod
    def test_calc_simple():
        m = model.Model()
        m.change_expr('2+2*2')
        assert m.calc_proc(0) == 6

    @staticmethod
    def test_calc_u_minus():
        a = model.Model()
        b = model.Model()
        a.change_expr('sinx')
        b.change_expr('sin-x')
        assert a.calc_proc(0.5) == - b.calc_proc(0.5)
        a.change_expr('cosx')
        b.change_expr('cos-x')
        assert a.calc_proc(0.5) == b.calc_proc(0.5)

    @staticmethod
    def test_calc_all_functions():
        a = model.Model()
        a.change_expr('cos0+sin0+tan0*acos0-asin0+atan0-sqrt1+ln1-log1')
        assert a.calc_proc(0) == 0
        a.change_expr('-1+2*3/2modx')
        assert a.calc_proc(2) == 0
        a.change_expr('2^3^2')
        assert a.calc_proc(0) == 512

    @staticmethod
    def test_persistence():
        a = model.Model()
        a.change_expr('7/2')
        assert a.calc_proc(0) == 3.5
        assert a.calc_proc(0) == 3.5

    @staticmethod
    def test_scientific_overflow():
        a = model.Model()
        with pytest.raises(RuntimeError):
            a.change_expr('1e999')
