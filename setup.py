#!/usr/bin/env python

from setuptools import setup

setup(name='caravan_phidgets',
    version='0.0.1',
    description='Phidgets module for Caravan',
    author='Alexey Balekhov',
    author_email='a@balek.ru',
    py_modules = ['caravan_phidgets'],
    entry_points = {
        'autobahn.twisted.wamplet': [ 'phidgets = caravan_phidgets:AppSession' ]
    })