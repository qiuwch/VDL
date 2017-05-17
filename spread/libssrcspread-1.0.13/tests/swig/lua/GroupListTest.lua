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

function test_add()
  local groups = ssrc.spread.GroupList()
  assert(groups:size() == 0)
  groups:add("foo")
  assert(groups:size() == 1)
  assert(groups:group(0) == "foo")
  groups:add("bar")
  assert(groups:size() == 2)
  assert(groups:group(1) == "bar")
end

function test_add_group_list()
  local groups = ssrc.spread.GroupList()
  local g = ssrc.spread.GroupList()

  groups:add("foo")
  groups:add("bar")

  g:add("foobar")
  g:add("blah")
  g:add("blargh")

  groups:add(g)

  assert(groups:size() == 5)
  assert(groups:group(4) == "blargh")
  assert(groups:group(1) == "bar")

  assert(groups ~= g)

  groups:clear()
  groups:add(g)

  assert(g == groups)
end

function test_copy()
  local groups = ssrc.spread.GroupList()
  local g2 = ssrc.spread.GroupList()

  g2:add("foo")
  assert(g2 ~= groups)
  groups:copy(g2)
  assert(groups:group(0) == "foo")
  assert(g2 == groups)
end

function test_split_private_group()
  local name = ssrc.spread.split_private_group("#foo#bar")
  assert("foo" == name.first)
  assert("bar" == name.second)
end

test_add()
test_add_group_list()
test_copy()
test_split_private_group()

