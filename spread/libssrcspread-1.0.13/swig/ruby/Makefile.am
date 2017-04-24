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

if LIBSSRCSPREAD_RUBY

_SWIG_RB_SITE_ARCH_DIR := $(DESTDIR)$(SWIG_RB_SITE_ARCH_DIR)

all-local: spread.$(RB_SO_EXTENSION)

install-exec-local:
	$(INSTALL_PROGRAM) -d $(_SWIG_RB_SITE_ARCH_DIR)/ssrc
	$(INSTALL_PROGRAM) spread.$(RB_SO_EXTENSION) $(_SWIG_RB_SITE_ARCH_DIR)/ssrc/spread.$(RB_SO_EXTENSION)

$(SWIG_OBJ): %.o: %.cc
	$(CXX) $(SWIG_RB_COMPILE_FLAGS) $(CXXFLAGS) -o $@ -c $<

spread.$(RB_SO_EXTENSION): $(SWIG_OBJ)
	$(LIBTOOL) --tag=CXX --mode=link $(CXX) $(SWIG_RB_LINK) \
	$(RB_SO_FLAGS) $(AM_CXXFLAGS) $(SWIG_LFLAGS) -o $@ $^
	if [ -f .libs/spread.$(RB_SO_EXTENSION) ]; then \
	  cp -f .libs/spread.$(RB_SO_EXTENSION) . ; \
	fi;

endif