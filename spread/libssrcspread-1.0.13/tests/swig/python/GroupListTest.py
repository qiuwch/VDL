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

class GroupListTest(unittest.TestCase):
  
  def setUp(self):
    self.groups = ssrc.spread.GroupList()

  def tearDown(self):
    self.groups = None
  
  def test_add(self):
    self.assertEqual(0, self.groups.size())
    self.groups.add("foo")
    self.assertEqual(1, self.groups.size())
    self.assertEqual("foo", self.groups.group(0))
    self.groups.add("bar")
    self.assertEqual(2, self.groups.size())
    self.assertEqual("bar", self.groups.group(1))

  def test_add_group_list(self):
    self.groups.add("foo")
    self.groups.add("bar")

    g = ssrc.spread.GroupList()

    g.add("foobar")
    g.add("blah")
    g.add("blargh")

    self.groups.add(g)

    self.assertEqual(5, self.groups.size())
    self.assertEqual("blargh", self.groups.group(4))
    self.assertEqual("bar", self.groups.group(1))

    self.assertNotEqual(g, self.groups)

    self.groups.clear()
    self.groups.add(g)

    self.assertEqual(g, self.groups)

  def test_copy(self):
    g2 = ssrc.spread.GroupList()
    g2.add("foo")
    self.assertNotEqual(g2, self.groups)
    self.groups.copy(g2)
    self.assertEqual("foo", self.groups.group(0))
    self.assertEqual(g2, self.groups)
  
  def test_split_private_group(self):
    private_name, proc_name = ssrc.spread.split_private_group("#foo#bar")
    self.assertEqual("foo", private_name)
    self.assertEqual("bar", proc_name)

if __name__ == '__main__':
  unittest.main()
