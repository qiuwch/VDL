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
 * This header defines the BaseMessage class.
 */

#ifndef __SSRC_SPREAD_BASE_MESSAGE_H
#define __SSRC_SPREAD_BASE_MESSAGE_H

#include <string>

#include <ssrc/libssrcspread-packages.h>

// sp.h includes stddef.h, so we need to include it before sp.h in
// order to ensure it gets skipped while inside the Spread namespace.
#include <cstddef>

__BEGIN_NS_SPREAD_INCLUDE
# include <sp.h>

  // Convert define to typedef.
# if defined(int16)
  typedef int16 foo_int16;
# undef int16
  typedef foo_int16 int16;
# endif
__END_NS_SPREAD_INCLUDE

#include <ssrc/spread/Error.h>
#include <ssrc/spread/GroupList.h>

__BEGIN_NS_SSRC_SPREAD

#ifdef LIBSSRCSPREAD_ENABLE_MEMBERSHIP_INFO

// Forward declaration
class MembershipInfo;

#endif

/**
 * BaseMessage is an abstract class defining the operations shared in
 * common by Message and ScatterMessage.  We do not document its
 * protected members because they are intended only for internal library use.
 */
class BaseMessage {
public:
  /** Defines the type for 16-bit message type identifiers. */
  typedef Spread::int16 message_type;

  /** Defines the type for specifying service types. */
  typedef Spread::service service_type;

  /**
   * Service is not a proper enumeration, but rather a specification
   * of constants corresponding to the %Spread service type flags.  We
   * do not document the meaning of these flags here.  See the %Spread
   * C API documentation to understand their meaning.  We will note,
   * however, that DropReceive is not a service type, but rather a
   * flag instructing the %Spread receive functions to truncate
   * messages and group lists if the buffers are too small.  There
   * should be no need to use this constant in the API as it is
   * handled by Mailbox::set_drop_receive.
   *
   *
   */
  enum Service {
    Unreliable  = UNRELIABLE_MESS,
    Reliable    = RELIABLE_MESS,
    FIFO        = FIFO_MESS,
    Causal      = CAUSAL_MESS,
    Agreed      = AGREED_MESS,
    Safe        = SAFE_MESS,
    SelfDiscard = SELF_DISCARD,
    DropReceive = DROP_RECV,
#define SERVICE_TYPE_DISCARD(s) s ## SelfDiscard = s | SelfDiscard

    SERVICE_TYPE_DISCARD(Unreliable),
    SERVICE_TYPE_DISCARD(Reliable),
    SERVICE_TYPE_DISCARD(FIFO),
    SERVICE_TYPE_DISCARD(Causal),
    SERVICE_TYPE_DISCARD(Agreed),
    SERVICE_TYPE_DISCARD(Safe)

#undef SERVICE_TYPE_DISCARD
  };

private:

#ifdef LIBSSRCSPREAD_ENABLE_MEMBERSHIP_INFO

  void get_vs_set_members(const Spread::vs_set_info *vs_set,
                          GroupList *members, unsigned int offset = 0) const;

#endif

protected:

  message_type _type;
  service_type _service_type;
  bool _endian_mismatch;
  string _sender;

  /**
   * Initializes the class with a message type equal to 0, service
   * type equal to Safe, endian mismatch equal to false, and a
   * zero-length string for the sender.
   */
  BaseMessage() :
    _type(0), _service_type(Safe), _endian_mismatch(false), _sender("")
  { }

#ifdef LIBSSRCSPREAD_ENABLE_MEMBERSHIP_INFO

  virtual int sp_get_membership_info(Spread::membership_info *info) const = 0;

  virtual int sp_get_vs_set_members(const Spread::vs_set_info *vs_set,
                                    Spread::group_type member_names[],
                                    unsigned int member_names_count) const = 0;

  virtual int sp_get_vs_sets_info(Spread::vs_set_info *vs_sets,
                                  unsigned int num_vs_sets,
                                  unsigned int *index) const = 0;

#endif

public:

  /** Virtual destructor. */
  virtual ~BaseMessage() { }

  /**
   * Returns the number of bytes in the message.
   *
   * @return The number of bytes in the message.
   */
  virtual unsigned int size() const = 0;

  /** Clears the message for reuse, resetting its size to zero. */
  virtual void clear() = 0;

#ifdef LIBSSRCSPREAD_ENABLE_MEMBERSHIP_INFO

  void get_membership_info(MembershipInfo & info) const SSRC_DECL_THROW(Error);

#endif

  /**
   * Sets the service type of the message.
   *
   * @param service The service type of the message.
   */
  void set_service(const service_type service) {
    _service_type = service;
  }

  /**
   * Returns the service type requested (for sends) or sent under (for
   * receives) of the message.
   *
   * @return The service type of the message.
   */
  service_type service() const {
    return _service_type;
  }

  /**
   * Sets the message type identifier.
   * @param type The new message type.
   */
  void set_type(const message_type type) {
    _type = type;
  }

  /**
   * Returns the type of the message.
   * @return The type of the message.
   */
  message_type type() const {
    return _type;
  }

  /**
   * Sets the message sender.
   * @param sender The message sender.
   */
  void set_sender(const string & sender) {
    _sender = sender;
  }

  /**
   * Returns the message sender.  This only has meaning for received messages.
   * @return The message sender.
   */
  const string & sender() const {
    return _sender;
  }

  /**
   * Sets the endian mismatch flag to the specified value.
   * @param mismatch The mismatch value.
   */
  void set_endian_mismatch(const bool mismatch = true) {
    _endian_mismatch = mismatch;
  }

  /**
   * Returns true if there is an endian mismatch between sender and receiver,
   * false otherwise.  This only has meaning for received messages.
   * @return true if there is an endian mismatch between sender and receiver,
   * false otherwise.
   */
  bool endian_mismatch() const {
    return _endian_mismatch;
  }

  /** Sets the service type to BaseMessage::Agreed.  */
  void set_agreed() {
    set_service(Agreed);
  }

  /**
   * Returns true if service type is BaseMessage::Agreed, false otherwise.
   * @return true if service type is BaseMessage::Agreed, false otherwise.
   */
  bool is_agreed() const {
    return Is_agreed_mess(service());
  }

  /** Sets the service type to BaseMessage::Causal.  */
  void set_causal() {
    set_service(Causal);
  }

  /**
   * Returns true if service type is BaseMessage::Causal, false otherwise.
   * @return true if service type is BaseMessage::Causal, false otherwise.
   */
  bool is_causal() const {
    return Is_causal_mess(service());
  }

  /** Sets the service type to BaseMessage::FIFO.  */
  void set_fifo() {
    set_service(FIFO);
  }

  /**
   * Returns true if service type is BaseMessage::FIFO, false otherwise.
   * @return true if service type is BaseMessage::FIFO, false otherwise.
   */
  bool is_fifo() const {
    return Is_fifo_mess(service());
  }

  /** Sets the service type to BaseMessage::Reliable.  */
  void set_reliable() {
    set_service(Reliable);
  }

  /**
   * Returns true if service type is BaseMessage::Reliable, false otherwise.
   * @return true if service type is BaseMessage::Reliable, false otherwise.
   */
  bool is_reliable() const {
    return Is_reliable_mess(service());
  }

  /** Sets the service type to BaseMessage::Unreliable.  */
  void set_unreliable() {
    set_service(Unreliable);
  }

  /**
   * Returns true if service type is BaseMessage::Unreliable, false otherwise.
   * @return true if service type is BaseMessage::Unreliable, false otherwise.
   */
  bool is_unreliable() const {
    return Is_unreliable_mess(service());
  }

  /** Sets the service type to BaseMessage::Safe.  */
  void set_safe() {
    set_service(Safe);
  }

  /**
   * Returns true if service type is BaseMessage::Safe, false otherwise.
   * @return true if service type is BaseMessage::Safe, false otherwise.
   */
  bool is_safe() const {
    return Is_safe_mess(service());
  }

  /**
   * Adds or removes the BaseMessage::SelfDiscard flag to or from the
   * service type.
   *
   * @param discard true to set the BaseMessage::SelfDiscard flag, false
   * to remove it.
   */
  void set_self_discard(const bool discard = true) {
    _service_type |= SelfDiscard;
    if(!discard)
      _service_type ^= SelfDiscard;
  }

  /**
   * Returns true if service type has the BaseMessage::SelfDiscard flag set,
   * false otherwise.
   * @return true if service type has the BaseMessage::SelfDiscard flag set,
   * false otherwise.
   */
  bool is_self_discard() const {
    return Is_self_discard(service());
  }

  /**
   * Returns true if this is a regular data (as opposed to membership)
   * message, false otherwise.
   * @return true if this is a regular message, false otherwise.
   */
  bool is_regular() const {
    return Is_regular_mess(service());
  }

  /**
   * Returns true if this is a membership message, false otherwise.
   * @return true if this is a membership message, false otherwise.
   */
  bool is_membership() const {
    return Is_membership_mess(service());
  }
};

__END_NS_SSRC_SPREAD

#endif
