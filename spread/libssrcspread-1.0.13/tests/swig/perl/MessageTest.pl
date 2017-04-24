#!/usr/bin/env perl
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

use strict;
use Test::More tests => 13;
use ssrc::spread;

sub test_capacity {
  my $message = new ssrc::spread::Message();
  isnt($message->capacity(), 0);
  is($message->capacity(), $ssrc::spread::Message::DefaultCapacity);
}

sub test_self_discard {
  my $message = new ssrc::spread::Message();
  ok(not $message->is_self_discard());
  $message->set_self_discard();
  ok($message->is_self_discard());
  $message->set_self_discard(0);
  ok(not $message->is_self_discard());
}

sub test_service {
  my $message = new ssrc::spread::Message();
  my $service = ($ssrc::spread::BaseMessage::Reliable |
                 $ssrc::spread::BaseMessage::SelfDiscard);
  $message->set_service($service);
  is($message->service(), $service);
  ok($message->is_self_discard());
  ok($message->is_reliable());
  ok(not $message->is_fifo());
}

sub test_write {
  my $message = new ssrc::spread::Message();
  $message->writen("test_scatter_send", 17);
  is($message->size(), 17);
  $message->clear();
  $message->write("test_scatter_send2");
  # Includes null terminator
  is($message->size(), 18 + 1);
}
  
sub test_read {
  my $message = new ssrc::spread::Message();
  $message->write("foobar");
  $message->rewind();
  my $foo = $message->read(3);
  is($foo, "foo");
  $foo = "   ";
  $message->readn($foo, 3);
  is($foo, "bar");
}

test_capacity();
test_self_discard();
test_service();
test_write();
test_read();
