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
 * This header defines the Mailbox class.
 */

#ifndef __SSRC_SPREAD_MAILBOX_H
#define __SSRC_SPREAD_MAILBOX_H

#include <ssrc/spread/ScatterMessage.h>

__BEGIN_NS_SSRC_SPREAD

/**
 * Timeout is a simple wrapper around Spread::sp_time the %Spread C
 * API's Spread::sp_time struct that facilitates specifying connection
 * timeouts for the Mailbox constructor.  The constructor will convert
 * an integral number into a Timeout instance, allowing you to specify
 * timeouts to the Mailbox constructor as either Timeout instances or
 * a single number (interpreted as a number of seconds).
 */
class Timeout {
  Spread::sp_time time;

public:
  /**
   * Converts a Spread::sp_time instance to a Timeout instance, copying
   * the stored time representation in the process.
   *
   * @param time The Spread::sp_time instance to convert.
   */
  Timeout(const Spread::sp_time time) : time(time) { }

  /**
   * Creates a Timeout instance representing a number of seconds
   * plus microseconds.  The constructor also is able to convert
   * an int or long to a Timeout, interpreting the number as the
   * first constructor argument (the number of seconds).
   *
   * @param sec The number of seconds.
   * @param usec The number of microseconds.
   */
  Timeout(const long sec = 0, const long usec = 0) {
    time.sec = sec, time.usec = usec;
  }

  /**
   * Converts a Timeout instance to a Spread::sp_time instance.
   *
   * @return A Spread::sp_time value representing the same time value.
   */
  operator Spread::sp_time() const { return time; }
};

/**
 * The Mailbox class wraps the file descriptor returned after
 * establishing a connection to a %Spread daemon and the operations
 * that can be performed with it.  The class is not named Connection
 * because it can lead to confusion.  The connection is between the
 * client application and the %Spread daemon, but through that
 * connection the client application can send and receive messages to
 * and from multiple destinations.  We feel that Mailbox is the more
 * conceptually appropriate metaphor.  Messages can be sent and
 * received to and from multiple destinations through a mailbox.  The
 * %Spread daemon acts as a post office, mediating and routing the
 * message transmission and retrieval.  A connection is a
 * point-to-point concept.  Beyond initializing a Mailbox, the client
 * application need not be conscious that there is a %Spread daemon in
 * the communication path.
 *
 * A Mailbox provides three different modes of interaction for sending
 * and receivng messages.  The first mode requires you to provide the
 * message and destination/source group list on every send and
 * receive.  The second mode involves using only the internal
 * ScatterMessage and GroupList maintained by Mailbox.  That is, you
 * add groups and messages to Mailbox instead of your own GroupList
 * and ScatterMessage.  The third mode involves a mixture of the two,
 * where you can specify either your own message or group list, and
 * let the Mailbox internal message or group list provide the other.
 *
 * The second and third modes are intended as convenience methods for
 * those programmers who prefer that model.  The first mode is a
 * direct analog to the %Spread C API and is what was originally
 * intended as the primary mode of use.  However, it turns out that
 * the %Spread C API delegates all of the non-scatter send and receive
 * functions to the scatter send and receive functions.  Therefore,
 * Mailbox uses only the scatter versions of the functions to do its
 * work, bypassing a level of indirection.  However, to support
 * sending a single message to a single group, as in send(const
 * Message &, const string &), Mailbox must maintain its own GroupList
 * and place the group name in the GroupList.  Also, it must maintain
 * its own ScatterMessage and add the Message to the ScatterMessage
 * before the send.  In fact, this is what the non-scatter %Spread C
 * API functions do.  Since these scratch variables are maintained
 * anyway to support the non-scatter convenience methods, we don't
 * lose anything by making them availble in the public API.  It is up
 * to the programmer to choose between the methods.  To disambiguate,
 * whenever you provide your own ScatterMessage or GroupList, it is
 * used directly, bypassing the internal scratch variables.  The
 * scratch variables are used only when you provide single-group
 * string destination or non-scatter messages.
 *
 * @section mailbox_examples Examples
 *
 * @subsection mailbox_examples_mode1 Mode 1 (provide your own Message and GroupList)
 * <pre>
 * Mailbox mbox(...);
 * ScatterMessage message;
 * GroupList destination;
 * char *data = "foo";
 *
 * destination.add("group1");
 * destination.add("group2");
 * message.add(data, 3);
 * mbox.send(message, destination);
 * </pre>
 *
 * @subsection mailbox_examples_mode2 Mode 2 (use Mailbox buffers)
 * <pre>
 * Mailbox mbox(...);
 * char *data = "foo";
 *
 * mbox.clear_groups();
 * mbox.add_group("group1");
 * mbox.add_group("group2");
 * mbox.clear_message_parts();
 * mbox.add_message_part(data, 3);
 * mbox.send();
 * </pre>
 *
 * @subsection mailbox_examples_mode3 Mode 3 (mixed mode)
 * <pre>
 * Mailbox mbox(...);
 * ScatterMessage message;
 * char *data = "foo";
 *
 * mbox.clear_groups();
 * mbox.add_group("group1");
 * mbox.add_group("group2");
 * message.add(data, 3);
 * mbox.send(message);
 * </pre>
 */
class Mailbox {
public:
  /** Defines the type for the Mailbox file descriptor. */
  typedef Spread::mailbox descriptor_type;

  static const Timeout ZeroTimeout;

  /**
   * The Priority enumeration defines the priority levels for establishing
   * a mailbox connection.
   */
  enum Priority {
    Low = LOW_PRIORITY, Medium = MEDIUM_PRIORITY, High = HIGH_PRIORITY
  };

private:
  bool _group_membership, _drop_receive, _killed;
  string _connection, _name, _private_group;
  descriptor_type _mbox;
  ScatterMessage _scatter;
  GroupList _groups;

public:

  explicit Mailbox(const string & connection = "", const string & name = "",
                   const bool group_membership = true,
                   const Timeout & timeout = ZeroTimeout,
                   const Priority priority = Medium) SSRC_DECL_THROW(Error);

  /**
   * Disconnects from the %Spread daemon unless kill() was called during
   * the lifetime of the object.
   */
  ~Mailbox() {
    if(!killed())
      Spread::SP_disconnect(_mbox);
  }

  /**
   * Returns the name of the %Spread daemon connection.
   * @return The name of the %Spread daemon connection.
   */
  const string & connection() const {
    return _connection;
  }

  /**
   * Returns the name of the Mailbox.
   * @return The name of the Mailbox.
   */
  const string & name() const {
    return _name;
  }

  /**
   * Returns the file descriptor of the connection to the %Spread daemon.
   * This file descriptor is made available to allow you to hook into an
   * event handling system (e.g., select, poll, Linux epoll).
   * @return The file descriptor of the connection to the %Spread daemon.
   */
  descriptor_type descriptor() const {
    return _mbox;
  }

  /**
   * Returns the private group name of the Mailbox.
   * @return The private group name of the Mailbox.
   */
  const string & private_group() const {
    return _private_group;
  }

  /**
   * Returns true if reception of group membership messages is
   * enabled, false if not.
   * @return true if reception of group membership messages is
   * enabled, false if not.
   */
  bool group_membership() const {
    return _group_membership;
  }

  /**
   * Sets whether or not received messages that are too large to fit
   * in the provided buffer should be truncated.  By default, Mailbox
   * does not drop data and instead resizes Message instances to hold
   * the data and retries the receive.
   * @param drop true to drop excess data, false to preserve it and retry.
   */
  void set_drop_receive(const bool drop = true) {
    _drop_receive = drop;
  }

  /**
   * Returns true if excess received data will be dropped, false if not.
   * @return true if excess received data will be dropped, false if not.
   */
  bool drop_receive() const {
    return _drop_receive;
  }

  /**
   * Joins the specified group.
   *
   * @param group The name of the group to join.
   * @throw Error If the operation fails.
   */
  void join(const string & group) SSRC_DECL_THROW(Error) {
    int result = Spread::SP_join(_mbox, group.c_str());
    if(result != 0)
      throw Error(result);
  }

  /**
   * Leaves the specified group.
   *
   * @param group The name of the group to leave.
   * @throw Error If the operation fails.
   */
  void leave(const string & group) SSRC_DECL_THROW(Error) {
    int result = Spread::SP_leave(_mbox, group.c_str());
    if(result != 0)
      throw Error(result);
  }

#ifdef LIBSSRCSPREAD_ENABLE_MAILBOX_KILL
  /**
   * Closes the connection to the %Spread daemon without notifying the
   * daemon.  If you call this, you can't use the object anymore!  It
   * is provided for forking purposes only, so that a child or parent
   * may continue using the Mailbox while the other discontinues using
   * it.
   *
   * <b>Warning:</b> This method is available only when compiled against
   * %Spread 4.x and greater.
   */
  void kill() {
    Spread::SP_kill(_mbox);
    _killed = true;
  }
#endif

  /**
   * Returns true if kill() has been called, false if not.
   *
   * <b>Warning:</b> This method always returns false when not
   * compiled against %Spread 4.x and greater.
   *
   * @return true if kill() has been called, false if not.
   */
  bool killed() const {
    return _killed;
  }

  /**
   * Polls the Mailbox to see if any messags have arrived that can be
   * retrieved via receive().
   *
   * @return The number of bytes available to be received (0 if there
   * are no messages).
   * @throw Error If the operation fails.
   */
  unsigned int poll() const SSRC_DECL_THROW(Error) {
    int result = Spread::SP_poll(_mbox);
    if(result < 0)
      throw Error(result);
    return result;
  }

  /**
   * Adds a message part to the internal ScatterMessage.
   *
   * @param data A pointer to the data buffer.
   * @param size The size of the data buffer in bytes.
   */
  bool add_message_part(const void *data, const unsigned int size) {
    return _scatter.add(data, size);
  }

  /**
   * Adds a Message to the internal ScatterMessage.  The service
   * type and message type of the Message will not be used in a send
   * because the internal ScatterMessage may contain multiple Message
   * parts.  You must specify the types as parameters to the appropriate
   * send() call.
   *
   * @param message The Message to add.
   */
  bool add_message_part(const Message & message) {
    return _scatter.add(message);
  }

  /**
   * Appends a group name to the end of the internal GroupList.
   *
   * @param group The name of the group to add.
   */
  void add_group(const string & group) {
    _groups.add(group);
  }

  /**
   * Appends the contents of a GroupList to the end of the internal GroupList.
   *
   * @param groups The GroupList to append.
   */
  void add_groups(const GroupList & groups) {
    _groups.add(groups);
  }

  /**
   * Returns the name of the group at the specified position in the
   * internal Grouplist.
   *
   * @param index The index of the group name to return.
   * @return The name of the group at the specified position in the
   * internal Grouplist.
   */
  string group(const unsigned int index) const {
    return _groups[index];
  }

  /**
   * Copies the internal GroupList.
   *
   * @param groups A reference to the GroupList that will store the copy.
   */
  void copy_groups(GroupList & groups) {
    groups = _groups;
  }

  /**
   * Returns the number of groups contained in the internal GroupList.
   * @return The number of groups contained in the internal GroupList.
   */
  unsigned int count_groups() const {
    return _groups.size();
  }

  /**
   * Clears the internal GroupList.
   */
  void clear_groups() {
    _groups.clear();
  }

  /**
   * Returns the number of message parts in the internal ScatterMessage.
   * @return The number of message parts in the internal ScatterMessage.
   */
  unsigned int count_message_parts() const {
    return _scatter.count_message_parts();
  }

  /**
   * Clears the internal ScatterMessage.
   */
  void clear_message_parts() {
    _scatter.clear();
  }

  int send(const Message & message, const string & group)
    SSRC_DECL_THROW(Error);

  int send(const Message & message, const GroupList & groups)
    SSRC_DECL_THROW(Error);

  int send(const ScatterMessage & message, const GroupList & groups)
    SSRC_DECL_THROW(Error);

  /**
   * Same as send(message, _groups) where _groups is the internal
   * GroupList containing only the supplied group parameter.
   */
  int send(const ScatterMessage & message, const string & group)
    SSRC_DECL_THROW(Error)
  {
    clear_groups();
    add_group(group);
    return send(message, _groups);
  }

  /**
   * Same as send(_scatter, groups) where _scatter is the internal
   * ScatterMessage after having its type and service set to to the
   * supplied type and service values.
   *
   * @throw Error If the operation fails.
   */
  int send(const GroupList & groups, const BaseMessage::message_type type = 0,
           const BaseMessage::service_type service = BaseMessage::Safe)
    SSRC_DECL_THROW(Error)
  {
    _scatter.set_type(type);
    _scatter.set_service(service);
    return send(_scatter, groups);
  }

  /**
   * Same as send(_groups, type, service) where _groups is the internal
   * GroupList containing only the supplied group parameter.
   *
   * @throw Error If the operation fails.
   */
  int send(const string & group, const BaseMessage::message_type type = 0,
           const BaseMessage::service_type service = BaseMessage::Safe)
    SSRC_DECL_THROW(Error)
  {
    clear_groups();
    add_group(group);
    return send(_groups, type, service);
  }

  /**
   * Same as send(_groups, type, service) where _groups is the internal
   * GroupList.
   *
   * @throw Error If the operation fails.
   */
  int send(const BaseMessage::message_type type = 0,
           const BaseMessage::service_type service = BaseMessage::Safe)
    SSRC_DECL_THROW(Error)
  {
    return send(_groups, type, service);
  }

  /**
   * Same as send(messaage, _groups) where _groups is the internal GroupList.
   *
   * @throw Error If the operation fails.
   */
  int send(const Message & message) SSRC_DECL_THROW(Error) {
    return send(message, _groups);
  }

  /**
   * Same as send(messaage, _groups) where _groups is the internal GroupList.
   *
   * @throw Error If the operation fails.
   */
  int send(const ScatterMessage & message) SSRC_DECL_THROW(Error) {
    return send(message, _groups);
  }

  int receive(ScatterMessage & message, GroupList & groups)
    SSRC_DECL_THROW(BufferSizeError, Error);

  /**
   * See receive(ScatterMessage &, GroupList &).
   *
   * @throw BufferSizeError
   * @throw Error
   */
  int receive(Message & message, GroupList & groups)
    SSRC_DECL_THROW(BufferSizeError, Error)
  {
    clear_message_parts();
    add_message_part(message);
    return receive(_scatter, groups);
  }

  /**
   * Same as receive(_scatter, groups), where _scatter is the internal
   * ScatterMessage.
   *
   * @throw BufferSizeError
   * @throw Error
   */
  int receive(GroupList & groups) SSRC_DECL_THROW(BufferSizeError, Error) {
    return receive(_scatter, groups);
  }

  /**
   * Same as receive(message, _groups), where _groups is the interal
   * GroupList.
   *
   * @throw BufferSizeError
   * @throw Error
   */
  int receive(Message & message) SSRC_DECL_THROW(BufferSizeError, Error) {
    return receive(message, _groups);
  }

  /**
   * Same as receive(message, _groups), where _groups is the interal
   * GroupList.
   *
   * @throw BufferSizeError
   * @throw Error
   */
  int receive(ScatterMessage & message)
    SSRC_DECL_THROW(BufferSizeError, Error)
  {
    return receive(message, _groups);
  }

  /**
   * Same as receive(_scatter, _groups), where _scatter and _groups
   * are the internal ScatterMessage and GroupList.
   *
   * @throw BufferSizeError
   * @throw Error
   */
  int receive() SSRC_DECL_THROW(BufferSizeError, Error) {
    return receive(_scatter, _groups);
  }

};

__END_NS_SSRC_SPREAD

#endif
