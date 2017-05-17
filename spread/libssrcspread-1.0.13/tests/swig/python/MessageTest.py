#!/usr/bin/env python
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

class MessageTest(unittest.TestCase):

  def setUp(self):
    self.message = ssrc.spread.Message()
  
  def tearDown(self):
    self.message = None

  def test_capacity(self):
    self.assertEqual(ssrc.spread.Message.DefaultCapacity, self.message.capacity())

  def test_self_discard(self):
    self.assertTrue(not self.message.is_self_discard())
    self.message.set_self_discard()
    self.assertTrue(self.message.is_self_discard())
    self.message.set_self_discard(False)
    self.assertTrue(not self.message.is_self_discard())

  def test_service(self):
    service = ssrc.spread.Message.Reliable | ssrc.spread.Message.SelfDiscard
    self.message.set_service(service)
    self.assertEqual(service, self.message.service())
    self.assertTrue(self.message.is_self_discard())
    self.assertTrue(self.message.is_reliable())
    self.assertTrue(not self.message.is_fifo())

  def test_write(self):
    self.message.writen("test_scatter_send", 17)
    self.assertEqual(17, self.message.size())
    self.message.clear()
    self.message.write("test_scatter_send2")
    # Includes null terminator
    self.assertEqual(18 + 1, self.message.size())
  
  def test_read(self):
    self.message.write("foobar")
    self.message.rewind()
    foo = self.message.read(3)
    self.assertEqual("foo", foo)
    # Can't use readn in Python because strings are immutable!
    #foo = "   "
    #self.message.readn(foo, 3)
    foo = self.message.read(3)
    self.assertEqual("bar", foo)
  
if __name__ == '__main__':
  unittest.main()

