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

function test_capacity()
  local message = ssrc.spread.Message()
  assert(message:capacity() > 0)
  assert(message:capacity()== ssrc.spread.Message_DefaultCapacity)
end

function test_self_discard()
  local message = ssrc.spread.Message()
  assert(not message:is_self_discard())
  message:set_self_discard()
  assert(message:is_self_discard())
  message:set_self_discard(false)
  assert(not message:is_self_discard())
end

function test_service()
  local message = ssrc.spread.Message()
  local service = ssrc.spread.BaseMessage_ReliableSelfDiscard
  message:set_service(service)
  assert(message:service() == service)
  assert(message:is_self_discard())
  assert(message:is_reliable())
  assert(not message:is_fifo())
end

function test_write()
  local message = ssrc.spread.Message()
  message:writen("test_scatter_send", 17)
  assert(message:size() == 17)
  message:clear()
  message:write("test_scatter_send2")
  -- Includes null terminator
  assert(message:size() == 18 + 1)
end
  
function test_read()
  local message = ssrc.spread.Message()
  message:write("foobar")
  message:rewind()
  local foo = message:read(3)
  assert(foo == "foo")
  foo = message:read(3)
  assert(foo == "bar")
end

test_capacity()
test_self_discard()
test_service()
test_write()
test_read()
