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

EXTRA_DIST = LICENSE NOTICE CHANGES doc/images/logoSmall.jpg doc/api \
	doc/index.h doc/spread-4.1.0-64-bit.patch config/dox.footer \
	config/dox.header config/libssrcspread.dox config/get-py-info.py

nobase_include_HEADERS := $(subst $(top_srcdir)/,,$(shell find $(top_srcdir)/ssrc '(' -name "*.h" -not -name libssrcspread-config.h -not -name config.h ')' -print)) ssrc/libssrcspread-config.h

check_HEADERS := $(subst $(top_srcdir)/,,$(shell find $(top_srcdir)/tests -name "*.h" -print))

SUBDIRS = ssrc swig tests

TEST_AM_CXXFLAGS = $(AM_CXXFLAGS) -Wno-non-virtual-dtor -Wno-overloaded-virtual -fprofile-arcs -ftest-coverage
TEST_CXXFLAGS := $(patsubst -O%,,$(CXXFLAGS))
TEST_CFLAGS := $(patsubst -O%,,$(CFLAGS))

LCOV_DIRS = ssrc tests

test:
	$(MAKE) all-recursive AM_CXXFLAGS='$(TEST_AM_CXXFLAGS)' CXXFLAGS='$(TEST_CXXFLAGS)' CFLAGS='$(TEST_CFLAGS)'
	find $(LCOV_DIRS) '(' -name "*.gcda*" -o -name AllTests.info ')' -exec rm -f {} +
	(cd tests/spread && $(MAKE) check AM_CXXFLAGS='$(TEST_AM_CXXFLAGS)' CXXFLAGS='$(TEST_CXXFLAGS)' CFLAGS='$(TEST_CFLAGS)')

coverage: test
	geninfo .
	find $(LCOV_DIRS) '(' -name "*.info" -a -not -name AllTests.info ')' \
		-exec \
		lcov -r {} "/usr/include/*" -r {} "$(SPREAD_DIR)/*" \
			-r {} "/net/*" -o {}.r ';'
	find $(LCOV_DIRS) -name "*.info.r" -exec \
		sh -c 'test=`basename {} .gcda.info.r`; perl -pi -e "s#^TN:#TN:$$test#" {}' ';'
	find $(LCOV_DIRS) -name "*.info.r" -print | sed 's/\(.*\)/ -a \1/' | \
		xargs lcov -o tests/AllTests.info
	genhtml -t "Ssrc C++/Lua/Perl/Python/Ruby Bindings for Spread $(VERSION) Unit Tests " \
		--show-details -o $(top_srcdir)/doc/tests tests/AllTests.info
	for file in $$(find $(top_srcdir)/doc/tests -name "*.html" -print) ; do \
		imgdir=$(top_srcdir)/doc/tests ; \
		imgdir="`echo $$imgdir | sed -e 's/\\//\\\\\\//g'`" ; \
		imgdir="`echo $$file | sed -e \"s/$$imgdir//\"`" ; \
		imgdir="`echo $$imgdir | sed -e 's#^\./##' -e 's#[^/]\+/#../#g'`" ; \
		imgdir="`dirname $${imgdir} | sed -e 's#^\.\?/##' -e 's#\.\.$$#../#'`" ; \
		perl -pi \
			-e "s/<title>LCOV - /<title>/;" \
			-e "s#<tr><td class=\"versionInfo\">.*?</td></tr>##;" \
			-e "s#<td class=\"title\">.*?</td>#<td class=\"title\">Ssrc C++ Binding for Spread $(VERSION) Unit Test Coverage</td>#;" "$$file" ; \
	done

package: apidocs dist-xz

if LIBSSRCSPREAD_DOXYGEN

$(top_srcdir)/doc/api/%.jpg: doc/images/%.jpg
	if [ ! -d $(top_srcdir)/doc/api ]; then \
		mkdir $(top_srcdir)/doc/api $(top_srcdir)/doc/api ; \
	fi; \
	cp $< $@

apidocs: $(top_srcdir)/doc/api/logoSmall.jpg
	(incdir="`pwd | sed -e 's/\\//\\\\\\//g'`" ; \
        cd $(top_srcdir); \
	sed -e "s/^\(INCLUDE_PATH.*=.*\)/\1 $${incdir}/" \
	    -e "s/^PROJECT_NUMBER.*=.*/PROJECT_NUMBER = $(VERSION)/" \
	    -e 's/^PROJECT_NAME.*=[^"]*\("[^"]*"\)/PROJECT_NAME = \1 $(VERSION)/' \
	    -e "s#^EXAMPLE_PATH.*=.*#EXAMPLE_PATH = $(abs_srcdir)/doc#" \
		config/libssrcspread.dox | $(DOXYGEN) -)
	find $(top_srcdir)/doc/api '(' -type f -name "*.html" ')' \
		-exec perl -pi -e \
		's/\b$(libssrcspread_namespace)/ssrc::spread/g' {} +
	find $(top_srcdir)/doc/api '(' -type f \
		-regex '.*\.\(md5\|map\|dot\)' ')' -exec rm -f {} +
	if [ -n "$(TIDY)" ]; then \
		find $(top_srcdir)/doc/api '(' -type f -name "*.html" ')' \
			-exec $(TIDY) -modify -quiet -wrap 0 {} + || true; \
	fi;
	cp $(top_srcdir)/doc/*.patch $(top_srcdir)/doc/api
endif