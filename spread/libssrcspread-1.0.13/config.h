/* config.h.  Generated from config.h.in by configure.  */
/* config.h.in.  Generated from configure.ac by autoheader.  */

/* Enable debug code. */
/* #undef DEBUG */

/* Boost is available. */
/* #undef HAVE_BOOST */

/* Define to 1 if you have the <dlfcn.h> header file. */
#define HAVE_DLFCN_H 1

/* Define to 1 if you have the <inttypes.h> header file. */
#define HAVE_INTTYPES_H 1

/* Define to 1 if you have the <memory.h> header file. */
#define HAVE_MEMORY_H 1

/* Define if the compiler implements namespaces. */
#define HAVE_NAMESPACES 1

/* Define to 1 if you have the `SP_get_memb_info' function. */
/* #undef HAVE_SP_GET_MEMB_INFO */

/* Define to 1 if you have the `SP_kill' function. */
/* #undef HAVE_SP_KILL */

/* Define to 1 if you have the <stdint.h> header file. */
#define HAVE_STDINT_H 1

/* Define to 1 if you have the <stdlib.h> header file. */
#define HAVE_STDLIB_H 1

/* Define to 1 if you have the <strings.h> header file. */
#define HAVE_STRINGS_H 1

/* Define to 1 if you have the <string.h> header file. */
#define HAVE_STRING_H 1

/* Define to 1 if you have the <sys/stat.h> header file. */
#define HAVE_SYS_STAT_H 1

/* Define to 1 if you have the <sys/types.h> header file. */
#define HAVE_SYS_TYPES_H 1

/* Define to 1 if you have the <unistd.h> header file. */
#define HAVE_UNISTD_H 1

/* Define to the sub-directory where libtool stores uninstalled libraries. */
#define LT_OBJDIR ".libs/"

/* Name of package */
#define PACKAGE "libssrcspread"

/* Define to the address where bug reports for this package should be sent. */
#define PACKAGE_BUGREPORT ""

/* Define to the full name of this package. */
#define PACKAGE_NAME "libssrcspread"

/* Define to the full name and version of this package. */
#define PACKAGE_STRING "libssrcspread 1.0.13"

/* Define to the one symbol short name of this package. */
#define PACKAGE_TARNAME "libssrcspread"

/* Define to the home page for this package. */
#define PACKAGE_URL ""

/* Define to the version of this package. */
#define PACKAGE_VERSION "1.0.13"

/* Spread major version. */
#define SPREAD_MAJOR_VERSION (SPREAD_VERSION >> 24)

/* Define to 1 if you have the ANSI C header files. */
#define STDC_HEADERS 1

/* Version number of package */
#define VERSION "1.0.13"


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

