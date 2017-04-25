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

if LIBSSRCSPREAD_PYTHON

EXTRA_DIST = setup.py

ifneq ($(strip $(DESTDIR)),)
export SETUP_ROOT = --root=$(DESTDIR)
@ELSE@
export SETUP_ROOT =
@ENDIF@

all-local: _spread.so __init__.py

install-exec-local:
	$(srcdir)/setup.py install --prefix=$(PYTHON_PREFIX) $(SETUP_ROOT)

# We set CC and CXX as environment variables in case SWIG_PY_COMPILE
# and SWIG_PY_LINK use pycc, which may pick up /usr/ucb/cc on Solaris.
$(SWIG_OBJ): %.o: %.cc
	CC=$(CXX) CXX=$(CXX) $(SWIG_PY_COMPILE) $(CXXFLAGS) -o $@ -c $<

_spread.so: $(SWIG_OBJ)
	CC=$(CXX) CXX=$(CXX) $(LIBTOOL) --tag=CXX --mode=link $(SWIG_PY_LINK) \
	$(PY_SO_FLAGS) $(AM_CXXFLAGS) $(SWIG_LFLAGS) -o $@ $^
	if [ -f .libs/_spread.so ]; then \
	  cp -f .libs/_spread.so . ; \
	fi

__init__.py:
	touch $@

endif
