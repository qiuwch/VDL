## Copyright 2008 Savarese Software Research Corporation
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

EXTRA_DIST = spread.lua

if LIBSSRCSPREAD_LUA

_SWIG_LUA_SITE_ARCH_DIR := $(DESTDIR)$(SWIG_LUA_SITE_ARCH_DIR)

all-local: _spread.$(SO_EXTENSION) spread.lua

install-exec-local:
	$(INSTALL_PROGRAM) -d $(_SWIG_LUA_SITE_ARCH_DIR)/ssrc
	$(INSTALL_PROGRAM) _spread.$(SO_EXTENSION) $(_SWIG_LUA_SITE_ARCH_DIR)/_spread.$(SO_EXTENSION)
	$(INSTALL_PROGRAM) $(srcdir)/spread.lua $(_SWIG_LUA_SITE_ARCH_DIR)/ssrc/spread.lua

$(SWIG_OBJ): %.o: %.cc
	$(CXX) -fPIC $(SWIG_LUA_INCLUDES) $(CXXFLAGS) -o $@ -c $<

_spread.$(SO_EXTENSION): $(SWIG_OBJ)
	$(LIBTOOL) --tag=CXX --mode=link $(CXX) $(SO_FLAGS) \
	$(AM_CXXFLAGS) $(SWIG_LFLAGS) -o $@ $^
	if [ -f .libs/_spread.$(SO_EXTENSION) ]; then \
	  cp -f .libs/_spread.$(SO_EXTENSION) . ; \
	fi

endif