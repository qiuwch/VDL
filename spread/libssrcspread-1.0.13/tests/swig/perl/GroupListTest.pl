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

sub test_add {
  my $groups = new ssrc::spread::GroupList();
  is($groups->size(), 0);
  $groups->add("foo");
  is($groups->size(), 1);
  is($groups->group(0), "foo");
  $groups->add("bar");
  is($groups->size(), 2);
  is($groups->group(1), "bar");
}

sub test_add_group_list {
  my $groups = new ssrc::spread::GroupList();
  my $g = new ssrc::spread::GroupList();

  $groups->add("foo");
  $groups->add("bar");

  $g->add("foobar");
  $g->add("blah");
  $g->add("blargh");

  $groups->add($g);

  is($groups->size(), 5);
  is($groups->group(4), "blargh");
  is($groups->group(1), "bar");

  isnt($groups, $g);

  $groups->clear();
  $groups->add($g);

  ok($g == $groups);
}

sub test_copy {
  my $groups = new ssrc::spread::GroupList();
  my $g2 = new ssrc::spread::GroupList();

  $g2->add("foo");
  ok($g2 != $groups);
  $groups->copy($g2);
  is($groups->group(0), "foo");
  ok($g2 == $groups);
}

sub test_split_private_group {
  my $name = ssrc::spread::split_private_group("#foo#bar");
  ok("foo" == $name->{first});
  ok("bar" == $name->{second});
}

test_add();
test_add_group_list();
test_copy();
#test_split_private_group();
