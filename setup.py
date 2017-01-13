#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: xiLin.ding


from setuptools import setup, find_packages


setup(
    name='django-aliyun-oss',
    version='0.2',
    packages=find_packages(),
    author='WANG Jian',
    author_email='waen.wj@gmail.com',
    url='https://github.com/waenwj/django-aliyun-oss/',
    description='django aliyun oss backend',
    long_description=open('README.md').read(),
    license='Apache2',
    requires=[
        'Django',
        #'alioss',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: System :: Installation/Setup'
    ],
    include_package_data=True,
    zip_safe=False
)
