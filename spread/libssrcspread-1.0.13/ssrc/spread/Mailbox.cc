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

#include <ssrc/spread/Mailbox.h>
#include <fcntl.h>

__BEGIN_NS_SSRC_SPREAD

/**
 * A constant denoting a timeout of zero seconds and zero
 * microseconds.  This value is taken to mean block indefinitely.
 */
const Timeout Mailbox::ZeroTimeout(0, 0);


/**
 * Creates a Mailbox configured with the specified parameters.
 * Mailbox follows the "resource acquisition is initialization"
 * model.  When a Mailbox is created, it establishes a connection
 * with the specified %Spread daemon.  When it is destroyed, it
 * disconnects.  You cannot reuse a Mailbox to establish multiple
 * connections in succession.  A new Mailbox must be created for each
 * daemon connection.
 *
 * Mailbox::Mailbox sets the FD_CLOEXEC flag on the connection's
 * file descriptor.
 *
 * @param connection The name of the %Spread daemon to connect to.  A
 * zero-length string indicates that the default daemon should be
 * connected to ("4803" or "4803@localhost"; this is an undocumented
 * feature of SP_connect).
 * @param name The name of the session (used to create the private
 * group name).  A zero-length string value indicates that the Spread
 * daemon should assign the session a random unique name.
 * @param group_membership true if you want to receive group
 * membership messages, false if not.  The default is true.
 * @param timeout A timeout for connecting to the daemon.  A value of
 * zero designates no timeout (the default).
 * @param priority The priority level for establishing the connection.
 * @throw Error If the connection cannot be established because of a
 * timeout or some other reason.
 */
Mailbox::Mailbox(const string & connection, const string & name,
                 const bool group_membership, const Timeout & timeout,
                 const Priority priority)
  SSRC_DECL_THROW(Error)
{
  int result;
  Spread::group_type private_group;

  result =
    Spread::SP_connect_timeout(connection.c_str(),
                               (name.size() == 0 ? 0 : name.c_str()), priority,
                               group_membership, &_mbox, private_group,
                               timeout);

  if(result != Error::AcceptSession)
    throw Error(result);

  ::fcntl(_mbox, F_SETFD, (::fcntl(_mbox, F_GETFD) | FD_CLOEXEC));

  _connection = connection;
  _group_membership = group_membership;
  _private_group = private_group;
  _name = split_private_group(_private_group).first;

  _drop_receive  = false;
  _killed        = false;
}

/**
 * Multicasts a message to the specified groups using the service and
 * message type of the message.
 *
 * @param message The message to send.
 * @param groups The list of groups the message should be sent to.
 * @return The number of bytes sent.
 * @throw Error If the operation fails.
 */
int Mailbox::send(const ScatterMessage & message, const GroupList & groups)
  SSRC_DECL_THROW(Error)
{
  int result;

  result =
    Spread::SP_multigroup_scat_multicast(_mbox, message.service(),
                                         groups.size(), groups.groups(),
                                         message.type(), message.scatter());
  if(result < 0)
    throw Error(result);

  return result;
}

/**
 * See send(const ScatterMessage &, const GroupList &).
 */
int Mailbox::send(const Message & message, const GroupList & groups)
  SSRC_DECL_THROW(Error)
{
  clear_message_parts();
  add_message_part(message);
  _scatter.set_type(message.type());
  _scatter.set_service(message.service());
  return send(_scatter, groups);
}

/**
 * Same as send(message, _groups) where _groups is the internal
 * GroupList containing only the supplied group parameter.
 */
int Mailbox::send(const Message & message, const string & group)
  SSRC_DECL_THROW(Error)
{
  clear_groups();
  add_group(group);
  clear_message_parts();
  add_message_part(message);
  _scatter.set_type(message.type());
  _scatter.set_service(message.service());
  return send(_scatter, _groups);
}

/**
 * Receives a multicast group message and records the groups the
 * message was sent to.  If drop_receive() is false and the message
 * buffers are too short, the last Message instance in the
 * ScatterMessage is resized to hold any excess data (see
 * ScatterMessage::add(const Message &) for additional discussion) and
 * the receive attempt is retried.  Also, if drop_receive() is false
 * and the group buffer is too short, the GroupList is automatically resized
 * and the receive attempt retried.
 *
 * @param message A reference to the message that will store the
 * received data.
 * @param groups A reference to the Grouplist that will
 * store the groups the message was sent to.
 *
 * @return The total numbr of bytes received.  If drop_receive() is
 * true, either Error::BufferTooShort or Error::GroupsTooShort is
 * returned when data is dropped.
 *
 * @throw BufferSizeError If the %Spread C API does not provide enough
 * information to retry a receive (when drop_receive() is false).
 * This should not happen unless there is a bug in the %Spread API.
 * Also, a BufferSizeError is thrown when no Message instances are
 * provided in the ScatterMessage and there is an Error::BufferTooShort
 * error.  In that case, it is impossible for receive to resize the
 * message and retry.  In such a case, you will have to manuallly
 * resize your buffers and retry based on the information provided by
 * the BufferSizeError.
 *
 * @throw Error If the operation fails.
 */
int Mailbox::receive(ScatterMessage & message, GroupList & groups)
  SSRC_DECL_THROW(BufferSizeError, Error)
{
  int result, num_groups, endian_mismatch;
  BaseMessage::message_type type;
  BaseMessage::service_type stype;
  Spread::group_type sender;

  groups.resize(groups.capacity());
  message.init_pre_receive();

 try_again:
  type = 0, num_groups = 0, endian_mismatch = 0;
  stype = (_drop_receive ? BaseMessage::DropReceive : 0);

  result =
    Spread::SP_scat_receive(_mbox, &stype, sender, groups.size(), &num_groups,
                            groups.groups(), &type, &endian_mismatch,
                            message.scatter());
  if(!_drop_receive) {
    if(result == Error::GroupsTooShort) {
      if(num_groups < 0) {
        groups.resize(-num_groups);
        if(endian_mismatch == 0)
          goto try_again;
        else
          result = Error::BufferTooShort;
      } else
        throw BufferSizeError(Error::GroupsTooShort, -num_groups);
    }

    if(result == Error::BufferTooShort) {
      if(num_groups < 0)
        groups.resize(-num_groups);

      if(message.count_message_objects() > 0 && endian_mismatch < 0) {
        const unsigned int last_message = message.count_message_objects() - 1;
        Message *m = message.message(last_message);
        // endian_mismatch stores negative of incoming message size
        message.resize_message(last_message,
                               - endian_mismatch - message.size() + m->size());
        goto try_again;
      } else
        throw BufferSizeError(Error::BufferTooShort, -endian_mismatch);
    } else if(result < 0)
      throw Error(result);
  } else if(result < 0 && result != Error::GroupsTooShort &&
            result != Error::BufferTooShort)
    throw Error(result);

  message.set_type(type);
  message.set_service(stype);
  message.set_sender(sender);
  message.set_endian_mismatch(endian_mismatch != 0);

  groups.resize(num_groups);
  message.init_post_receive(result);

  return result;
}

__END_NS_SSRC_SPREAD
