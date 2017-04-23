/* Copyright 2006 Savarese Software Research Corporation
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
 * This header defines the Error class.
 */

#ifndef __SSRC_SPREAD_ERROR_H
#define __SSRC_SPREAD_ERROR_H

#include <ssrc/libssrcspread-packages.h>

// sp.h includes stddef.h, so we need to include it before sp.h in
// order to ensure it gets skipped while inside the Spread namespace.
#include <cstddef>

__BEGIN_NS_SPREAD_INCLUDE
# include <sp.h>
__END_NS_SPREAD_INCLUDE

__BEGIN_NS_SSRC_SPREAD

/**
 * Error is a container for a %Spread error code and is thrown
 * by the library in only truly exceptional circumstances.
 */
class Error {
  const int _error;

public:

  /**
   * Code is not a proper enumeration, but rather a specification of
   * constants corresponding to %Spread return and error codes.  We do
   * not document the meaning of these codes.  See the %Spread C API
   * documentation to understand their meaning.
   */
  enum Code {
    AcceptSession     = ACCEPT_SESSION,
    IllegalSpread     = ILLEGAL_SPREAD,
    CouldNotConnect   = COULD_NOT_CONNECT,
    RejectQuota       = REJECT_QUOTA,
    RejectNoName      = REJECT_NO_NAME,
    RejectIllegalName = REJECT_ILLEGAL_NAME,
    RejectNotUnique   = REJECT_NOT_UNIQUE,
    RejectVersion     = REJECT_VERSION,
    ConnectionClosed  = CONNECTION_CLOSED,
    RejectAuth        = REJECT_AUTH,
    IllegalSession    = ILLEGAL_SESSION,
    IllegalService    = ILLEGAL_SERVICE,
    IllegalMessage    = ILLEGAL_MESSAGE,
    IllegalGroup      = ILLEGAL_GROUP,
    BufferTooShort    = BUFFER_TOO_SHORT,
    GroupsTooShort    = GROUPS_TOO_SHORT,
    MessageTooLong    = MESSAGE_TOO_LONG
#if (LIBSSRCSPREAD_SPREAD_MAJOR_VERSION >= 4)
    , NetErrorOnSession = NET_ERROR_ON_SESSION
#endif
#if (LIBSSRCSPREAD_SPREAD_MAJOR_VERSION >= 5)
    , IllegalTime = ILLEGAL_TIME
#endif
  };

  /**
   * Creates an Error instance containing the spcified error code.
   * @param err The %Spread error code.
   */
  explicit Error(const int err) : _error(err) { }

  /**
   * Returns the error code used to create the Error.
   * @return The error code used to create the Error.
   */
  int error() const {
    return _error;
  }

  /**
   * Prints the message corresponding to the error via SP_error.  We'd
   * like to give you the message as a string, but the documented
   * %Spread C API does not provide such a facility.
   */
  void print() const {
    Spread::SP_error(_error);
  }
};


/**
 * BufferSizeError is a container for a BufferTooShort or
 * GroupTooShort errror, reporting the buffer size required for
 * success.  Only in a rare circumstance will this error be thrown by
 * the library.  In every expected situation the library handles the
 * error itself by automatically resizing buffers and reattempting the
 * operation or by truncating the buffer if so-specified by the user.
 */
class BufferSizeError : public Error {
  const unsigned int _size;

public:

  /**
   * Creates a BufferSizeError instance with the specified error code and
   * required buffer size.
   * @param err The %Spread error code.
   * @param size The required buffer size for a successful retry.
   */
  BufferSizeError(const int err, const unsigned int size) :
    Error(err), _size(size)
  { }

  /**
   * Returns the required buffer size for a successful retry.
   * @return The required buffer size for a successful retry.
   */
  unsigned int size() const {
    return _size;
  }
};

__END_NS_SSRC_SPREAD

#endif
