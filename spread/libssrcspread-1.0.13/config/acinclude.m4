dnl AC_WITH_SPREAD_TOOLKIT
dnl
dnl Add spread related options and autodetect if necessary.

AC_DEFUN([AC_WITH_SPREAD_TOOLKIT],
[AC_ARG_WITH(spread,
 AS_HELP_STRING([--with-spread=PATHNAME],
          [specify the root installation path for the Spread toolkit.
           If not specified and sp.h and libspread-core are not not
           auto-detected, the building of the spread package is
           disabled.]))

CFLAGS_ORIG="${CFLAGS}"
CPPFLAGS_ORIG="${CPPFLAGS}"
CXXFLAGS_ORIG="${CXXFLAGS}"
LDFLAGS_ORIG="${LDFLAGS}"

if test -n "${with_spread}"; then
   CFLAGS="${CFLAGS_ORIG} -I${with_spread}/include"
   CPPFLAGS="${CPPFLAGS_ORIG} -I${with_spread}/include"
   CXXFLAGS="${CXXFLAGS_ORIG} -I${with_spread}/include"
   LDFLAGS3="${LDFLAGS_ORIG} -L${with_spread}/lib -ltspread"
   LDFLAGS4="${LDFLAGS_ORIG} -L${with_spread}/lib -ltspread-core"
else
   LDFLAGS3="${LDFLAGS_ORIG} -ltspread"
   LDFLAGS4="${LDFLAGS_ORIG} -ltspread-core"
fi

for LDFLAGS in "${LDFLAGS4}" "${LDFLAGS3}"; do

AC_LANG_PUSH(C++)

AC_LINK_IFELSE([
  AC_LANG_PROGRAM(
[[
#include <cstdio>
#include <sp.h>
]],
[[
  int major = 0, minor, patch;
  SP_version(&major, &minor, &patch);
  std::printf("%d.%d.%d\n", major, minor, patch);
]])],[spread_compiled=1],[spread_compiled=0])

if test "$spread_compiled" -eq 1; then
   if test "$LDFLAGS" = "$LDFLAGS4"; then
      spread_version=4
   else	
      spread_version=3
   fi
   break;
fi

AC_LANG_POP(C++)

done

if test "$spread_compiled" -eq 1; then
   if test -z "${with_spread}"; then with_spread=" "; fi;

   AC_DEFINE(SPREAD_MAJOR_VERSION, [(SPREAD_VERSION >> 24)],
             [Spread major version.])
else
   with_spread=""
   CFLAGS="${CFLAGS_ORIG}"
   CPPFLAGS="${CPPFLAGS_ORIG}"
   CXXFLAGS="${CXXFLAGS_ORIG}"
fi

LDFLAGS="${LDFLAGS_ORIG}"

if test "$with_spread" = " "; then
   AC_MSG_NOTICE([found spread at default system location.])
   if test "$spread_version" -gt 3; then
      libssrcspread_with_spread_ldflags="-ltspread-core"
   else
      libssrcspread_with_spread_ldflags="-ltspread"
   fi
elif test -n "${with_spread}"; then
   AC_MSG_NOTICE([found spread at: ${with_spread}])
   SPREAD_DIR="${with_spread}"
   libssrcspread_with_spread_cflags="-I${with_spread}/include"
   if test "$spread_version" -gt 3; then
      libssrcspread_with_spread_ldflags="-L${with_spread}/lib -ltspread-core"
   else
      libssrcspread_with_spread_ldflags="-L${with_spread}/lib -ltspread"
   fi
   AC_SUBST(SPREAD_DIR)
   AC_SUBST(libssrcspread_with_spread_cflags)
   AC_MSG_NOTICE([added to spread cflags: ${libssrcspread_with_spread_cflags}])
else
   AC_MSG_ERROR([a usable spread version could not be found.  spread package cannot be compiled.])
fi

AC_SUBST(libssrcspread_with_spread_ldflags)
AC_MSG_NOTICE([added to spread ldflags: ${libssrcspread_with_spread_ldflags}])
AC_MSG_NOTICE([enabled spread package.])

])


dnl
dnl AC_WITH_TEST_DAEMON
dnl
dnl Specify the name of the Spread daemon to use for unit tests.
dnl

AC_DEFUN([AC_WITH_TEST_DAEMON],
[AC_ARG_WITH(test-daemon,
 AS_HELP_STRING([--with-test-daemon=SPREADNAME],
          [specify the name of the Spread daemon to use with the unit
           tests.  If not specified, the default port is used.]))

if test -n "${with_test_daemon}"; then
  libssrcspread_test_daemon="\"${with_test_daemon}\""
else
  libssrcspread_test_daemon="\"4803\""
fi
AC_SUBST(libssrcspread_test_daemon)
])

dnl
dnl AC_CHECK_SWIG
dnl
dnl SWIG bindings
dnl

AC_DEFUN([AC_CHECK_SWIG],
[
  AC_ARG_WITH(swig,
              AC_HELP_STRING([--with-swig=PATH],
                             [Try to use 'PATH/bin/swig' to build the
                              swig bindings.  If PATH is not specified,
                              look for a 'swig' binary in your PATH.]),
  [
      if test "$withval" = "no"; then
        SWIG_SUITABLE=no
      elif test "$withval" = "yes"; then
	withval=check
      fi
      AC_DO_CHECK_SWIG(["$withval"])
  ],
 [ AC_DO_CHECK_SWIG([check]) ])
])

AC_DEFUN([AC_DO_CHECK_SWIG],
[
  where=$1

  if test "$where" = no; then
    AC_PATH_PROG(SWIG, none, none)
  elif test "$where" = check; then
    AC_PATH_PROG(SWIG, swig, none)
  else
    if test -f "$where"; then
      SWIG="$where"
    else
      SWIG="$where/bin/swig"
    fi
    if test ! -f "$SWIG" -o ! -x "$SWIG"; then
      AC_MSG_ERROR([Could not find swig binary at $SWIG])
    fi
  fi

  if test "$SWIG" != "none"; then
    AC_MSG_CHECKING([SWIG version])
    SWIG_VERSION_RAW="`$SWIG -version 2>&1 | \
                       sed -ne 's/^.*Version \(.*\)$/\1/p'`"
    SWIG_VERSION="`echo \"$SWIG_VERSION_RAW\" | \
                  sed -e 's/[[^0-9\.]].*$//' \
                      -e 's/\.\([[0-9]]\)$/.0\1/' \
                      -e 's/\.\([[0-9]][[0-9]]\)$/.0\1/' \
                      -e 's/\.\([[0-9]]\)\./0\1/; s/\.//g;'`"
    AC_MSG_RESULT([$SWIG_VERSION_RAW])
    if test -n "$SWIG_VERSION" && test "$SWIG_VERSION" -ge "103029"; then
      SWIG_SUITABLE=yes
    else
      SWIG_SUITABLE=no
      AC_MSG_WARN([Detected SWIG version $SWIG_VERSION_RAW])
      AC_MSG_WARN([Version 1.3.29 or later is required.])
    fi
  fi
 
  SWIG_PY_COMPILE="none"
  SWIG_PY_LINK="none"
  if test "$PYTHON" != "none" -a "$PYTHON" != ":"; then
    AC_MSG_NOTICE([Configuring Python swig binding])

    AC_CACHE_CHECK([for Python includes], [ac_cv_python_includes],[
      ac_cv_python_includes="`$PYTHON ${ac_confdir}/config/get-py-info.py --includes`"
    ])
    SWIG_PY_INCLUDES="\$(SWIG_INCLUDES) $ac_cv_python_includes"

    if test "$ac_cv_python_includes" = "none"; then
      AC_MSG_WARN([python bindings cannot be built without distutils module])
    fi

    AC_CACHE_CHECK([for compiling Python extensions], [ac_cv_python_compile],[
      ac_cv_python_compile="`$PYTHON ${ac_confdir}/config/get-py-info.py --compile`"
    ])
    SWIG_PY_COMPILE="$ac_cv_python_compile \$(SWIG_PY_INCLUDES)"

    AC_CACHE_CHECK([for linking Python extensions], [ac_cv_python_link],[
      ac_cv_python_link="`$PYTHON ${ac_confdir}/config/get-py-info.py --link`"
    ])
    SWIG_PY_LINK="$ac_cv_python_link"

    AC_CACHE_CHECK([for linking Python libraries], [ac_cv_python_libs],[
      ac_cv_python_libs="`$PYTHON ${ac_confdir}/config/get-py-info.py --libs`"
    ])
    SWIG_PY_LIBS="$ac_cv_python_libs"
  fi

  if test "$PERL" != "none"; then
    AC_MSG_CHECKING([Perl version])
    PERL_VERSION="`$PERL -e 'q([[); print $]] * 1000000,$/;'`"
    AC_MSG_RESULT([$PERL_VERSION])
    if test "$PERL_VERSION" -ge "5008000"; then
      SWIG_PL_INCLUDES="\$(SWIG_INCLUDES) `$PERL -MExtUtils::Embed -e ccopts`"

      AC_CACHE_VAL([libssrcspread_cv_perl_sitedir],[
        libssrcspread_cv_perl_sitedir="`$PERL -e 'use Config; print $Config{sitelib_stem}, \"\n\";'`"
    ])
      AC_ARG_WITH([perl-sitedir],
      AC_HELP_STRING([--with-perl-sitedir=SITEDIR],
                                 [install Perl bindings in SITEDIR
                                  (default is same as Perl's site dir)]),
      [libssrcspread_perl_installdir="$withval"],
      [libssrcspread_perl_installdir="$libssrcspread_cv_perl_sitedir"])

      AC_MSG_CHECKING([where to install Perl extensions])
      AC_CACHE_VAL([libssrcspread_cv_perl_sitedir_archsuffix],[
        libssrcspread_cv_perl_sitedir_archsuffix="`$PERL -e 'use Config; print \"$Config{version}/$Config{archname}\n\";'`"
    ])
      if test "${libssrcspread_perl_installdir}" = "${libssrcspread_cv_perl_sitedir}"; then
	SWIG_PL_SITE_ARCH_DIR="`$PERL -e 'use Config; print \"$Config{installsitearch}\n\";'`"
      else
        SWIG_PL_SITE_ARCH_DIR="${libssrcspread_perl_installdir}/${libssrcspread_cv_perl_sitedir_archsuffix}"
      fi
      AC_MSG_RESULT([$SWIG_PL_SITE_ARCH_DIR])
    else
      AC_MSG_WARN([Perl bindings require Perl 5.8.0 or newer.])
    fi
  fi

  if test "$LUA" != "none"; then
    AC_CACHE_CHECK([for default Lua sitedir], [libssrcspread_cv_lua_sitedir],[
      libssrcspread_cv_lua_sitedir="`$LUA -e 'print(string.match(package.cpath, \"([[^;]]+)/lib/lua/[[^/]]+/[[^;]]*\"))'`"
    ])
    SWIG_LUA_INCLUDES="\$(SWIG_INCLUDES) -I$libssrcspread_cv_lua_sitedir/include"

    AC_ARG_WITH([lua-sitedir],
    AC_HELP_STRING([--with-lua-sitedir=SITEDIR],
                               [install Lua bindings in SITEDIR
                                (default is same as lua's site dir)]),
    [libssrcspread_lua_installdir="$withval"],
    [libssrcspread_lua_installdir="$libssrcspread_cv_lua_sitedir"])

    AC_MSG_CHECKING([where to install Lua extensions])
    AC_CACHE_VAL([libssrcspread_cv_lua_sitedir_archsuffix],[
      libssrcspread_cv_lua_sitedir_archsuffix="`$LUA -e 'print(string.match(package.cpath, \"[[^;]]+/(lib/lua/[[^/]]+/)[[^;]]*\"))'`"
    ])
    SWIG_LUA_SITE_ARCH_DIR="${libssrcspread_lua_installdir}/${libssrcspread_cv_lua_sitedir_archsuffix}"
    AC_MSG_RESULT([$SWIG_LUA_SITE_ARCH_DIR])
  fi

  SWIG_RB_COMPILE_FLAGS="none"
  SWIG_RB_LINK="none"
  if test "$RUBY" != "none"; then

    AC_MSG_NOTICE([Configuring Ruby SWIG binding])

    AC_CACHE_CHECK([for Ruby include path], [libssrcspread_cv_ruby_includes],[
    libssrcspread_cv_ruby_includes="-I. -I`$RUBY -rrbconfig -e 'print RbConfig::CONFIG.fetch(%q(archdir))'` `$RUBY -rrbconfig -e 'RbConfig::CONFIG.has_key?(%q(rubyhdrdir)) and print %q(-I),RbConfig::CONFIG.fetch(%q(rubyhdrdir))'`  `$RUBY -rrbconfig -e 'RbConfig::CONFIG.has_key?(%q(rubyhdrdir)) and print %q(-I),RbConfig::CONFIG.fetch(%q(rubyhdrdir)),%q(/),RbConfig::CONFIG.fetch(%q(arch))'`"
    ])
    SWIG_RB_INCLUDES="\$(SWIG_INCLUDES) $libssrcspread_cv_ruby_includes"

    AC_CACHE_CHECK([how to compile Ruby extensions], [libssrcspread_cv_ruby_compile],[
      libssrcspread_cv_ruby_compile="`$RUBY -rrbconfig -e 'print RbConfig::CONFIG.fetch(%q(CC)), %q( ), RbConfig::CONFIG.fetch(%q(CFLAGS))'` \$(SWIG_RB_INCLUDES)"
    ])

    SWIG_RB_COMPILE_FLAGS="`echo $libssrcspread_cv_ruby_compile | sed -e 's/^ *[[^ ]][[^ ]]*//'`"

    AC_CACHE_CHECK([how to link Ruby extensions], [libssrcspread_cv_ruby_link],[
      libssrcspread_cv_ruby_link="`$RUBY -rrbconfig -e 'print RbConfig::CONFIG.fetch(%q(LDSHARED)).sub(/^\S+/, RbConfig::CONFIG.fetch(%q(CC)))'`"
    ])

    SWIG_RB_LINK="`echo $libssrcspread_cv_ruby_link | sed -e 's/^ *[[^ ]][[^ ]]*//'`"

    AC_CACHE_VAL([libssrcspread_cv_ruby_sitedir],[
      libssrcspread_cv_ruby_sitedir="`$RUBY -rrbconfig -e 'print RbConfig::CONFIG.fetch(%q(sitedir))'`"
    ])
    AC_ARG_WITH([ruby-sitedir],
    AC_HELP_STRING([--with-ruby-sitedir=SITEDIR],
                               [install Ruby bindings in SITEDIR
                                (default is same as ruby's site dir)]),
    [libssrcspread_ruby_installdir="$withval"],
    [libssrcspread_ruby_installdir="$libssrcspread_cv_ruby_sitedir"])

    AC_MSG_CHECKING([where to install Ruby scripts])
    AC_CACHE_VAL([libssrcspread_cv_ruby_sitedir_libsuffix],[
      libssrcspread_cv_ruby_sitedir_libsuffix="`$RUBY -rrbconfig -e 'print RbConfig::CONFIG.fetch(%q(sitelibdir)).sub(/^#{RbConfig::CONFIG.fetch(%q(sitedir))}/, %q())'`"
    ])
    SWIG_RB_SITE_LIB_DIR="${libssrcspread_ruby_installdir}${libssrcspread_cv_ruby_sitedir_libsuffix}"
    AC_MSG_RESULT([$SWIG_RB_SITE_LIB_DIR])

    AC_MSG_CHECKING([where to install Ruby extensions])
    AC_CACHE_VAL([libssrcspread_cv_ruby_sitedir_archsuffix],[
      libssrcspread_cv_ruby_sitedir_archsuffix="`$RUBY -rrbconfig -e 'print RbConfig::CONFIG.fetch(%q(sitearchdir)).sub(/^#{RbConfig::CONFIG.fetch(%q(sitedir))}/, %q())'`"
    ])
    SWIG_RB_SITE_ARCH_DIR="${libssrcspread_ruby_installdir}${libssrcspread_cv_ruby_sitedir_archsuffix}"
    AC_MSG_RESULT([$SWIG_RB_SITE_ARCH_DIR])
  fi
  SWIG_PL_INCLUDES="`echo $SWIG_PL_INCLUDES | sed -e 's/-arch [[^ ]]*//g'`"
  SWIG_PY_COMPILE="`echo $SWIG_PY_COMPILE | sed -e 's/gcc/g++/' -e 's/^cc/g++/' -e 's/ -g / /g'`"
  SWIG_RB_COMPILE_FLAGS="`echo $SWIG_RB_COMPILE_FLAGS | sed -e 's/gcc/g++/' -e 's/^cc/g++/' -e 's/ -g / /g' -e 's/-arch [[^ ]]*//g'`"
  SWIG_PY_LINK="`echo $SWIG_PY_LINK | sed -e 's/gcc/g++/' -e 's/^cc/g++/' -e 's/ -g / /g'`"
  SWIG_RB_LINK="`echo $SWIG_RB_LINK | sed -e 's/gcc/g++/' -e 's/^cc/g++/' -e 's/ -g / /g' -e 's/-arch [[^ ]]*//g'`"
  AC_SUBST(SWIG)
  AC_SUBST(SWIG_PL_INCLUDES)
  AC_SUBST(SWIG_PL_SITE_ARCH_DIR)
  AC_SUBST(SWIG_LUA_INCLUDES)
  AC_SUBST(SWIG_LUA_SITE_ARCH_DIR)
  AC_SUBST(SWIG_PY_INCLUDES)
  AC_SUBST(SWIG_PY_COMPILE)
  AC_SUBST(SWIG_PY_LINK)
  AC_SUBST(SWIG_PY_LIBS)
  AC_SUBST(SWIG_RB_INCLUDES)
  AC_SUBST(SWIG_RB_COMPILE_FLAGS)
  AC_SUBST(SWIG_RB_LINK)
  AC_SUBST(SWIG_RB_SITE_LIB_DIR)
  AC_SUBST(SWIG_RB_SITE_ARCH_DIR)
])
