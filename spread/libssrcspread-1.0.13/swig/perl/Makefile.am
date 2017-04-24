## Copyright 2006 Savarese Software Research Corporation
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

include $(top_srcdir)/config/global.mk
include ../swigsrc.mk

if LIBSSRCSPREAD_PERL

_SWIG_PL_SITE_ARCH_DIR := $(DESTDIR)$(SWIG_PL_SITE_ARCH_DIR)

all-local: spread.$(SO_EXTENSION) spread.pm

install-exec-local:
	$(INSTALL_PROGRAM) -d $(_SWIG_PL_SITE_ARCH_DIR)/auto/ssrc
	$(INSTALL_PROGRAM) -d $(_SWIG_PL_SITE_ARCH_DIR)/ssrc
	$(INSTALL_PROGRAM) spread.$(SO_EXTENSION) $(_SWIG_PL_SITE_ARCH_DIR)/auto/ssrc/spread.$(SO_EXTENSION)
	$(INSTALL_PROGRAM) spread.pm $(_SWIG_PL_SITE_ARCH_DIR)/ssrc/spread.pm

$(SWIG_OBJ): %.o: %.cc
	$(CXX) -fPIC $(SWIG_PL_INCLUDES) $(CXXFLAGS) $(CPPFLAGS) -o $@ -c $<

spread.$(SO_EXTENSION): $(SWIG_OBJ)
	$(LIBTOOL) --tag=CXX --mode=link $(CXX) $(SO_FLAGS) \
	$(AM_CXXFLAGS) $(SWIG_LFLAGS) -o $@ $^
	if [ -f .libs/spread.$(SO_EXTENSION) ]; then \
	  cp -f .libs/spread.$(SO_EXTENSION) . ; \
	fi

endif