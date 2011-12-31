#!/usr/bin/env python

# Copyright (C) 2011, Valentin Lorentz
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import with_statement

import os
from distutils.core import setup
from DistUtilsExtra.command import *

import wididit

def recursive_listdir(base_path):
    files = []
    subdirectories = []
    for item in os.listdir(base_path):
        item_path = os.path.join(base_path, item)
        (files if os.path.isfile(item_path) else subdirlist).append(item_path)
    for subdirectory in subdirectories:
        files.extend(resursive_listdir(subdirectory))
    return files

if os.path.isfile('po/POTFILES.in'):
    os.unlink('po/POTFILES.in')
files = [x for x in recursive_listdir('wididit') if x.endswith('.py')]
with open('po/POTFILES.in', 'a') as fd:
    fd.write('\n'.join(files))

setup(name='wididit',
      version=wididit.__version__,
      description='The Wididit social network library',
      author='Valentin Lorentz',
      author_email='progval@gmail.com',
      url='http://python.wididit.net/',
      packages=['wididit'],
      requires=['requests'],
      cmdclass = {'build': build_extra.build_extra,
                  'build_i18n': build_i18n.build_i18n,
                 }

     )
