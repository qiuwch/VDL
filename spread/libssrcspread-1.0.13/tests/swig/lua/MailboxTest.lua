#!/usr/bin/env lua
--
--
-- Copyright 2008 Savarese Software Research Corporation
--
-- Licensed under the Apache License, Version 2.0 (the "License");
-- you may not use this file except in compliance with the License.
-- You may obtain a copy of the License at
--
--     http://www.savarese.com/software/ApacheLicense-2.0
--
-- Unless required by applicable law or agreed to in writing, software
-- distributed under the License is distributed on an "AS IS" BASIS,
-- WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
-- See the License for the specific language governing permissions and
-- limitations under the License.

require("ssrc.spread")

local TestDaemon = os.getenv("LIBSSRCSPREAD_TEST_DAEMON"):gsub('"', '')
local TestGroupName  = "MailboxTestGroup"
local TestGroupName2 = "MailboxTestGroup2"

local mbox
local rmbox
local message

function set_up()
  mbox  = ssrc.spread.Mailbox(TestDaemon, "", true, 0)
  rmbox = ssrc.spread.Mailbox(TestDaemon)
  message = ssrc.spread.Message()
end

function tear_down()
  mbox = nil
  rmbox = nil
  message = nil
end

function join_()
  mbox:join(TestGroupName)
  mbox:join(TestGroupName2)
end

function send_(s, g)
  message:clear()
  message:write(s)
  mbox:send(message, g)
end

function leave()
  mbox:leave(TestGroupName)
  mbox:leave(TestGroupName2)
end

function test_join_and_leave()
  join_()
  leave()
end

function test_send()
  join_()
  send_("test_send", TestGroupName)
  send_("test_send2", TestGroupName2)
  leave()
end

function test_scatter_send()
  local sm = ssrc.spread.ScatterMessage()
  local m  = ssrc.spread.Message()

  join_()

  message:write("test_scatter_send")
  m:write("test_scatter_send2")

  assert(sm:add(message))
  assert(sm:add(m))
  mbox:send(sm, TestGroupName)

  mbox:clear_groups()
  mbox:add_group(TestGroupName)
  mbox:clear_message_parts()

  -- If you add a straight data message part, you must make sure
  -- it does not get garbage-collected before the s.
  local s1 = "test_scatter_send3"
  assert(mbox:add_message_part(s1))
  local s2 = "test_scatter_send4"
  assert(mbox:add_message_part(s2))
  mbox:send()

  leave()
end

function test_group_send()
  local groups = ssrc.spread.GroupList()

  groups:add(TestGroupName)
  groups:add(TestGroupName2)

  join_()
  send_("test_group_send", groups)
  send_("test_group_send2", groups)
  leave()
end

function test_scatter_group_send()
  local groups = ssrc.spread.GroupList()
  local sm = ssrc.spread.ScatterMessage()
  local m = ssrc.spread.Message()

  groups:add(TestGroupName)
  groups:add(TestGroupName2)

  join_()
  message:write("test_scatter_group_send")
  m:write("test_scatter_group_send2")
  sm:add(message)
  sm:add(m)
  mbox:send(sm, groups)
  leave()
end

function test_receive_message()
  local data = "foobar"
  local groups = ssrc.spread.GroupList()
  local padding = ssrc.spread.Message()

  mbox:clear_groups()
  mbox:clear_message_parts()
  mbox:add_group(rmbox:private_group())
  mbox:add_message_part(data)
  mbox:send()

  rmbox:clear_groups()
  rmbox:clear_message_parts()
  rmbox:add_message_part(message)
  rmbox:add_message_part(padding)

  padding:resize(padding:capacity())
  assert(padding:size() > 0)

  local bytes = rmbox:receive()
  rmbox:copy_groups(groups)

  assert(padding:size() == 0)
  assert(bytes == #data + 1)
  assert(message:size() == #data + 1)
  assert(message:read(#data + 1) == data)
  assert(groups:group(0) == rmbox:private_group())
  assert(message:sender() == mbox:private_group())
end

function test_receive_membership_message()
  if not ssrc.spread.MembershipInfo then
    return
  end

  local info = ssrc.spread.MembershipInfo()

  join_()

  -- mbox join() message
  local groups = ssrc.spread.GroupList()
  mbox:receive(message, groups)

  assert(message:is_membership())
  assert(message:sender() == TestGroupName)

  message:get_membership_info(info)

  assert(info:caused_by_join())
  assert(info:changed_member() == mbox:private_group())

  local mbox_group = ssrc.spread.GroupList()
  local local_members = ssrc.spread.GroupList()
  local  all_members = ssrc.spread.GroupList()

  mbox_group:add(mbox:private_group())
  info:get_local_members(local_members)
  info:get_all_members(all_members)

  assert(mbox_group == local_members)
  assert(mbox_group == all_members)
  assert(groups == all_members)

  -- mbox join() message
  mbox:receive(message)
  assert(message:is_membership())
  assert(message:sender() == TestGroupName2)

  -- rmbox join() message
  rmbox:join(TestGroupName2)

  mbox:receive(message)
  assert(message:is_membership())
  assert(message:sender() == TestGroupName2)

  -- rmbox leave() message
  rmbox:leave(TestGroupName2)

  mbox:receive(message)
  assert(message:is_membership())

  message:get_membership_info(info)

  assert(info:caused_by_leave())
  assert(message:sender() == TestGroupName2)

  leave()
end

function test_self_leave_message()
  if not ssrc.spread.MembershipInfo then
    return
  end

  mbox:join(TestGroupName)
  mbox:receive(message)
  mbox:leave(TestGroupName)
  mbox:receive(message)

  local info = ssrc.spread.MembershipInfo()

  message:get_membership_info(info)

  assert(info:caused_by_leave())
  assert(info:is_self_leave())
end

function test_error()
  local succeeded, message = pcall(mbox.join, mbox, "####");
  assert(not succeeded)
end

function run_test(test)
  set_up()
  test()
  tear_down()
end

local Tests = {
  test_join_and_leave,
  test_send,
  test_scatter_send,
  test_group_send,
  test_scatter_group_send,
  test_receive_message,
  test_receive_membership_message,
  test_self_leave_message,
  test_error
}

for i = 1, #Tests do
  run_test(Tests[i])
end
