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
#

import unittest
import os
import time
import ssrc.spread

class MailboxTest(unittest.TestCase):

  TestDaemon = os.environ["LIBSSRCSPREAD_TEST_DAEMON"].replace('"','')
  TestGroupName  = "MailboxTestGroup"
  TestGroupName2 = "MailboxTestGroup2"

  def setUp(self):
    try:
      self.mbox = ssrc.spread.Mailbox(MailboxTest.TestDaemon, "", True, 0)
      self.rmbox = ssrc.spread.Mailbox(MailboxTest.TestDaemon)
    except ssrc.spread.Error as error:
      error._print()
      raise error

    self.message = ssrc.spread.Message()

  def tearDown(self):
    self.mbox = None
    self.rmbox = None
    self.message = None
    # TODO: There's race condition in the Python binding that causes
    # test_self_leave_message to occasionally fail with INVALID_MESSAGE
    # when more than one spread daemon is in the test daemon's segment.
    # The cause is likely related to the Python garbage collector.  Until
    # there's time to investigate this bug, we kluge a pause to work
    # around the issue and allow the test to pass.
    time.sleep(0.05)
  
  def join(self):
    self.mbox.join(MailboxTest.TestGroupName)
    self.mbox.join(MailboxTest.TestGroupName2)
  
  def leave(self):
    self.mbox.leave(MailboxTest.TestGroupName)
    self.mbox.leave(MailboxTest.TestGroupName2)
  
  def test_join_and_leave(self):
    self.join()
    self.leave()
  
  def test_send(self):
    def send(s, g):
      self.message.clear()
      self.message.write(s)
      self.mbox.send(self.message, g)
    self.join()
    send("test_send", MailboxTest.TestGroupName)
    send("test_send2", MailboxTest.TestGroupName2)
    self.leave()

  def test_scatter_send(self):
    sm = ssrc.spread.ScatterMessage()
    m  = ssrc.spread.Message()

    self.join()

    self.message.write("test_scatter_send")
    m.write("test_scatter_send2")

    self.assertTrue(sm.add(self.message))
    self.assertTrue(sm.add(m))
    self.mbox.send(sm, MailboxTest.TestGroupName)

    self.mbox.clear_groups()
    self.mbox.add_group(MailboxTest.TestGroupName)
    self.mbox.clear_message_parts()

    # If you add a straight data message part, you must make sure
    # it does not get garbage-collected before the s.
    s1 = "test_scatter_send3"
    self.assertTrue(self.mbox.add_message_part(s1))
    s2 = "test_scatter_send4"
    self.assertTrue(self.mbox.add_message_part(s2))
    self.mbox.send()

    self.leave()

  def test_group_send(self):
    groups = ssrc.spread.GroupList()

    groups.add(MailboxTest.TestGroupName)
    groups.add(MailboxTest.TestGroupName2)

    def send(s,g):
      self.message.clear()
      self.message.write(s)
      self.mbox.send(self.message, g)

    self.join()
    send("test_group_send", groups)
    send("test_group_send2", groups)
    self.leave()

  def test_scatter_group_send(self):
    groups = ssrc.spread.GroupList()
    sm = ssrc.spread.ScatterMessage()
    m = ssrc.spread.Message()

    groups.add(MailboxTest.TestGroupName)
    groups.add(MailboxTest.TestGroupName2)

    self.join()
    self.message.write("test_scatter_group_send")
    m.write("test_scatter_group_send2")
    sm.add(self.message)
    sm.add(m)
    self.mbox.send(sm, groups)
    self.leave()
  
  def test_receive_message(self):
    data = "foobar"

    groups = ssrc.spread.GroupList()
    padding = ssrc.spread.Message()

    self.mbox.clear_groups()
    self.mbox.clear_message_parts()
    self.mbox.add_group(self.rmbox.private_group())
    self.mbox.add_message_part(data)
    self.mbox.send()

    self.rmbox.clear_groups()
    self.rmbox.clear_message_parts()
    self.rmbox.add_message_part(self.message)
    self.rmbox.add_message_part(padding)

    padding.resize(padding.capacity())
    self.assertTrue(padding.size() > 0)

    bytes = self.rmbox.receive()
    self.rmbox.copy_groups(groups)

    self.assertEqual(0, padding.size())
    self.assertEqual(len(data) + 1, bytes)
    self.assertEqual(len(data) + 1, self.message.size())
    self.assertEqual(data, self.message.read(len(data) + 1))
    self.assertEqual(self.rmbox.private_group(), groups.group(0))
    self.assertEqual(self.mbox.private_group(), self.message.sender())

  def test_receive_membership_message(self):
    if not 'MembershipInfo' in dir(ssrc.spread):
      return

    info = ssrc.spread.MembershipInfo()

    self.join()

    # mbox self.join() message
    groups = ssrc.spread.GroupList()
    self.mbox.receive(self.message, groups)

    self.assertTrue(self.message.is_membership())
    self.assertEqual(MailboxTest.TestGroupName, self.message.sender())

    self.message.get_membership_info(info)

    self.assertTrue(info.caused_by_join())
    self.assertEqual(self.mbox.private_group(), info.changed_member())

    mbox_group = ssrc.spread.GroupList()
    local_members = ssrc.spread.GroupList()
    all_members = ssrc.spread.GroupList()

    mbox_group.add(self.mbox.private_group())
    info.get_local_members(local_members)
    info.get_all_members(all_members)

    self.assertEqual(mbox_group, local_members)
    self.assertEqual(mbox_group, all_members)
    self.assertEqual(groups, all_members)

    # mbox self.join() message
    self.mbox.receive(self.message)
    self.assertTrue(self.message.is_membership())
    self.assertEqual(MailboxTest.TestGroupName2, self.message.sender())

    # rmbox self.join() message
    self.rmbox.join(MailboxTest.TestGroupName2)

    self.mbox.receive(self.message)
    self.assertTrue(self.message.is_membership())
    self.assertEqual(MailboxTest.TestGroupName2, self.message.sender())

    # rmbox self.leave() message
    self.rmbox.leave(MailboxTest.TestGroupName2)

    self.mbox.receive(self.message)
    self.assertTrue(self.message.is_membership())

    self.message.get_membership_info(info)

    self.assertTrue(info.caused_by_leave())
    self.assertEqual(MailboxTest.TestGroupName2, self.message.sender())

    self.leave()

  def test_self_leave_message(self):
    if not 'MembershipInfo' in dir(ssrc.spread):
      return
    
    self.mbox.join(MailboxTest.TestGroupName)
    self.mbox.receive(self.message)
    self.mbox.leave(MailboxTest.TestGroupName)
    self.mbox.receive(self.message)

    info = ssrc.spread.MembershipInfo()

    self.message.get_membership_info(info)

    self.assertTrue(info.caused_by_leave())
    self.assertTrue(info.is_self_leave())

  def test_error(self):
    try:
      self.mbox.join("####")
    except ssrc.spread.Error as e:
      self.assertEqual(ssrc.spread.Error.IllegalGroup, e.error())
    else:
      self.assertTrue(False)

if __name__ == '__main__':
  unittest.main()
