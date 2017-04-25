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

#include <ssrc/spread/ScatterMessage.h>

__BEGIN_NS_SSRC_SPREAD

/**
 * Handles auto-resizing prior to a receive.  Each message part that
 * is a Message instance is resized to its capacity so that it may be
 * completely filled if necessary.  The size of the ScatterMessage is
 * adjusted accordingly.
 */
void ScatterMessage::init_pre_receive() {
  int size = _messages.size();

  for(int i = 0; i < size; ++i) {
    value_type & value = _messages[i];
    Message *m = value.first;

    if(value.second >= _scatter.num_elements)
      break;

    _size-=m->size();
    m->resize(m->capacity());
    _size+=m->size();
    _scatter.elements[value.second].len = m->size();
  }
}

/**
 * Handles auto-resizing after a receive.  Each message part that is a
 * Message instance is resized to reflect the number of bytes that was
 * stored in it by the receive.  The type, service, endian mismatch,
 * and sender of eatch Message is set to that of the message (copied
 * from the ScatterMessage).
 *
 * @param bytes_received The total number of bytes received.  May be
 * negative in case of an error.
 */
void ScatterMessage::init_post_receive(int bytes_received) {
  int index = 0, i, len;
  int size = _messages.size();
  Message *m;

  if(bytes_received > 0)
    _size = bytes_received;
  else
    _size = 0;

  for(i = 0; i < size && bytes_received > 0; ++i) {
    value_type & value = _messages[i];
    int mindex = value.second;
    if(mindex >= _scatter.num_elements)
      break;

    while(index < mindex)
      bytes_received-=_scatter.elements[index++].len;

    if(bytes_received <= 0)
      break;

    len = _scatter.elements[mindex].len;
    m   = value.first;

    m->set_type(type());
    m->set_service(service());
    m->set_endian_mismatch(endian_mismatch());
    m->set_sender(_sender);

    if(len <= bytes_received)
      m->resize(len);
    else
      m->resize(bytes_received);

    bytes_received-=len;
  }

  // Anything left over gets a size of zero.
  for(; i < size; ++i) {
    m = _messages[i].first;
    m->resize(0);
    m->set_type(type());
    m->set_service(service());
    m->set_endian_mismatch(endian_mismatch());
    m->set_sender(_sender);
  }
}

/**
 * Adds a message part to the ScatterMessage with a designated number
 * of bytes indicating either the capacity of the buffer (for
 * receiving) or the length of its contents (for sending).
 *
 * @param data A pointer to the data buffer to add.
 * @param size The number of bytes to be filled in to or read from the
 * data buffer.
 * @return true if the message part was added, false if there's no
 * more parts can be added.
 */
bool ScatterMessage::add(const void *data, const unsigned int size) {
  int i = _scatter.num_elements;

  if(i >= MaxScatterElements)
    return false;

  ++_scatter.num_elements;
  _scatter.elements[i].buf = 
    const_cast<char *>(static_cast<const char *>(data));
  _scatter.elements[i].len = size;
  _size+=size;

  return true;
}

__END_NS_SSRC_SPREAD
