from setuptools import setup, Extension

import pybind11
# import os

ext_modules = [
    Extension(
        'bound_core',
        ['bound_core.cpp', 'calc_core.cpp'],
        include_dirs=[
            pybind11.get_include(),
            # os.system("locate include/python3.11 | grep 'python3.11$'")
        ],
        language='c++',
        extra_compile_args=['-lstdc++', '-std=c++17'],
    )
]

setup(
    name='bound_core',
    version='1',
    ext_modules=ext_modules,
    setup_requires=[
        'pybind11',
        'importlib-metadata; python_version == "3.11"',
    ],
)
