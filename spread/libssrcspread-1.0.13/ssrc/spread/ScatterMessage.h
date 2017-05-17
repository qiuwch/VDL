/*
 *
 * Copyright 2006,2007 Savarese Software Research Corporation
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
 * This header defines the ScatterMessage class.
 */

#ifndef __SSRC_SPREAD_SCATTER_MESSAGE_H
#define __SSRC_SPREAD_SCATTER_MESSAGE_H

#include <ssrc/spread/Message.h>

#include <utility>
#include <vector>

__BEGIN_NS_SSRC_SPREAD

/**
 * ScatterMessage is a reusable container of multiple in-place data
 * buffers.  It can be populated with Message instances or straight
 * data pointers.  However, the auto-resizing feature of
 * Mailbox::receive will be exercised only if the ScatterMessage
 * contains at least one Message instance.  You will want to use a
 * ScatterMessage primarily when you want to avoid multiple buffer
 * copies.  For example, if you know the format of an incoming message
 * you can add data pointers for each message part instead of parsing
 * the message and copying the data.  Also, instead of allocating a
 * message buffer and copying multiple data items to it for a send,
 * you can populate a ScatterMessage with pointers to the data items
 * and avoid an extra copy.
 *
 * We do not document ScatterMessage protected members because they
 * are intended only for internal library use.
 */
class ScatterMessage : public BaseMessage {
public:

  enum {
    /**
     * The maximum number of elements that can be added to a scatter
     * message.
     */
    MaxScatterElements = MAX_CLIENT_SCATTER_ELEMENTS
  };

private:
  friend class Mailbox;

  typedef std::pair<Message *, int> value_type;

  Spread::scatter _scatter;
  std::vector<value_type> _messages;
  unsigned int _size;

  const Spread::scatter *scatter() const {
    return &_scatter;
  }

  Spread::scatter *scatter() {
    return &_scatter;
  }

  void init_pre_receive();

  void init_post_receive(int bytes_received);

  Message * message(const unsigned int index) {
    return _messages[index].first;
  }

  void resize_message(const unsigned int message_index,
                      const unsigned int size)
  {
    value_type & v = _messages[message_index];
    Message *m = v.first;

    _size-=m->size();
    m->resize(size);
    _size+=m->size();
    _scatter.elements[v.second].buf = &((*m)[0]);
    _scatter.elements[v.second].len = m->size();
  }

protected:

#ifdef LIBSSRCSPREAD_ENABLE_MEMBERSHIP_INFO

  virtual int sp_get_membership_info(Spread::membership_info *info) const {
    return Spread::SP_scat_get_memb_info(&_scatter, service(), info);
  }

  virtual int sp_get_vs_set_members(const Spread::vs_set_info *vs_set,
                                        Spread::group_type member_names[],
                                        unsigned int member_names_count)
    const
  {
    return
      Spread::SP_scat_get_vs_set_members(&_scatter, vs_set, member_names,
                                         member_names_count);
  }

  virtual int sp_get_vs_sets_info(Spread::vs_set_info *vs_sets,
                                      unsigned int num_vs_sets,
                                      unsigned int *index)
    const
  {
    return
      Spread::SP_scat_get_vs_sets_info(&_scatter, vs_sets, num_vs_sets, index);
  }

#endif

public:

  /**
   * Creates a ScatterMessage with a size of zero and no message parts.
   * See BaseMessage() for the default values of various properties,
   * including service type.
   */
  // The initial vector capacity of 8 is an arbitrary choice.  We don't expect
  // a typical ScatterMessage to have too many parts.
  ScatterMessage() : _messages(8), _size(0) {
    _scatter.num_elements = 0;
  }

  /**
   * Returns the total size of the message (comprising all of its
   * parts) in bytes.
   * @returns The total size of the message in bytes.
   */
  virtual unsigned int size() const {
    return _size;
  }

  /**
   * Clears the message for reuse, resetting both its size and number
   * of message parts to zero.
   */
  virtual void clear() {
    _scatter.num_elements = 0;
    _size = 0;
    _messages.clear();
  }

  /**
   * Returns the number of parts that have been added to the message.
   * @return The number of parts that have been added to the message.
   */
  unsigned int count_message_parts() const {
    return _scatter.num_elements;
  }

  /**
   * Returns the number of Message instances that have been added to
   * the message.  This number will be different from that returned by
   * count_message_parts() if any straight pointers have ben added.
   *
   * @return The number of Message instances that have been added to the
   * message.
   */
  unsigned int count_message_objects() const {
    return _messages.size();
  }

  bool add(const void *data, const unsigned int size);

  /**
   * Adds a Message as a message part.  ScatterMessage will store a
   * pointer to the original Message; therefore you should not alter
   * the Message between the time it is added and when the send or
   * receive is performed.  Note that for receives, each Message added
   * will be filled up to its capacity, not its size.  The size will
   * be ajdusted to reflect the amount of data written to the Message.
   * The capacity will not be increased to accommodate more data
   * except for the last Message added to the ScatterMessage.  If you
   * don't want this behavior, use add(const void *, const unsigned int)
   * instead, with <code>&message[0]</code> as the data argument.
   * When using fixed-length message parts, it is often useful to tack
   * on a Message as the last message part to store any unexpected
   * overflow.
   *
   * @param message The Message to add.
   * @return true if the message part was added, false if no more parts
   *         can be added.
   */
  bool add(const Message & message) {
    if(add(&message[0], message.size())) {
      // We cheat and cast away constness!
      _messages.push_back(value_type(const_cast<Message*>(&message),
                                     _scatter.num_elements - 1));
      return true;
    } else
      return false;
  }
};


__END_NS_SSRC_SPREAD

#endif
