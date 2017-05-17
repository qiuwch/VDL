/* automatically generated */
#ifndef _LIBSSRCSPREAD_CONFIG_H
#define _LIBSSRCSPREAD_CONFIG_H 1
 
/* libssrcspread-config.h. Generated automatically at end of configure. */
/* config.h.  Generated from config.h.in by configure.  */
/* config.h.in.  Generated from configure.ac by autoheader.  */

/* Enable debug code. */
/* #undef LIBSSRCSPREAD_DEBUG */

/* Boost is available. */
/* #undef LIBSSRCSPREAD_HAVE_BOOST */

/* Define to 1 if you have the <dlfcn.h> header file. */
#ifndef LIBSSRCSPREAD_HAVE_DLFCN_H 
#define LIBSSRCSPREAD_HAVE_DLFCN_H  1 
#endif

/* Define to 1 if you have the <inttypes.h> header file. */
#ifndef LIBSSRCSPREAD_HAVE_INTTYPES_H 
#define LIBSSRCSPREAD_HAVE_INTTYPES_H  1 
#endif

/* Define to 1 if you have the <memory.h> header file. */
#ifndef LIBSSRCSPREAD_HAVE_MEMORY_H 
#define LIBSSRCSPREAD_HAVE_MEMORY_H  1 
#endif

/* Define if the compiler implements namespaces. */
#ifndef LIBSSRCSPREAD_HAVE_NAMESPACES 
#define LIBSSRCSPREAD_HAVE_NAMESPACES  1 
#endif

/* Define to 1 if you have the `SP_get_memb_info' function. */
/* #undef LIBSSRCSPREAD_HAVE_SP_GET_MEMB_INFO */

/* Define to 1 if you have the `SP_kill' function. */
/* #undef LIBSSRCSPREAD_HAVE_SP_KILL */

/* Define to 1 if you have the <stdint.h> header file. */
#ifndef LIBSSRCSPREAD_HAVE_STDINT_H 
#define LIBSSRCSPREAD_HAVE_STDINT_H  1 
#endif

/* Define to 1 if you have the <stdlib.h> header file. */
#ifndef LIBSSRCSPREAD_HAVE_STDLIB_H 
#define LIBSSRCSPREAD_HAVE_STDLIB_H  1 
#endif

/* Define to 1 if you have the <strings.h> header file. */
#ifndef LIBSSRCSPREAD_HAVE_STRINGS_H 
#define LIBSSRCSPREAD_HAVE_STRINGS_H  1 
#endif

/* Define to 1 if you have the <string.h> header file. */
#ifndef LIBSSRCSPREAD_HAVE_STRING_H 
#define LIBSSRCSPREAD_HAVE_STRING_H  1 
#endif

/* Define to 1 if you have the <sys/stat.h> header file. */
#ifndef LIBSSRCSPREAD_HAVE_SYS_STAT_H 
#define LIBSSRCSPREAD_HAVE_SYS_STAT_H  1 
#endif

/* Define to 1 if you have the <sys/types.h> header file. */
#ifndef LIBSSRCSPREAD_HAVE_SYS_TYPES_H 
#define LIBSSRCSPREAD_HAVE_SYS_TYPES_H  1 
#endif

/* Define to 1 if you have the <unistd.h> header file. */
#ifndef LIBSSRCSPREAD_HAVE_UNISTD_H 
#define LIBSSRCSPREAD_HAVE_UNISTD_H  1 
#endif

/* Define to the sub-directory where libtool stores uninstalled libraries. */
#ifndef LIBSSRCSPREAD_LT_OBJDIR 
#define LIBSSRCSPREAD_LT_OBJDIR  ".libs/" 
#endif

/* Name of package */
#ifndef LIBSSRCSPREAD_PACKAGE 
#define LIBSSRCSPREAD_PACKAGE  "libssrcspread" 
#endif

/* Define to the address where bug reports for this package should be sent. */
#ifndef LIBSSRCSPREAD_PACKAGE_BUGREPORT 
#define LIBSSRCSPREAD_PACKAGE_BUGREPORT  "" 
#endif

/* Define to the full name of this package. */
#ifndef LIBSSRCSPREAD_PACKAGE_NAME 
#define LIBSSRCSPREAD_PACKAGE_NAME  "libssrcspread" 
#endif

/* Define to the full name and version of this package. */
#ifndef LIBSSRCSPREAD_PACKAGE_STRING 
#define LIBSSRCSPREAD_PACKAGE_STRING  "libssrcspread 1.0.13" 
#endif

/* Define to the one symbol short name of this package. */
#ifndef LIBSSRCSPREAD_PACKAGE_TARNAME 
#define LIBSSRCSPREAD_PACKAGE_TARNAME  "libssrcspread" 
#endif

/* Define to the home page for this package. */
#ifndef LIBSSRCSPREAD_PACKAGE_URL 
#define LIBSSRCSPREAD_PACKAGE_URL  "" 
#endif

/* Define to the version of this package. */
#ifndef LIBSSRCSPREAD_PACKAGE_VERSION 
#define LIBSSRCSPREAD_PACKAGE_VERSION  "1.0.13" 
#endif

/* Spread major version. */
#ifndef LIBSSRCSPREAD_SPREAD_MAJOR_VERSION 
#define LIBSSRCSPREAD_SPREAD_MAJOR_VERSION  (SPREAD_VERSION >> 24) 
#endif

/* Define to 1 if you have the ANSI C header files. */
#ifndef LIBSSRCSPREAD_STDC_HEADERS 
#define LIBSSRCSPREAD_STDC_HEADERS  1 
#endif

/* Version number of package */
#ifndef LIBSSRCSPREAD_VERSION 
#define LIBSSRCSPREAD_VERSION  "1.0.13" 
#endif


#if !defined(NS_SSRCSPREAD)
#  define NS_SSRCSPREAD ssrcspread_v1_0_13
#endif

#if !defined(SWIG_NS_SSRCSPREAD)
#  define SWIG_NS_SSRCSPREAD ssrcspread_v1_0_13
#  define SWIG_NS_SSRCSPREAD_SYM(sym) ssrcspread_v1_0_13 ## sym
#endif

#if !defined(LIBSSRCSPREAD_DEFINE_NAMESPACE)
#  define LIBSSRCSPREAD_DEFINE_NAMESPACE(name) NS_SSRCSPREAD::name
#endif

#if !defined(NS_SSRCSPREAD_DECL_PREFIX)
#  define NS_SSRCSPREAD_DECL_PREFIX \
namespace ssrcspread_v1_0_13 {
#endif

#if !defined(NS_SSRCSPREAD_DECL_SUFFIX)
#  define NS_SSRCSPREAD_DECL_SUFFIX \
}
#endif

#if !defined(LIBSSRCSPREAD_TEST_DAEMON)
#  define LIBSSRCSPREAD_TEST_DAEMON "4803"
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

 
/* _LIBSSRCSPREAD_CONFIG_H */
#endif
