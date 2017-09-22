#coding=utf-8

from setuptools import setup, find_packages

setup(
    name='mtx',
    version='1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click>=6.0',
        'pyyaml>=3.11',
    ],
    entry_points='''
        [console_scripts]
        mtx=matrix.cmd:main
    ''',
)
