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

import unittest
import ssrc.spread

class ErrorTest(unittest.TestCase):

  def test_error(self):
    error = ssrc.spread.Error(ssrc.spread.Error.ConnectionClosed)
    self.assertEqual(ssrc.spread.Error.ConnectionClosed, error.error())

  def test_buffer_size_error(self):
    error = \
          ssrc.spread.BufferSizeError(ssrc.spread.Error.BufferTooShort, 10)
    self.assertEqual(ssrc.spread.Error.BufferTooShort, error.error())
    self.assertEqual(10, error.size())

if __name__ == '__main__':
  unittest.main()
