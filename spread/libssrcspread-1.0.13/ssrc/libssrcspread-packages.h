/*
 *
 * Copyright 2006 Savarese Software Research Corporation
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.savarese.com/software/ApacheLicense-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

/**
 * @file
 * This header defines the macros for the package namespaces.  These
 * macros are for use internal to the library.  Client code should
 * refer only to ssrc:: prefixed namespaces (e.g., ssrc::spread)
 *
 * This header also includes libssrcspread-config.h so that all modules pick
 * up the platform-specific feature definitions since every module
 * ultimately includes this header.
 */

#ifndef __SSRC_LIBSSRCSPREAD_PACKAGES_H
#define __SSRC_LIBSSRCSPREAD_PACKAGES_H

#include <ssrc/libssrcspread-config.h>

// Begin namespace definitions.

#define NS_SSRC_SPREAD    NS_SSRCSPREAD
#define NS_SPREAD_INCLUDE Spread

#define NS_SSRCSPREAD_INTERNAL_DECL_PREFIX NS_SSRCSPREAD_DECL_PREFIX
#define NS_SSRCSPREAD_INTERNAL_DECL_SUFFIX NS_SSRCSPREAD_DECL_SUFFIX

#define NS_SSRCSPREAD_EXTERNAL_DECL_PREFIX \
namespace ssrc {
#define NS_SSRCSPREAD_EXTERNAL_DECL_SUFFIX \
}

#define __END_NS_SSRCSPREAD \
    } \
NS_SSRCSPREAD_DECL_SUFFIX

#define LIBSSRCSPREAD_BEGIN_NS(name) \
  NS_SSRCSPREAD_DECL_PREFIX \
    namespace name {

#define __BEGIN_NS_SSRC_SPREAD  NS_SSRCSPREAD_DECL_PREFIX
#define __END_NS_SSRC_SPREAD    NS_SSRCSPREAD_DECL_SUFFIX

#define __BEGIN_NS_SPREAD_INCLUDE \
namespace Spread {
#define __END_NS_SPREAD_INCLUDE \
}

// End namespace definitions.

// Document namespaces

/**  
 * The ssrc::spread namespace contains group communication classes
 * that wrap the %Spread Toolkit's C API.
 */
NS_SSRCSPREAD_INTERNAL_DECL_PREFIX

/**  
 * The ssrc::spread::detail namespace contains classes that are used
 * internally by ssrc::spread classes, but are not meant for use by
 * library users.  The classes are documented so that you may use
 * the methods inherited by their public subclasses.  Please do not
 * directly use the classes in this namespace because they are not
 * feature complete and their implementation may change in
 * incompatible ways at any time.
 */
namespace detail { }

NS_SSRCSPREAD_INTERNAL_DECL_SUFFIX

/**
 * The %Spread C API from <sp.h> can be accessed via the %Spread
 * namespace if required, but it is intended for internal use by Ssrc
 * %Spread to avoid polluting the global namespace.  If, for example,
 * you want to use the %Spread event system, you can access it through
 * this namespace.  However, we recommend you use the cross-platform
 * libevent library because it takes advantage of more efficient
 * platform-specific system calls when available.
 */
namespace Spread { }

// Create aliases

/**
 * The ssrc namespace is an alias intended for use by library users.
 * The alternate namespaces prefixed by ssrcspread_vX_X_X contain
 * versioning information internal to the library and should not be used
 * outside of it.  For example, you should use the namespace ssrc::spread
 * instead of ssrcspread_vX_X_X.
 */
NS_SSRCSPREAD_EXTERNAL_DECL_PREFIX

  namespace spread = NS_SSRC_SPREAD;

NS_SSRCSPREAD_EXTERNAL_DECL_SUFFIX

// End namespace aliases

#endif
