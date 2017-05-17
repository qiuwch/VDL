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

AM_CPPFLAGS = -I$(top_srcdir)
AM_LDFLAGS  =

#
# Ensure swig tests run with shared library we just built.
#
ld_library_path        := $(LD_LIBRARY_PATH)
export LD_LIBRARY_PATH = $(top_builddir)/ssrc/.libs:$(SPREAD_DIR)/lib:$(ld_library_path)

ifeq ($(SO_EXTENSION),dylib)
export DYLD_LIBRARY_PATH = $(LD_LIBRARY_PATH)
@ENDIF@

if LIBSSRCSPREAD_USING_GCC
#LIBSSRCSPREAD_CXX_FLAGS    = -fexternal-templates -fno-gnu-keywords
#LIBSSRCSPREAD_CXX_FLAGS    = -std="c++98" -pipe -fno-gnu-keywords
LIBSSRCSPREAD_CXX_FLAGS    = -pthread -D_REENTRANT
#
# Remove -Woverloaded-virtual if virtual methods that get hidden,
# as can happen in template specializations, aren't a concern.
#
LIBSSRCSPREAD_CXX_WARNINGS = -pedantic -Wall -Wno-long-long -Winline \
	 -Woverloaded-virtual -Wold-style-cast -Wsign-promo
LIBSSRCSPREAD_DEBUG_FLAGS  = -g -DLIBSSRCSPREAD_DEBUG
else
LIBSSRCSPREAD_DEBUG_FLAGS  = -DLIBSSRCSPREAD_DEBUG
endif

if LIBSSRCSPREAD_DEBUG
AM_CXXFLAGS = $(LIBSSRCSPREAD_CXX_FLAGS) $(LIBSSRCSPREAD_CXX_WARNINGS) $(LIBSSRCSPREAD_DEBUG_FLAGS)
else
AM_CXXFLAGS = $(LIBSSRCSPREAD_CXX_FLAGS) $(LIBSSRCSPREAD_CXX_WARNINGS)
endif

LIBSSRCSPREAD_LFLAGS = -L$(top_builddir)/ssrc -lssrcspread

if LIBSSRCSPREAD_SWIG

SWIG_INCLUDES = -I$(top_srcdir) -I$(top_builddir) $(patsubst -U%,,$(CPPFLAGS))
SWIG_FLAGS = -Wall -small -c++ -templatereduce -O $(SWIG_INCLUDES)
SWIG_LFLAGS = $(LIBSSRCSPREAD_LFLAGS) $(libssrcspread_with_spread_ldflags) $(LDFLAGS)

endif