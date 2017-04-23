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
 * This header defines the Message class.
 */

#ifndef __SSRC_SPREAD_MESSAGE_H
#define __SSRC_SPREAD_MESSAGE_H

#include <ssrc/spread/detail/ByteBuffer.h>
#include <ssrc/spread/MembershipInfo.h>

__BEGIN_NS_SSRC_SPREAD

/**
 * Message is a reusable and resizable data buffer for sending and
 * receiving messages.  We do not document its protected members
 * because they are intended only for internal library use.  All of
 * its useful public methods are inherited from BaseMessage and
 * detail::ByteBuffer.
 *
 * Please note that you can directly access the message data via
 * indexing with detail::Buffer::operator[] or obtaining a pointer
 * to the data via:
 * <pre>&message[0]</pre>
 * Therefore, you will find you do not have to use detail::ByteBuffer::read
 * unless you really have to make a copy of the data instead of using
 * it directly.  However, you should use detail::ByteBuffer::write to avoid
 * overrunning the buffer.
 */
class Message : public BaseMessage, public detail::ByteBuffer {
protected:

#ifdef LIBSSRCSPREAD_ENABLE_MEMBERSHIP_INFO

  virtual int sp_get_membership_info(Spread::membership_info *info) const {
    return Spread::SP_get_memb_info(&(this->operator[](0)), service(), info);
  }

  virtual int sp_get_vs_set_members(const Spread::vs_set_info *vs_set,
                                    Spread::group_type member_names[],
                                    unsigned int member_names_count)
    const
  {
    return
      Spread::SP_get_vs_set_members(&(this->operator[](0)),
                                    vs_set, member_names, member_names_count);
  }

  virtual int sp_get_vs_sets_info(Spread::vs_set_info *vs_sets,
                                  unsigned int num_vs_sets,
                                  unsigned int *index)
    const
  {
    return
      Spread::SP_get_vs_sets_info(&(this->operator[](0)),
                                  vs_sets, num_vs_sets, index);
  }

#endif

public:

  enum {
    /** The default capacity used to construct a Message. */
    DefaultCapacity = 4096
  };

  /**
   * Creates a Message with the specified initial capacity (or
   * DefaultCapacity if no parameter is provided).  See BaseMessage()
   * for the default values of various properties, including service
   * type.
   *
   * @param capacity The initial capacity of the message.
   */
  explicit Message(const unsigned int capacity = DefaultCapacity) :
    detail::ByteBuffer(capacity) { }

  virtual unsigned int size() const {
    return detail::ByteBuffer::size();
  }

  virtual void clear() {
    return detail::ByteBuffer::clear();
  }

};

__END_NS_SSRC_SPREAD

#endif
