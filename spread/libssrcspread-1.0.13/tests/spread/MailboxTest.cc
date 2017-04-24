/* Copyright 2006,2007,2011 Savarese Software Research Corporation
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.savarese.com/software/ApacheLicense-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include <ssrc/spread.h> 

#include <utility>
#include <cstdlib>

#define BOOST_TEST_MODULE MailboxTest
#include <boost/test/unit_test.hpp>

using namespace NS_SSRC_SPREAD; 
using namespace std::rel_ops;

const char *TestGroupName = "MailboxTestGroup";
const char *TestGroupName2 = "MailboxTestGroup2";

class MailboxFixture {
public:
  Mailbox *mbox;
  Mailbox *rmbox;
  Message *message;

  MailboxFixture() {
    try {
      mbox  = new Mailbox(LIBSSRCSPREAD_TEST_DAEMON);
      rmbox = new Mailbox(LIBSSRCSPREAD_TEST_DAEMON, "", false);
    } catch(const Error & e) {
      e.print();
      throw e;
    }
    message = new Message();
  }

  ~MailboxFixture() {
    delete mbox;
    delete rmbox;
    delete message;
    mbox = 0;
    message = 0;
  }

  void join() {
    mbox->join(TestGroupName);
    mbox->join(TestGroupName2);
  }

  void leave() {
    mbox->leave(TestGroupName);
    mbox->leave(TestGroupName2);
  }
};

BOOST_FIXTURE_TEST_SUITE(all, MailboxFixture)

BOOST_AUTO_TEST_CASE(test_join_and_leave) {
  BOOST_REQUIRE_NO_THROW(this->join());
  BOOST_REQUIRE_NO_THROW(this->leave());
}

BOOST_AUTO_TEST_CASE(test_send) {
  this->join();
  message->write("test_send", 9);
  BOOST_REQUIRE_NO_THROW(mbox->send(*message, TestGroupName));
  message->clear();
  message->write("test_send2", 10);
  BOOST_REQUIRE_NO_THROW(mbox->send(*message, TestGroupName));
  this->leave();
}

BOOST_AUTO_TEST_CASE(test_scatter_send) {
  ScatterMessage sm;
  Message m;

  this->join();
  message->write("test_scatter_send", 17);
  m.write("test_scatter_send2", 18);
  BOOST_REQUIRE(sm.add(*message));
  BOOST_REQUIRE(sm.add(m));
  BOOST_REQUIRE_NO_THROW(mbox->send(sm, TestGroupName));

  mbox->clear_groups();
  mbox->add_group(TestGroupName);
  mbox->clear_message_parts();
  BOOST_REQUIRE(mbox->add_message_part("test_scatter_send3", 18));
  BOOST_REQUIRE(mbox->add_message_part("test_scatter_send4", 18));
  BOOST_REQUIRE_NO_THROW(mbox->send());
  this->leave();
}

BOOST_AUTO_TEST_CASE(test_group_send) {
  GroupList groups;

  groups.add(TestGroupName);
  groups.add(TestGroupName2);

  this->join();
  message->write("test_group_send", 15);
  BOOST_REQUIRE_NO_THROW(mbox->send(*message, groups));
  message->clear();
  message->write("test_group_send2", 16);
  BOOST_REQUIRE_NO_THROW(mbox->send(*message, groups));
  this->leave();
}

BOOST_AUTO_TEST_CASE(test_scatter_group_send) {
  GroupList groups;
  ScatterMessage sm;
  Message m;

  groups.add(TestGroupName);
  groups.add(TestGroupName2);

  this->join();
  message->write("test_scatter_group_send", 23);
  m.write("test_scatter_group_send2", 24);
  sm.add(*message);
  sm.add(m);
  BOOST_REQUIRE_NO_THROW(mbox->send(sm, groups));
  this->leave();
}

BOOST_AUTO_TEST_CASE(test_receive_message) {
  const char *data = "foobar";
  unsigned int data_len = strlen(data) + 1;
  unsigned int bytes;
  GroupList groups;
  Message padding;

  mbox->clear_groups();
  mbox->clear_message_parts();
  mbox->add_group(rmbox->private_group());
  mbox->add_message_part(data, data_len);
  mbox->send();

  rmbox->clear_groups();
  rmbox->clear_message_parts();
  rmbox->add_message_part(*message);
  rmbox->add_message_part(padding);

  padding.resize(padding.capacity());
  BOOST_REQUIRE(padding.size() > 0);

  bytes = rmbox->receive();
  rmbox->copy_groups(groups);

  BOOST_REQUIRE_EQUAL(padding.size(), 0u);
  BOOST_REQUIRE_EQUAL(bytes, data_len);
  BOOST_REQUIRE_EQUAL(message->size(), data_len);
  BOOST_REQUIRE_EQUAL(std::memcmp(data, &((*message)[0]), data_len), 0);
  BOOST_REQUIRE(rmbox->private_group() == groups[0]);
  BOOST_REQUIRE(mbox->private_group() == message->sender());
}

BOOST_AUTO_TEST_CASE(test_receive_message_buffer_too_short) {
  const unsigned int capacity = 131072;
  Message short_buffer(0);

  message->resize(capacity);

  for(unsigned int i = 0; i < capacity; i+=sizeof(int)) {
    const int j = std::rand();
    message->write(&j, sizeof(j));
  }

  mbox->clear_message_parts();
  mbox->add_message_part(*message);
  BOOST_REQUIRE_NO_THROW(mbox->send(rmbox->private_group()));

  BOOST_REQUIRE_EQUAL(short_buffer.size(), 0u);

  const unsigned int bytes = rmbox->receive(short_buffer);

  BOOST_REQUIRE_EQUAL(bytes, capacity);
  BOOST_REQUIRE_EQUAL(short_buffer.size(), capacity);
  BOOST_REQUIRE_EQUAL(std::memcmp(&((*message)[0]), &short_buffer[0],
                                  capacity), 0);
  BOOST_REQUIRE(rmbox->private_group() == rmbox->group(0));
  BOOST_REQUIRE(mbox->private_group() == short_buffer.sender());
}

BOOST_AUTO_TEST_CASE(test_receive_membership_message) {
  this->join();

  // mbox join message
  GroupList groups;
  mbox->receive(*message, groups);

  BOOST_REQUIRE(message->is_membership());
  BOOST_REQUIRE(TestGroupName == message->sender());

#ifdef LIBSSRCSPREAD_ENABLE_MEMBERSHIP_INFO
  MembershipInfo info;

  message->get_membership_info(info);

  BOOST_REQUIRE(info.is_regular_membership());
  BOOST_REQUIRE(info.caused_by_join());
  BOOST_REQUIRE(mbox->private_group() == info.changed_member());

  GroupList mbox_group, local_members, non_local_members, all_members;

  mbox_group.add(mbox->private_group());
  info.get_local_members(local_members);
  info.get_non_local_members(non_local_members);
  info.get_all_members(all_members);

  BOOST_REQUIRE(mbox_group == local_members);
  BOOST_REQUIRE(mbox_group != non_local_members);
  BOOST_REQUIRE_EQUAL(non_local_members.size(), 0u);
  BOOST_REQUIRE(mbox_group == all_members);
  BOOST_REQUIRE(groups == all_members);
#endif

  // mbox join message
  mbox->receive(*message);
  BOOST_REQUIRE(message->is_membership());
  BOOST_REQUIRE(TestGroupName2 == message->sender());

  // rmbox join message
  rmbox->join(TestGroupName2);

  mbox->receive(*message);
  BOOST_REQUIRE(message->is_membership());
  BOOST_REQUIRE(TestGroupName2 == message->sender());

  // rmbox leave message
  rmbox->leave(TestGroupName2);

  mbox->receive(*message);
  BOOST_REQUIRE(message->is_membership());

#ifdef LIBSSRCSPREAD_ENABLE_MEMBERSHIP_INFO
  message->get_membership_info(info);

  BOOST_REQUIRE(info.caused_by_leave());
#endif

  BOOST_REQUIRE(TestGroupName2 == message->sender());

  this->leave();
}

BOOST_AUTO_TEST_CASE(test_self_leave_message) {
#ifdef LIBSSRCSPREAD_ENABLE_MEMBERSHIP_INFO
  mbox->join(TestGroupName);
  mbox->receive(*message);
  mbox->leave(TestGroupName);
  mbox->receive(*message);

  MembershipInfo info;

  message->get_membership_info(info);

  BOOST_REQUIRE(info.caused_by_leave());
  BOOST_REQUIRE(info.is_self_leave());
#endif
}

BOOST_AUTO_TEST_SUITE_END()
