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

#include <cstdlib>
#include <algorithm>

#define BOOST_TEST_MODULE MessageTest
#include <boost/test/unit_test.hpp>

using namespace NS_SSRC_SPREAD; 

class MessageFixture {
public:
  Message *message;

  MessageFixture() {
    message = new Message();
  }

  ~MessageFixture() {
    delete message;
    message = 0;
  }
};

BOOST_FIXTURE_TEST_SUITE(all, MessageFixture)

BOOST_AUTO_TEST_CASE(test_set_self_discard) {
  BOOST_REQUIRE(!message->is_self_discard());
  message->set_self_discard();
  BOOST_REQUIRE(message->is_self_discard());
  message->set_self_discard(false);
  BOOST_REQUIRE(!message->is_self_discard());
}

BOOST_AUTO_TEST_CASE(test_service) {
  Message::service_type service = Message::ReliableSelfDiscard;
  message->set_service(service);
  BOOST_REQUIRE_EQUAL(message->service(), service);
}

BOOST_AUTO_TEST_CASE(test_write) {
  message->write("test_scatter_send", 17);
  BOOST_REQUIRE_EQUAL(std::memcmp("test_scatter_send",&(*message)[0],17), 0);
  BOOST_REQUIRE_EQUAL(message->size(), 17u);
  message->clear();
  message->write("test_scatter_send2", 18);
  BOOST_REQUIRE_EQUAL(message->size(), 18u);
  BOOST_REQUIRE_EQUAL(std::memcmp("test_scatter_send2",&(*message)[0],18), 0);
}

BOOST_AUTO_TEST_CASE(test_begin_end) {
  string str("this is a test");

  message->write(&str[0], str.size());

  BOOST_REQUIRE(std::equal(message->begin(), message->end(), str.begin()));
  BOOST_REQUIRE(std::equal(message->rbegin(), message->rend(),
                           str.rbegin()));

  Message const *cm = message;

  BOOST_REQUIRE(std::equal(cm->begin(), cm->end(), str.begin()));
  BOOST_REQUIRE(std::equal(cm->rbegin(), cm->rend(), str.rbegin()));
}

BOOST_AUTO_TEST_CASE(test_resize) {
  Message m(16);
  m.write("test_scatter_send2", 18);
  BOOST_REQUIRE_EQUAL(m.size(), 18u);
  BOOST_REQUIRE_EQUAL(std::memcmp("test_scatter_send2", &m[0], 18), 0);

  const unsigned int capacity = 1048576;
  Message m2(capacity);

  while(m2.offset() < capacity) {
    const int j = std::rand();
    m2.write(&j, sizeof(j));
  }

  // Test non-destructive resize.
  const unsigned int chunk_size = 131072;
  m.clear();

  BOOST_REQUIRE_EQUAL(m.offset(), 0u);

  m.write(&m2[0], chunk_size);

  BOOST_REQUIRE_EQUAL(m.offset(), chunk_size);

  m.resize(m2.size() / 2);
  BOOST_REQUIRE_EQUAL(m.size(), m2.size() / 2);
  BOOST_REQUIRE_EQUAL(m.capacity(), m2.size() / 2);

  for(unsigned int i = chunk_size; i < capacity; i+=chunk_size) {
    m.write(&m2[i], chunk_size);
  }

  BOOST_REQUIRE_EQUAL(m2.size(), capacity);
  BOOST_REQUIRE_EQUAL(m.size(), m2.size());
  BOOST_REQUIRE_EQUAL(std::memcmp(&m[0], &m2[0], capacity), 0);
}

BOOST_AUTO_TEST_SUITE_END()
