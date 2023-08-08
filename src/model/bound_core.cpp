#include "calc_core.h"
#include <pybind11/pybind11.h>

namespace py = pybind11;

PYBIND11_MODULE(bound_core, m) {
    m.doc() = "This is a Python binding of C++ calc_core library";

    py::class_<s21::Model>(m, "Model")
        .def(py::init())
        .def("change_expr", &s21::Model::ChangeExpr)
        .def("calc_proc", &s21::Model::CalcProc)
        .def("has_var_x", &s21::Model::HasVarX)
        ;
}