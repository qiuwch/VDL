## Copyright 2006,2011 Savarese Software Research Corporation
##
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
##
##     http://www.savarese.com/software/ApacheLicense-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
##

include $(top_srcdir)/config/global.mk

if LIBSSRCSPREAD_BOOST_TEST
if LIBSSRCSPREAD_SPREAD

AM_CPPFLAGS += $(ssrc_with_boost_cflags)
LDADD = $(top_builddir)/ssrc/libssrcspread.la \
	$(ssrc_with_boost_ldflags) \
	$(libssrcspread_with_spread_ldflags) \
	$(BOOST_DIR)/lib/libboost_unit_test_framework.a

TESTS = GroupListTest MessageTest MailboxTest
check_PROGRAMS = $(TESTS)

GroupListTest_SOURCES = GroupListTest.cc
MessageTest_SOURCES = MessageTest.cc
MailboxTest_SOURCES = MailboxTest.cc

endif
endif