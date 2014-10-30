#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: xiLin.ding


from setuptools import setup, find_packages


setup(
    name='django-aliyun-oss',
    version='0.1',
    packages=find_packages(),
    author='WANG Tai',
    author_email='wangtai@bugua.com',
    url='https://github.com/YuelianINC',
    description='django aliyun oss backend',
    long_description=open('README.md').read(),
    license='Apache2',
    requires=[
        'Django',
        'alioss',
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
