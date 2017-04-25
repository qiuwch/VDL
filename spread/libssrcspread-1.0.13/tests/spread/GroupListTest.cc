/* Copyright 2006,2011 Savarese Software Research Corporation
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

#define BOOST_TEST_MODULE GroupListTest
#include <boost/test/unit_test.hpp>

using namespace NS_SSRC_SPREAD; 
using namespace std::rel_ops;

class GroupListFixture {
public:
  GroupList *groups;

  GroupListFixture() {
    groups = new GroupList();
  }

  ~GroupListFixture() {
    delete groups;
    groups = 0;
  }
};

BOOST_FIXTURE_TEST_SUITE(all, GroupListFixture)

BOOST_AUTO_TEST_CASE(test_add) {
  BOOST_REQUIRE_EQUAL(groups->size(), 0u);
  groups->add("foo");
  BOOST_REQUIRE_EQUAL(groups->size(), 1u);
  BOOST_REQUIRE((*groups)[0] == "foo");
  groups->add("bar");
  BOOST_REQUIRE_EQUAL(groups->size(), 2u);
  BOOST_REQUIRE(groups->group(1) == "bar");
}

BOOST_AUTO_TEST_CASE(test_add_group_list) {
  groups->add("foo");
  groups->add("bar");

  GroupList g;

  g.add("foobar");
  g.add("blah");
  g.add("blargh");

  groups->add(g);

  BOOST_REQUIRE_EQUAL(groups->size(), 5u);
  BOOST_REQUIRE(groups->group(4) == "blargh" && groups->group(1) == "bar");

  BOOST_REQUIRE(g != *groups);

  groups->clear();
  groups->add(g);

  BOOST_REQUIRE(g == *groups);
}

BOOST_AUTO_TEST_CASE(test_split_private_group) {
  std::pair<string,string> name = split_private_group("#foo#bar");
  BOOST_REQUIRE("foo" == name.first);
  BOOST_REQUIRE("bar" == name.second);
}

BOOST_AUTO_TEST_SUITE_END()
