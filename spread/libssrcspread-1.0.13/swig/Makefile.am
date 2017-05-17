## Copyright 2006-2008 Savarese Software Research Corporation
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

BUILT_SOURCES   =

if LIBSSRCSPREAD_SWIG

include swigsrc.mk

EXTRA_DIST = $(SWIG_ISRC)

SUBDIRS = . lua perl python ruby

if LIBSSRCSPREAD_LUA

LUA_DIR        = lua
LUA_SRC        = $(SWIG_ISRC:%.i=$(LUA_DIR)/%.cc)
LUA_SWIG_FLAGS = -lua $(SWIG_FLAGS) -outdir $(LUA_DIR)

SWIG_CLEAN += $(LUA_SRC) $(LUA_SRC:%.cc=%.h)
BUILT_SOURCES += $(LUA_SRC)

$(LUA_SRC): $(LUA_DIR)/%.cc: %.i
	$(SWIG) $(LUA_SWIG_FLAGS) -o $@ $<

endif

if LIBSSRCSPREAD_PERL

PERL_DIR        = perl
PERL_SRC        = $(SWIG_ISRC:%.i=$(PERL_DIR)/%.cc)
PERL_SWIG_FLAGS = -perl $(SWIG_FLAGS) -outdir $(PERL_DIR)

SWIG_CLEAN += $(PERL_SRC) $(PERL_SRC:%.cc=%.h) $(PERL_DIR)/spread.pm
BUILT_SOURCES += $(PERL_SRC)

$(PERL_SRC): $(PERL_DIR)/%.cc: %.i
	$(SWIG) $(PERL_SWIG_FLAGS) -o $@ $<

endif

if LIBSSRCSPREAD_PYTHON

PYTHON_DIR        = python
PYTHON_SRC        = $(SWIG_ISRC:%.i=$(PYTHON_DIR)/%.cc)
PYTHON_SWIG_FLAGS = -python $(SWIG_FLAGS) -outdir $(PYTHON_DIR)

SWIG_CLEAN += $(PYTHON_SRC) $(PYTHON_SRC:%.cc=%.h) $(PYTHON_DIR)/spread.py
BUILT_SOURCES += $(PYTHON_SRC)

$(PYTHON_SRC): $(PYTHON_DIR)/%.cc: %.i
	$(SWIG) $(PYTHON_SWIG_FLAGS) -o $@ $<

endif

if LIBSSRCSPREAD_RUBY

RUBY_DIR        = ruby
RUBY_SRC        = $(SWIG_ISRC:%.i=$(RUBY_DIR)/%.cc)
RUBY_SWIG_FLAGS = -ruby -prefix "ssrc::" $(SWIG_FLAGS) -outdir $(RUBY_DIR)

SWIG_CLEAN += $(RUBY_SRC) $(RUBY_SRC:%.cc=%.h)
BUILT_SOURCES += $(RUBY_SRC)

$(RUBY_SRC): $(RUBY_DIR)/%.cc: %.i
	$(SWIG) $(RUBY_SWIG_FLAGS) -o $@ $<

endif

endif