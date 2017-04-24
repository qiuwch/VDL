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
%feature("director");
%feature("compactdefaultargs");

#if SWIGPERL
%module(directors="1") "ssrc::spread"
#elif SWIGLUA
%module(directors="1") _spread
#else
%module(directors="1") spread
#endif

%{
#include <ssrc/spread.h>
%}

/* Fix compilation errors from illegal static cast. */
#if SWIGRUBY
%{
#undef  SWIG_as_voidptr
#define SWIG_as_voidptr(a) const_cast< void * >(reinterpret_cast< const void * >(a)) 
%}
#endif

%include std_pair.i
%include std_string.i

#ifndef SWIGLUA
%include cstring.i
#endif

%import <ssrc/libssrcspread-config.h>
%import <ssrc/libssrcspread-packages.h>

/*
 * General transformations.
 */
%ignore operator[];
%ignore *::operator[];
%ignore operator<<;

%rename(__eq__) operator==;
%rename(copy) operator=;
%rename(copy) *::operator=;

/*
 * Error and BufferSizeError
 */
#ifndef SWIGLUA
%include <ssrc/spread/Error.h>
#else
%{
using NS_SSRC_SPREAD::Error;
using NS_SSRC_SPREAD::BufferSizeError;
%}
#endif

 
/*
 * GroupList
 */

#ifndef SWIGLUA
%template() std::pair<std::string,std::string>;
#else
%template(StringPair) std::pair<std::string,std::string>;
#endif

%include <ssrc/spread/GroupList.h>

%{
bool SWIG_NS_SSRCSPREAD_SYM(_GroupList___eq__) (
                    const NS_SSRC_SPREAD::GroupList * group1,
                    const NS_SSRC_SPREAD::GroupList * group2)
{
  return (*group1 == *group2);
}
%}

%extend NS_SSRC_SPREAD::GroupList {
public:
  bool __eq__(const GroupList * );
};

/*
 * Buffer and ByteBuffer type information.
 */

%import <ssrc/spread/detail/Buffer.h>

%template() NS_SSRC_SPREAD::detail::Buffer<char>;

%import <ssrc/spread/detail/ByteBuffer.h>

/*
 * Pick up Spread C types so our typedefs are reduced properly.
 */

%import <sp.h>

/*
 * BaseMessage
 */
/*
%ignore sp_get_membership_info;
%ignore sp_get_vs_set_members;
%ignore sp_get_vs_sets_info;
*/
%include <ssrc/spread/BaseMessage.h>

/*
 * MembershipInfo
 */

%include <ssrc/spread/MembershipInfo.h>

/*
 * Message
 */

%include <ssrc/spread/Message.h>

%{
unsigned int SWIG_NS_SSRCSPREAD_SYM(_Message_capacity)
(NS_SSRC_SPREAD::Message *message)
{
  return message->capacity();
}

void SWIG_NS_SSRCSPREAD_SYM(_Message_resize)
(NS_SSRC_SPREAD::Message *message, unsigned int size)
{
  return message->resize(size);
}

unsigned int SWIG_NS_SSRCSPREAD_SYM(_Message_offset)
(NS_SSRC_SPREAD::Message *message)
{
  return message->offset();
}

void SWIG_NS_SSRCSPREAD_SYM(_Message_rewind)
(NS_SSRC_SPREAD::Message *message)
{
  message->rewind();
}

unsigned int SWIG_NS_SSRCSPREAD_SYM(_Message_seek)
(NS_SSRC_SPREAD::Message *message, unsigned int offset)
{
  return message->seek(offset);
}

void SWIG_NS_SSRCSPREAD_SYM(_Message_writen)
(NS_SSRC_SPREAD::Message *message, const char *data, int size)
{
  message->write(data, size);
}

unsigned int SWIG_NS_SSRCSPREAD_SYM(_Message_readn)
(NS_SSRC_SPREAD::Message *message, char *data, int bytes)
{
  return message->read(data, bytes);
}
%}

#ifndef SWIGLUA

%{
void SWIG_NS_SSRCSPREAD_SYM(_Message_write)
(NS_SSRC_SPREAD::Message *message, const char *data, int size)
{
  message->write(data, size);
}

void  SWIG_NS_SSRCSPREAD_SYM(_Message_read)
(NS_SSRC_SPREAD::Message *message, char *data, int bytes)
{
  bytes = message->read(data, bytes);
  // Ensure null-termination to satisfy SWIG expectations.
  if(bytes > 0)
    data[bytes] = 0;
  else
    data[0] = 0;
}
%}

#else

%{
void SWIG_NS_SSRCSPREAD_SYM(_Message_write)
(NS_SSRC_SPREAD::Message *message, const char *data)
{
  message->write(data, strlen(data) + 1);
}

std::string SWIG_NS_SSRCSPREAD_SYM(_Message_read)
(NS_SSRC_SPREAD::Message *message, int bytes)
{
  std::string data(bytes, ' ');	
  bytes = message->read(&data[0], bytes);
  // Ensure null-termination to satisfy SWIG expectations.
  if(bytes > 0) {
    // Remove trailing null since string adds its own.
    if(data[bytes - 1] == '\0')
      --bytes;
    data.resize(bytes);
  } else
    data.clear();
  return data;    
}
%}

#endif

%extend NS_SSRC_SPREAD::Message {
public:
  unsigned int capacity();

  void resize(unsigned int size);

  unsigned int offset();

  void rewind();

  unsigned int seek(unsigned int offset);

  unsigned int readn(char *data, int bytes);

  void writen(const char *data, int size);

#ifndef SWIGLUA
  %typemap(in) (const char *data, int size) = (char *STRING, int SIZE);
  void write(const char *data, int size);
#else
  void write(const char *data);
#endif

  // Call second parameter bytes instead of size or it confounds the macro.
#ifndef SWIGLUA
  %cstring_output_maxsize(char *data, int bytes);
  void read(char *data, int bytes);
#else
  std::string read(int bytes);
#endif
};

/*
 * ScatterMessage
 */

#ifndef SWIGLUA
// Allow single-argument string passing.
%typemap(in) (const void *data, const unsigned int size) =
  (char *STRING, int SIZE);
#endif

#if (SWIGLUA || SWIGPERL)

%ignore ScatterMessage::add(const void *, const unsigned int);

%{
bool SWIG_NS_SSRCSPREAD_SYM(_ScatterMessage_add)
(NS_SSRC_SPREAD::ScatterMessage *msg, const char *data, int size)
{
  return msg->add(data, size);
}

bool SWIG_NS_SSRCSPREAD_SYM(_ScatterMessage_add)
(NS_SSRC_SPREAD::ScatterMessage *msg, const char *data)
{
  return msg->add(data, std::strlen(data) + 1);
}
%}

%extend NS_SSRC_SPREAD::ScatterMessage {
public:
  bool add(const char *data, int size);

  bool add(const char *data);
};

#endif

%include <ssrc/spread/ScatterMessage.h>

/*
 * Mailbox
 */
#if (SWIGLUA || SWIGPERL)

%ignore Mailbox::add_message_part(const void *, const unsigned int);

%{
bool SWIG_NS_SSRCSPREAD_SYM(_Mailbox_add_message_part)
(NS_SSRC_SPREAD::Mailbox *mbox, const char *data, int size)
{
  return mbox->add_message_part(data, size);
}

bool SWIG_NS_SSRCSPREAD_SYM(_Mailbox_add_message_part)
(NS_SSRC_SPREAD::Mailbox *mbox, const char *data)
{
  return mbox->add_message_part(data, std::strlen(data) + 1);
}
%}

%extend NS_SSRC_SPREAD::Mailbox {
public:
  bool add_message_part(const char *data, int size);

  bool add_message_part(const char *data);
};

#endif

%include <ssrc/spread/Mailbox.h>

%extend NS_SSRC_SPREAD::Mailbox {
public:
  Mailbox(const string & connection = "", const string & name = "",
          const bool group_membership = true, const long timeout = 0,
          const Priority priority = Medium)
    SSRC_DECL_THROW(Error)
  {
    return new NS_SSRC_SPREAD::Mailbox(connection, name, group_membership, timeout, priority);
  }
};
