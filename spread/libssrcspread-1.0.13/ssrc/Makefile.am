## Copyright 2006-2011 Savarese Software Research Corporation
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
##

include $(top_srcdir)/config/global.mk

SUBDIRS = spread

lib_LTLIBRARIES = libssrcspread.la
libssrcspread_la_SOURCES =
libssrcspread_la_LIBADD  = spread/*.lo
libssrcspread_la_LDFLAGS := -version-number $(subst .,:,$(libssrcspread_lib_version)) $(libssrcspread_with_spread_ldflags)
