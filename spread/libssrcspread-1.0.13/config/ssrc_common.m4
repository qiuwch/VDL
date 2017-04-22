dnl -*- mode: autoconf; -*-

dnl AC_AS_DIRNAME(PATHNAME)

AC_DEFUN([AC_AS_DIRNAME],
[AC_AS_DIRNAME_EXPR([$1]) 2>/dev/null ||
AC_AS_DIRNAME_SED([$1])
])


AC_DEFUN([_AC_AS_EXPR_PREPARE],
[if expr a : '\(a\)' >/dev/null 2>&1; then
  as_expr=expr
else
  as_expr=false
fi
])# _AC_AS_EXPR_PREPARE


AC_DEFUN([AC_AS_DIRNAME_EXPR],
[AC_REQUIRE([_AC_AS_EXPR_PREPARE])dnl
$as_expr X[]$1 : 'X\(.*[[^/]]\)//*[[^/][^/]]*/*$' \| \
         X[]$1 : 'X\(//\)[[^/]]' \| \
         X[]$1 : 'X\(//\)$' \| \
         X[]$1 : 'X\(/\)' \| \
         .     : '\(.\)'])

AC_DEFUN([AC_AS_DIRNAME_SED],
[echo X[]$1 |
    sed ['/^X\(.*[^/]\)\/\/*[^/][^/]*\/*$/{ s//\1/; q; }
          /^X\(\/\/\)[^/].*/{ s//\1/; q; }
          /^X\(\/\/\)$/{ s//\1/; q; }
          /^X\(\/\).*/{ s//\1/; q; }
          s/.*/./; q']])

dnl AC_AS_MKDIR_P(PATH)

AC_DEFUN([AC_AS_MKDIR_P],[dnl
case $1 in
  \\*)   ac_incr_dir=\\;;
  ?:\\*) ac_incr_dir=\\;; # ouch
  /*)    ac_incr_dir=/;;
  ?:/*)  ac_incr_dir=/;; # ouch
  *)     ac_incr_dir=.;;
esac
as_dummy=$1
for as_mkdir_dir in `echo $ac_dummy | tr \\/ '  '`; do
  case $as_mkdir_dir in
    # Skip DOS drivespec
    ?:) as_incr_dir=$as_mkdir_dir ;;
    *)
      as_incr_dir=$as_incr_dir/$as_mkdir_dir
      test -d "$as_incr_dir" || mkdir "$as_incr_dir"
    ;;
  esac
done
])

dnl AC_CREATE_PREFIX_CONFIG_H

AC_DEFUN([AC_CREATE_PREFIX_CONFIG_H],
[changequote({, })dnl
ac_prefix_conf_OUT=`echo ifelse($1, , $PACKAGE-config.h, $1)`
ac_prefix_conf_DEF=`echo _$ac_prefix_conf_OUT | tr 'abcdefghijklmnopqrstuvwxyz./,\-' ABCDEFGHIJKLMNOPQRSTUVWXYZ____`
ac_prefix_conf_PKG=`echo ifelse($2, , $PACKAGE, $2)`
ac_prefix_conf_LOW=`echo _$ac_prefix_conf_PKG | tr 'ABCDEFGHIJKLMNOPQRSTUVWXYZ\-' abcdefghijklmnopqrstuvwxyz_`
ac_prefix_conf_UPP=`echo $ac_prefix_conf_PKG | tr 'abcdefghijklmnopqrstuvwxyz\-' ABCDEFGHIJKLMNOPQRSTUVWXYZ_`
ac_prefix_conf_UPP=`echo $ac_prefix_conf_UPP | sed -e '/^[0-9]/s/^/_/'`
ac_prefix_conf_INP=`echo ifelse($3, , _, $3)`
if test "$ac_prefix_conf_INP" = "_"; then
   case $ac_prefix_conf_OUT in
      */*) ac_prefix_conf_INP=`basename $ac_prefix_conf_OUT`
      ;;
      *-*) ac_prefix_conf_INP=`echo $ac_prefix_conf_OUT | sed -e 's/[a-zA-Z0-9_]*-//'`
      ;;
      *) ac_prefix_conf_INP=config.h
      ;;
   esac
fi
changequote([, ])dnl
if test -z "$ac_prefix_conf_PKG" ; then
   AC_MSG_ERROR([no prefix for _PREFIX_PKG_CONFIG_H])
else
  AC_MSG_RESULT(creating $ac_prefix_conf_OUT - prefix $ac_prefix_conf_UPP for $ac_prefix_conf_INP defines)
  if test -f $ac_prefix_conf_INP ; then
    AC_ECHO_MKFILE([/* automatically generated */], $ac_prefix_conf_OUT)
changequote({, })dnl
    echo '#ifndef '$ac_prefix_conf_DEF >>$ac_prefix_conf_OUT
    echo '#define '$ac_prefix_conf_DEF' 1' >>$ac_prefix_conf_OUT
    echo ' ' >>$ac_prefix_conf_OUT
    echo /'*' $ac_prefix_conf_OUT. Generated automatically at end of configure. '*'/ >>$ac_prefix_conf_OUT

    echo 's/#undef  *\([A-Z_]\)/#undef '$ac_prefix_conf_UPP'_\1/' >conftest.sed
    echo 's/#undef  *\([a-z]\)/#undef '$ac_prefix_conf_LOW'_\1/' >>conftest.sed
    echo 's/#define  *\([A-Z_][A-Za-z0-9_]*\)\(.*\)/#ifndef '$ac_prefix_conf_UPP"_\\1 \\" >>conftest.sed
    echo '#define '$ac_prefix_conf_UPP"_\\1 \\2 \\" >>conftest.sed
    echo '#endif/' >>conftest.sed
    echo 's/#define  *\([a-z][A-Za-z0-9_]*\)\(.*\)/#ifndef '$ac_prefix_conf_LOW"_\\1 \\" >>conftest.sed
    echo '#define '$ac_prefix_conf_LOW"_\\1 \\2 \\" >>conftest.sed
    echo '#endif/' >>conftest.sed
    sed -f conftest.sed $ac_prefix_conf_INP >>$ac_prefix_conf_OUT
    echo ' ' >>$ac_prefix_conf_OUT
    echo '/*' $ac_prefix_conf_DEF '*/' >>$ac_prefix_conf_OUT
    echo '#endif' >>$ac_prefix_conf_OUT
changequote([, ])dnl
  else
    AC_MSG_ERROR([input file $ac_prefix_conf_IN does not exist, dnl
    skip generating $ac_prefix_conf_OUT])
  fi
  rm -f conftest.*
fi])


dnl AC_ECHO_MKFILE(MSG,FILE)

AC_DEFUN([AC_ECHO_MKFILE],
[dnl
  case $2 in
    */*) P=` AC_AS_DIRNAME($2) ` ; AC_AS_MKDIR_P($P) ;;
  esac
  echo "$1" >$2
])

dnl AC_SO_EXTENSION
dnl
dnl Detect shared object extension

AC_DEFUN([AC_SO_EXTENSION],
[
  if test `uname` = "Darwin"; then
    SO_EXTENSION="dylib"
    RB_SO_EXTENSION="bundle"
    SO_FLAGS="-dynamiclib -undefined dynamic_lookup"
    PY_SO_FLAGS=""
    RB_SO_FLAGS=""
    LD_EXPORT_DYNAMIC=""
  else
    SO_EXTENSION="so"
    RB_SO_EXTENSION="so"
    SO_FLAGS="-fPIC -DPIC -XCClinker -shared"
    PY_SO_FLAGS="$SO_FLAGS"
    RB_SO_FLAGS="$SO_FLAGS"
    LD_EXPORT_DYNAMIC="-Wl,-E"
  fi
  AC_SUBST(SO_EXTENSION)
  AC_SUBST(RB_SO_EXTENSION)
  AC_SUBST(SO_FLAGS)
  AC_SUBST(PY_SO_FLAGS)
  AC_SUBST(RB_SO_FLAGS)
  AC_SUBST(LD_EXPORT_DYNAMIC)
])

dnl AC_CXX_NAMESPACES
dnl
dnl If the compiler can prevent name clashes using namespaces, define
dnl HAVE_NAMESPACES.

AC_DEFUN([AC_CXX_NAMESPACES],
[AC_CACHE_CHECK(whether the compiler implements namespaces,
ac_cv_cxx_namespaces,
[AC_LANG_PUSH(C++)
 AC_COMPILE_IFELSE([
    AC_LANG_PROGRAM([[namespace Outer { namespace Inner { int i = 0; }}]],
                    [[using namespace Outer::Inner; return i;]])],
 ac_cv_cxx_namespaces=yes, ac_cv_cxx_namespaces=no)
 AC_LANG_POP(C++)
])
if test "$ac_cv_cxx_namespaces" = yes; then
  AC_DEFINE(HAVE_NAMESPACES,1,[Define if the compiler implements namespaces.])
fi
])

dnl AC_TR1_TUPLE
AC_DEFUN([AC_TR1_TUPLE], [
  AC_CACHE_CHECK(for std::tr1::tuple_size,
  ac_cv_cxx_tr1_tuple,
  [ AC_TRY_COMPILE([#include <tuple>], [using std::tr1::tuple_size; using std::tr1::get;],
  ac_cv_cxx_tr1_tuple=yes, ac_cv_cxx_tr1_tuple=no)
  ])
  if test "$ac_cv_cxx_tr1_tuple" = yes; then
    AC_DEFINE(HAVE_TR1_TUPLE,1,[Define if std::tr1::tuple_size is present. ])
  fi
])

dnl AC_STD_TUPLE
AC_DEFUN([AC_STD_TUPLE], [
  AC_CACHE_CHECK(for std::tuple_size,
  ac_cv_cxx_std_tuple,
  [ AC_TRY_COMPILE([#include <tuple>], [using std::tuple_size; using std::get;],
  ac_cv_cxx_std_tuple=yes, ac_cv_cxx_std_tuple=no)
  ])
  if test "$ac_cv_cxx_std_tuple" = yes; then
    AC_DEFINE(HAVE_STD_TUPLE,1,[Define if std::tuple_size is present. ])
  fi
])

dnl AC_CXX_UNIQUE_PTR
dnl
dnl If the compiler has unique_ptr, define HAVE_UNIQUE_PTR.

AC_DEFUN([AC_CXX_UNIQUE_PTR],
[AC_CACHE_CHECK([whether the compiler library contains std::unique_ptr],
ac_cv_cxx_unique_ptr,
[AC_LANG_PUSH(C++)
 AC_COMPILE_IFELSE([
    AC_LANG_PROGRAM([[#include <memory>
                      typedef std::unique_ptr<int> int_ptr;]],
                    [[int_ptr p(new int(3)); return *p;]])],
 ac_cv_cxx_unique_ptr=yes, ac_cv_cxx_unique_ptr=no)
 AC_LANG_POP(C++)
])
if test "$ac_cv_cxx_unique_ptr" = yes; then
  AC_DEFINE(HAVE_UNIQUE_PTR,1,
            [Define if the compiler library contains std::unique_ptr.])
fi
])

dnl AC_CXX_DELETED_FUNCTIONS
dnl
dnl If the compiler supports defaulted and deleted functions,
dnl define HAVE_DELETED_FUNCTIONS.

AC_DEFUN([AC_CXX_DELETED_FUNCTIONS],
[AC_CACHE_CHECK([whether the compiler supports defaulted and deleted functions],
ac_cv_cxx_deleted_functions,
[AC_LANG_PUSH(C++)
 AC_COMPILE_IFELSE([
    AC_LANG_PROGRAM([[
struct Foo {
  int i;

  explicit Foo(const int i) : i(i) { }
  Foo() = default;
  Foo(const Foo &) = delete;
  Foo & operator=(const Foo &) = delete;
};]],
                    [[Foo foo(0); return foo.i;]])],
 ac_cv_cxx_deleted_functions=yes, ac_cv_cxx_deleted_functions=no)
 AC_LANG_POP(C++)
])
if test "$ac_cv_cxx_deleted_functions" = yes; then
  AC_DEFINE(HAVE_DELETED_FUNCTIONS,1,
            [Define if the compiler supports defaulted and deleted functions.])
fi
])

dnl AC_CXX_EXTENDED_FRIEND_DECLARATIONS
dnl
dnl If the compiler supports extended friend declarations.

AC_DEFUN([AC_CXX_EXTENDED_FRIEND_DECLARATIONS],
[AC_CACHE_CHECK([whether the compiler supports extended friend declarations],
ac_cv_cxx_extended_friend_declarations,
[AC_LANG_PUSH(C++)
 AC_COMPILE_IFELSE([
    AC_LANG_PROGRAM([[
class A {
  int foo;
};
struct C {
  typedef A B;
  int bar;
};
template<typename T>
class D {
  //friend class T::B;
  friend T::B;
  int baz;
};]],
                    [[typedef D<C> E; E e;]])],
                    ac_cv_cxx_extended_friend_declarations=yes,
                    ac_cv_cxx_extended_friend_declarations=no)
 AC_LANG_POP(C++)
])
if test "$ac_cv_cxx_extended_friend_declarations" = yes; then
  AC_DEFINE(HAVE_EXTENDED_FRIEND_DECLARATIONS,1,
            [Define if the compiler supports extended friend declarations.])
fi
])

dnl AC_CHECK_PIC
dnl
dnl If the system is 64-bit, add -fPIC -DPIC to CFLAGS and CXXFLAGS.
dnl Note, this is not an exact method for checking the requirement.
dnl It's an initial hack to tide us over until we can write a test
dnl that tries to link with non-PIC code and PIC code.

AC_DEFUN([AC_CHECK_PIC],
[_isainfo_test=""
if test -x /bin/isainfo; then
   _isainfo_test="-o `/bin/isainfo -b` = 64"
fi
if test "`getconf ULONG_MAX`" != "`getconf UINT_MAX`" -o "`uname -m`" = x86_64 -o "`uname -m`" = amd64 $_isainfo_test; then
    CFLAGS="$CFLAGS -fPIC -DPIC"
    CXXFLAGS="$CXXFLAGS -fPIC -DPIC"
 fi
])

dnl AC_WITH_DOXYGEN
dnl
dnl Specify or autodetect doxygen.

AC_DEFUN([AC_WITH_DOXYGEN],
[AC_ARG_WITH(doxygen,
 AS_HELP_STRING([--with-doxygen=PATHNAME],
          [specify the pathname of the doxygen command.  If not
           specified and doxygen is not auto-detected, API
           documentation will not be generated.]), [ ],
 [AC_CHECK_PROGS([with_doxygen], [doxygen], [""])])

command="`which ${with_doxygen}`"
if test "${with_doxygen}" -a -x "${command}"; then
   AC_MSG_NOTICE([found doxygen at: ${command}])
   DOXYGEN="${with_doxygen}"
   AC_SUBST(DOXYGEN)
else
   AC_MSG_WARN([doxygen not found.  Generation of API documentation
                will be disabled.])
fi
])

dnl AC_WITH_CPPUNIT
dnl
dnl Add cppunit related options and autodetect if necessary.

AC_DEFUN([AC_WITH_CPPUNIT],
[AC_ARG_WITH(cppunit-config,
 AS_HELP_STRING([--with-cppunit-config=PATHNAME],
          [specify the pathname of the cppunit cppunit-config command.
           If not specified and cppunit-config is not auto-detected,
           unit tests are disabled.]), [ ],
 [AC_CHECK_PROGS([with_cppunit_config], [cppunit-config], [""])])

command="`which ${with_cppunit_config}`"
if test "${with_cppunit_config}" -a -x "${command}"; then
   AC_MSG_NOTICE([found cppunit-config at: ${command}])
   ssrc_with_cppunit_cflags="`${with_cppunit_config} --cflags`"
   ssrc_with_cppunit_ldflags="`${with_cppunit_config} --libs`"
   AC_SUBST(ssrc_with_cppunit_cflags)
   AC_SUBST(ssrc_with_cppunit_ldflags)
   AC_MSG_NOTICE([added to test cflags: ${ssrc_with_cppunit_cflags}])
   AC_MSG_NOTICE([added to test ldflags: ${ssrc_with_cppunit_ldflags}])
   AC_MSG_NOTICE([enabled unit tests.])
   CPPUNIT_CONFIG="${with_cppunit_config}"
   AC_SUBST(CPPUNIT_CONFIG)
else
   AC_MSG_WARN([cppunit not found.  Unit tests will be disabled.])
fi
])
dnl AC_WITH_BOOST_TEST
dnl
dnl Add Boost related options and autodetect if necessary.
dnl TODO: make separate checks for Boost.Test and Boost.Iterator.  Define
dnl HAVE_BOOST_TEST and HAVE_BOOST_ITERATOR instead of HAVE_BOOST.

AC_DEFUN([AC_WITH_BOOST_TEST],
[AC_ARG_WITH(boost,
 AS_HELP_STRING([--with-boost=PATHNAME],
          [specify the root installation path for the Boost C++ libraries.]))

CFLAGS_ORIG="${CFLAGS}"
CPPFLAGS_ORIG="${CPPFLAGS}"
CXXFLAGS_ORIG="${CXXFLAGS}"
LDFLAGS_ORIG="${LDFLAGS}"
LIBS_ORIG="${LIBS}"

if test -n "${with_boost}"; then
   CFLAGS="${CFLAGS_ORIG} -I${with_boost}/include"
   CPPFLAGS="${CPPFLAGS_ORIG} -I${with_boost}/include"
   CXXFLAGS="${CXXFLAGS_ORIG} -I${with_boost}/include"
   LDFLAGS="${LDFLAGS_ORIG} -L${with_boost}/lib"
   LIBS="${LIBS_ORIG} -lboost_unit_test_framework"
fi

AC_LANG_PUSH(C++)
AC_LINK_IFELSE([
  AC_LANG_PROGRAM([[
#include <boost/test/unit_test.hpp>]],
[[
  BOOST_CHECK(true);
]])], [if test -z "${with_boost}"; then with_boost=" "; fi], [with_boost=""])
AC_LANG_POP(C++)

if test "$with_boost"; then
   AC_DEFINE(HAVE_BOOST, 1, [Boost is available.])
fi

CFLAGS="${CFLAGS_ORIG}"
CPPFLAGS="${CPPFLAGS_ORIG}"
CXXFLAGS="${CXXFLAGS_ORIG}"
LDFLAGS="${LDFLAGS_ORIG}"
LIBS="${LIBS_ORIG}"

if test "$with_boost" = " "; then
   AC_MSG_NOTICE([found Boost default system location.])
elif test "${with_boost}"; then
   AC_MSG_NOTICE([found Boost at: ${with_boost}])
   BOOST_DIR="${with_boost}"
   ssrc_with_boost_cflags="-I${with_boost}/include"
   ssrc_with_boost_ldflags="-L${with_boost}/lib"
   AC_SUBST(BOOST_DIR)
   AC_SUBST(ssrc_with_boost_cflags)
   AC_SUBST(ssrc_with_boost_ldflags)
else
   AC_MSG_WARN([boost test not found.  Unit tests will be disabled.])
fi
])

dnl AC_ENABLE_DEBUG
dnl
dnl Adds debug flags to CFLAGS and CXXFLAGS and define DEBUG preprocessor macro.

AC_DEFUN([AC_ENABLE_DEBUG],
[AC_ARG_ENABLE(debug,
 AC_HELP_STRING([--enable-debug],
                [enable compilation with debug flags [default=no]]),
 [ ],
 [ enable_debug=no; CFLAGS=`echo "$CFLAGS" | sed -e 's/-g//g'`;
   CXXFLAGS=`echo "$CXXFLAGS" | sed -e 's/-g//g'`; ])
if test "$enable_debug" = yes; then
   AC_DEFINE(DEBUG, 1, [ Enable debug code. ])
   CFLAGS="-g $CFLAGS"
   CXXFLAGS="-g $CXXFLAGS"
fi
])

dnl AC_NAMESPACE_VERSIONING
dnl
dnl Sets enable_namespace_versioning to yes if not disabled.

AC_DEFUN([AC_NAMESPACE_VERSIONING],
[AC_ARG_ENABLE(namespace-versioning,
 AC_HELP_STRING([--disable-namespace-versioning],
                [disable the appending of a version string to the top-level namespace [[default=no]]]),
 [ ],
 [ enable_namespace_versioning=yes; ])
])
