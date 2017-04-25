dnl Copyright 2006-2015 Savarese Software Research Corporation
dnl
dnl Licensed under the Apache License, Version 2.0 (the "License");
dnl you may not use this file except in compliance with the License.
dnl You may obtain a copy of the License at
dnl
dnl     http://www.savarese.com/software/ApacheLicense-2.0
dnl
dnl Unless required by applicable law or agreed to in writing, software
dnl distributed under the License is distributed on an "AS IS" BASIS,
dnl WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
dnl See the License for the specific language governing permissions and
dnl limitations under the License.

AC_INIT(libssrcspread, 1.0.13)
libssrcspread_lib_version=1.9.0
AC_SUBST(libssrcspread_lib_version)
AC_PREREQ(2.50)
AC_CONFIG_AUX_DIR(config)
AC_CANONICAL_HOST
AC_CANONICAL_SYSTEM
AC_COPYRIGHT([
Copyright 2006-2017 Savarese Software Research Corporation

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.savarese.com/software/ApacheLicense-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
])

AM_INIT_AUTOMAKE
AM_CONFIG_HEADER(config.h)

dnl
dnl Define custom functions
dnl

dnl
dnl Checks for programs.
dnl

AC_PROG_CXX
AM_CONDITIONAL(LIBSSRCSPREAD_USING_GCC, [test "$ac_cv_prog_gxx" = yes])

dnl
dnl Do not build shared libraries by default.  This is in order
dnl to speed up the build process; otherwise both shared and
dnl static libraries get built simultaneously, requiring two
dnl compiles for every .o.
dnl 

AC_DISABLE_SHARED
AC_PROG_LN_S

dnl
dnl Disable libtool fortran checks
dnl

F77=no

AC_PROG_LIBTOOL
AC_SUBST(LIBTOOL_DEPS)
AC_PROG_INSTALL()
AC_PROG_MAKE_SET

dnl
dnl Adds options
dnl

AC_ENABLE_DEBUG
AM_CONDITIONAL(LIBSSRCSPREAD_DEBUG, [test "$enable_debug" = yes])
AC_CHECK_PIC

AC_NAMESPACE_VERSIONING

AC_WITH_SPREAD_TOOLKIT
AM_CONDITIONAL(LIBSSRCSPREAD_SPREAD, [test "$with_spread"])
LDFLAGS_ORIG="${LDFLAGS}"
LDFLAGS="${LDFLAGS_ORIG} ${libssrcspread_with_spread_ldflags}"
AC_CHECK_FUNCS(SP_get_memb_info SP_kill)
LDFLAGS="${LDFLAGS_ORIG}"

AC_WITH_TEST_DAEMON

AC_WITH_BOOST_TEST
AM_CONDITIONAL(LIBSSRCSPREAD_BOOST_TEST, [test "$with_boost"])

AC_WITH_DOXYGEN
AM_CONDITIONAL(LIBSSRCSPREAD_DOXYGEN, [test "$with_doxygen"])

dnl
dnl Set default language for checks to C++
dnl

AC_LANG_CPLUSPLUS

if test "$ac_cv_prog_gcc" = yes; then
    CFLAGS="$CFLAGS -std=c99 -pipe -fno-gnu-keywords"
    CXXFLAGS="$CXXFLAGS -pipe -fno-gnu-keywords"
    AC_LIBTOOL_COMPILER_OPTION(
      [checking if compiler recognizes -fvisibility-inlines-hidden],
      [libssrcspread_cv_flag], [-fvisibility-inlines-hidden], ,
      [ CXXFLAGS="$CXXFLAGS -fvisibility-inlines-hidden" ])
fi

dnl
dnl Checks for typedefs, structures, and compiler characteristics.
dnl

AC_CXX_NAMESPACES
if test "$ac_cv_cxx_namespaces" = no; then
AC_MSG_ERROR([
    The source code can be compiled only with a C++ compiler that
    supports namespaces.  Your compiler does not support namespaces.
    Please try again with a compiler that supports namespaces, such
    as the latest version of GCC at http://gcc.gnu.org/

])
fi

dnl
dnl SWIG bindings 
dnl

dnl Add AM_CONDITIONALs for each so we can conditionally compile
dnl extensions based on availability of swig and the script language.
dnl make with-swig default be without

AC_PATH_PROG(PERL, perl, none)
AM_PATH_PYTHON(2.4,, :)
AC_PATH_PROG(RUBY, ruby, none)
AC_PATH_PROG(LUA, lua, none)

AC_ARG_ENABLE(perl-binding,
 AC_HELP_STRING([--disable-perl-binding],
                [disable compilation of the Perl binding [[default=no]]]),
 [ PERL="none"; ],
 [ enable_perl_binding="yes"; ])

AC_ARG_ENABLE(python-binding,
 AC_HELP_STRING([--disable-python-binding],
                [disable compilation of the Python binding [[default=no]]]),
 [ PYTHON="none"; ],
 [ enable_python_binding="yes"; ])

AC_ARG_ENABLE(ruby-binding,
 AC_HELP_STRING([--disable-ruby-binding],
                [disable compilation of the Ruby binding [[default=no]]]),
 [ RUBY="none"; ],
 [ enable_ruby_binding="yes"; ])

AC_ARG_ENABLE(lua-binding,
 AC_HELP_STRING([--disable-lua-binding],
                [disable compilation of the Lua binding [[default=no]]]),
 [ LUA="none"; ],
 [ enable_lua_binding="yes"; ])

AC_CHECK_SWIG
AM_CONDITIONAL(LIBSSRCSPREAD_PERL, [test "$SWIG_PL_INCLUDES"])
AM_CONDITIONAL(LIBSSRCSPREAD_PYTHON, [test "$SWIG_PY_COMPILE" != "none"])
AM_CONDITIONAL(LIBSSRCSPREAD_RUBY, [test "$SWIG_RB_COMPILE_FLAGS" != "none"])
AM_CONDITIONAL(LIBSSRCSPREAD_LUA, [test "$SWIG_LUA_INCLUDES"])
AM_CONDITIONAL(LIBSSRCSPREAD_SWIG, [test "$SWIG" != "none"])

AC_SO_EXTENSION

dnl For documentation generation

AC_CHECK_PROG([TIDY], [tidy5], [tidy5])
AC_CHECK_PROG([TIDY], [tidy], [tidy])

IF=if
ELSE=else
ENDIF=endif
AC_SUBST(IF)
AC_SUBST(ELSE)
AC_SUBST(ENDIF)

dnl
dnl Output commands and files
dnl 

libssrcspread_build="_v`echo $VERSION | sed -e 's/\./_/g'`"
if test "$enable_namespace_versioning" = no; then
  libssrcspread_namespace="ssrcspread"
else
  libssrcspread_namespace="ssrcspread${libssrcspread_build}"
fi
libssrcspread_swig_namespace="`echo ${libssrcspread_namespace} | sed -e 's/::/_/g'`"

AC_SUBST(libssrcspread_namespace)

AH_BOTTOM(
[
#if !defined(NS_SSRCSPREAD)
#  define NS_SSRCSPREAD $libssrcspread_namespace
#endif

#if !defined(SWIG_NS_SSRCSPREAD)
#  define SWIG_NS_SSRCSPREAD $libssrcspread_swig_namespace
#  define SWIG_NS_SSRCSPREAD_SYM(sym) $libssrcspread_swig_namespace ## sym
#endif

#if !defined(LIBSSRCSPREAD_DEFINE_NAMESPACE)
#  define LIBSSRCSPREAD_DEFINE_NAMESPACE(name) NS_SSRCSPREAD::name
#endif

#if !defined(NS_SSRCSPREAD_DECL_PREFIX)
#  define NS_SSRCSPREAD_DECL_PREFIX \
namespace $libssrcspread_namespace {
#endif

#if !defined(NS_SSRCSPREAD_DECL_SUFFIX)
#  define NS_SSRCSPREAD_DECL_SUFFIX \
}
#endif

#if !defined(LIBSSRCSPREAD_TEST_DAEMON)
#  define LIBSSRCSPREAD_TEST_DAEMON $libssrcspread_test_daemon
#endif

#if defined(LIBSSRCSPREAD_HAVE_SP_GET_MEMB_INFO)
#  define LIBSSRCSPREAD_ENABLE_MEMBERSHIP_INFO 1
#endif

#if defined(LIBSSRCSPREAD_HAVE_SP_KILL)
#  define LIBSSRCSPREAD_ENABLE_MAILBOX_KILL 1
#endif

#ifndef SSRC_DECL_THROW
#  ifdef SWIG
#    define SSRC_DECL_THROW(...) throw(__VA_ARGS__)
#  else
#    define SSRC_DECL_THROW(...)
#  endif
#endif
])

PACKAGEDIR=ssrc

MOVE_CONFIG_HEADER='
moveConfigHeader() {
  srcfile="$PACKAGE-config.h"
  if test -f "$srcfile"; then
    sed -e "s/\$libssrcspread_build/$libssrcspread_build/g" \
        -e "s/\$libssrcspread_namespace/$libssrcspread_namespace/g" \
        -e "s/\$libssrcspread_swig_namespace/$libssrcspread_swig_namespace/g" \
        -e "s/\$libssrcspread_test_daemon/$libssrcspread_test_daemon/g" \
        "$srcfile" > "$srcfile".sed
    destfile="$PACKAGEDIR/$srcfile"
    if diff -q "$srcfile".sed "$destfile" > /dev/null 2>&1; then
      echo "$srcfile and $destfile are the same."
      echo "Removing $srcfile."
      rm -f "$srcfile" "$srcfile".sed
    else
      echo "$srcfile and $destfile differ."
      echo "Overwriting $destfile with $srcfile."
      mv -f "$srcfile".sed "$destfile"
      rm -f "$srcfile"
    fi
  fi
}'

AC_CONFIG_COMMANDS([ moveConfigHeader ],
	[ eval "$MOVE_CONFIG_HEADER"; ],
	[ MOVE_CONFIG_HEADER='$MOVE_CONFIG_HEADER' ])

AC_CONFIG_FILES([
Makefile
ssrc/Makefile
ssrc/spread/Makefile
swig/Makefile
swig/lua/Makefile
swig/perl/Makefile
swig/python/Makefile
swig/ruby/Makefile
tests/Makefile
tests/spread/Makefile
tests/swig/Makefile
tests/swig/lua/Makefile
tests/swig/perl/Makefile
tests/swig/python/Makefile
tests/swig/ruby/Makefile
]
,
[
 eval "$MOVE_CONFIG_HEADER";
 moveConfigHeader
]
)

AC_OUTPUT

AC_CREATE_PREFIX_CONFIG_H

[
 #
 # Moves the config header to the source include directory.
 #

 eval "$MOVE_CONFIG_HEADER"; moveConfigHeader
]
