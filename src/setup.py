# from setuptools import setup, Extension
from distutils.core import setup, Extension

import pybind11

ext_modules = [
    Extension(
        'model.bound_core',
        ['model/bound_core.cpp', 'model/calc_core.cpp'],
        include_dirs=[
            pybind11.get_include(),
            'model/'
        ],
        language='c++',
        extra_compile_args=['-lstdc++', '-std=c++17'],
        depends=['model/calc_core.h']
    )
]

setup(
    name='smart_calc_v3',
    version='1.0',
    author='irobin',
    author_email='irobin@student.21-school.ru',
    py_modules=['smart_calc_v3', 'view', 'presenter'],
    ext_modules=ext_modules,
    setup_requires=[
        'pybind11',
        'importlib-metadata; python_version == "3.11"',
        'customtkinter',
        'matplotlib',
        'pytest',
    ],
    data_files=[
        ('manual', ['manual/formula.txt',
                    'manual/graph.txt',
                    'manual/help.txt',
                    'manual/limits.txt',
                    'manual/tools.txt',
                    'manual/variable.txt']),
    ],
    app=['smart_calc_v3.py'],
)
