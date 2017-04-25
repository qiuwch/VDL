#!/usr/bin/env perl
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

use strict;
use Test::More qw(no_plan);
use ssrc::spread;

my $TestDaemon = $ENV{"LIBSSRCSPREAD_TEST_DAEMON"};
$TestDaemon =~ s/\"//g;

my $TestGroupName  = "MailboxTestGroup";
my $TestGroupName2 = "MailboxTestGroup2";

my $mbox;
my $rmbox;
my $message;

sub setUp() {
  $mbox  = new ssrc::spread::Mailbox($TestDaemon, "", 1,
                                     new ssrc::spread::Timeout(0));
  $rmbox = new ssrc::spread::Mailbox($TestDaemon);
  $message = new ssrc::spread::Message();
}

sub tearDown() {
  undef $mbox;
  undef $rmbox;
  undef $message;
}

sub join_() {
  $mbox->join($TestGroupName);
  $mbox->join($TestGroupName2);
}

sub send_ {
  my ($s, $g) = @_;
  $message->clear();
  $message->write($s);
  $mbox->send($message, $g);
}

sub leave() {
  $mbox->leave($TestGroupName);
  $mbox->leave($TestGroupName2);
}

sub test_join_and_leave {
  join_();
  leave();
}

sub test_send {
  join_();
  send_("test_send", $TestGroupName);
  send_("test_send2", $TestGroupName2);
  leave();
}

sub test_scatter_send {
  my $sm = new ssrc::spread::ScatterMessage();
  my $m  = new ssrc::spread::Message();

  join_();

  $message->write("test_scatter_send");
  $m->write("test_scatter_send2");

  ok($sm->add($message));
  ok($sm->add($m));
  $mbox->send($sm, $TestGroupName);

  $mbox->clear_groups();
  $mbox->add_group($TestGroupName);
  $mbox->clear_message_parts();

  # If you add a straight data message part, you must make sure
  # it does not get garbage-collected before the s.
  my $s1 = "test_scatter_send3";
  ok($mbox->add_message_part($s1));
  my $s2 = "test_scatter_send4";
  ok($mbox->add_message_part($s2));
  $mbox->send();

  leave();
}

sub test_group_send {
  my $groups = new ssrc::spread::GroupList();

  $groups->add($TestGroupName);
  $groups->add($TestGroupName2);

  join_();
  send_("test_group_send", $groups);
  send_("test_group_send2", $groups);
  leave();
}

sub test_scatter_group_send {
  my $groups = new ssrc::spread::GroupList();
  my $sm = new ssrc::spread::ScatterMessage();
  my $m = new ssrc::spread::Message();

  $groups->add($TestGroupName);
  $groups->add($TestGroupName2);

  join_();
  $message->write("test_scatter_group_send");
  $m->write("test_scatter_group_send2");
  $sm->add($message);
  $sm->add($m);
  $mbox->send($sm, $groups);
  leave();
}

sub test_receive_message {
  my $data = "foobar";
  my $groups = new ssrc::spread::GroupList();
  my $padding = new ssrc::spread::Message();

  $mbox->clear_groups();
  $mbox->clear_message_parts();
  $mbox->add_group($rmbox->private_group());
  $mbox->add_message_part($data);
  $mbox->send();

  $rmbox->clear_groups();
  $rmbox->clear_message_parts();
  $rmbox->add_message_part($message);
  $rmbox->add_message_part($padding);

  $padding->resize($padding->capacity());
  ok($padding->size() > 0);

  my $bytes = $rmbox->receive();
  $rmbox->copy_groups($groups);

  is($padding->size(), 0);
  is($bytes, length($data) + 1);
  is($message->size(), length($data) + 1);
  is($message->read(length($data) + 1), $data);
  is($groups->group(0), $rmbox->private_group());
  is($message->sender(), $mbox->private_group());
}

sub test_receive_membership_message {
# TODO: Port  this to Perl.
#  if not 'MembershipInfo' in dir(ssrc->spread):
#      return

  my $info = new ssrc::spread::MembershipInfo();

  join_();

  # mbox join() message
  my $groups = new ssrc::spread::GroupList();
  $mbox->receive($message, $groups);

  ok($message->is_membership());
  is($message->sender(), $TestGroupName);

  $message->get_membership_info($info);

  ok($info->caused_by_join());
  is($info->changed_member(), $mbox->private_group());

  my $mbox_group = new ssrc::spread::GroupList();
  my $local_members = new ssrc::spread::GroupList();
  my $all_members = new ssrc::spread::GroupList();

  $mbox_group->add($mbox->private_group());
  $info->get_local_members($local_members);
  $info->get_all_members($all_members);

  ok($mbox_group == $local_members);
  ok($mbox_group == $all_members);
  ok($groups == $all_members);

  # mbox join() message
  $mbox->receive($message);
  ok($message->is_membership());
  is($message->sender(), $TestGroupName2);

  # rmbox join() message
  $rmbox->join($TestGroupName2);

  $mbox->receive($message);
  ok($message->is_membership());
  is($message->sender(), $TestGroupName2);

  # rmbox leave() message
  $rmbox->leave($TestGroupName2);

  $mbox->receive($message);
  ok($message->is_membership());

  $message->get_membership_info($info);

  ok($info->caused_by_leave());
  is($message->sender(), $TestGroupName2);

  leave();
}

sub test_self_leave_message {
# TODO: Port  this to Perl.
#    if not 'MembershipInfo' in dir(ssrc->spread):
#      return
    
  $mbox->join($TestGroupName);
  $mbox->receive($message);
  $mbox->leave($TestGroupName);
  $mbox->receive($message);

  my $info = new ssrc::spread::MembershipInfo();

  $message->get_membership_info($info);

  ok($info->caused_by_leave());
  ok($info->is_self_leave());
}

sub test_error {
  eval { $mbox->join("####"); };
  is($@->error(), $ssrc::spread::Error::IllegalGroup);
}

sub run_test {
  my ($test) = @_;
  setUp();
  $test->();
  tearDown();
}

my @Tests =
    (
     \&test_join_and_leave,
     \&test_send,
     \&test_scatter_send,
     \&test_group_send,
     \&test_scatter_group_send,
     \&test_receive_message,
     \&test_receive_membership_message,
     \&test_self_leave_message,
     \&test_error
     );

foreach my $test (@Tests) {
  run_test($test);
}
