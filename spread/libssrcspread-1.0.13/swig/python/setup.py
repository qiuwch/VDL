#!/usr/bin/env python
#
#
# Copyright 2006 Savarese Software Research Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.savarese.com/software/ApacheLicense-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from distutils.core import setup

setup(name='Ssrc C++/Lua/Perl/Python/Ruby Bindings for Spread',
      description='Group Communication Classes for the Spread Toolkit',
      author='Savarese Software Research Corporation',
      author_email='http://www.savarese.com/contact/',
      url='http://www.savarese.com/software/',
      packages=['ssrc'],
      package_dir = {'ssrc': '.'},
      package_data={'ssrc': ['_spread.so']}
      )