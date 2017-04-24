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
 * This header defines the MembershipInfo class.
 */

#ifndef __SSRC_SPREAD_MEMBERSHIP_INFO_H
#define __SSRC_SPREAD_MEMBERSHIP_INFO_H

#include <ssrc/spread/BaseMessage.h>

__BEGIN_NS_SSRC_SPREAD

#ifdef LIBSSRCSPREAD_ENABLE_MEMBERSHIP_INFO

/**
 * MembershipInfo stores information about group membership messages.
 * You can populate a MembershipInfo instance with information about a
 * membership message by invoking BaseMessage::get_membership_info on
 * a Message or ScatterMessage containing a membership message.
 *
 * <b>Warning:</b> This class is available only when compiled against
 * %Spread 4.x and greater.
 */
class MembershipInfo {
  friend void BaseMessage::get_membership_info(MembershipInfo & info) const;

  BaseMessage::service_type _service_type;
  Spread::membership_info _info;
  GroupList _local_members, _non_local_members;

  void set_service(const BaseMessage::service_type service) {
    _service_type = service;
  }

public:

  /**
   * Returns the service type of the message.
   * @return The service type of the message.
   */
  BaseMessage::service_type service() const {
    return _service_type;
  }

  /**
   * Returns a list of the private group names from the local segment
   * that remained in the group after a change in membership caused by
   * a network partition.  For join/leave/disconnect changes, the list
   * contains only the changed member (you should call
   * changed_member() instead).  This is the equivalent of the group
   * information from the my_vs_set vs_set_info member from the
   * membership_info struct in the C API.
   *
   * @param members A reference to the GroupList that should store the
   * local members.
   */
  void get_local_members(GroupList & members) const {
    members = _local_members;
  }
  /**
   * Returns a list of the private group names from all the segments
   * except the local segment that belong to the group after a change
   * in membership caused by a network partition.  For
   * join/leave/disconnect changes, the list will be empty.
   *
   * @param members A reference to the GroupList that should store the
   * non-local members.
   */
  void get_non_local_members(GroupList & members) const {
    members = _non_local_members;
  }

  /**
   * Returns a list of the private group names from all the segments
   * that belong to the group after a change in membership caused by a
   * network partition.  For join/leave/disconnect changes, the list
   * contains only the changed member (you should call
   * changed_member() instead).  This is the equivalent of the group
   * information from the C API vs_set_info data structure, but
   * the group ordering may differ.
   *
   * @param members A reference to the GroupList that should store all
   * of the members.
   */
  void get_all_members(GroupList & members) const {
    members.clear();
    members.add(_local_members);
    members.add(_non_local_members);
  }

  /**
   * Tests if the group ids of the MembrshipInfo objects are the same.
   *
   * @param info The MembershipInfo object whose group id is to to compare.
   * @return true if the group ids are equal, false if not.
   */
  bool equal_group_ids(const MembershipInfo & info) const {
    return (Spread::SP_equal_group_ids(_info.gid, info._info.gid) != 0);
  }

  /**
   * Returns the private group name of member who joined, left, or
   * disconnected.  Only valid if caused_by_join, leave, or disconnect
   * are true.
   * @return The private group name of member who joined, left, or
   * disconnected.
   */
  string changed_member() const {
    return _info.changed_member;
  }

  /**
   * Returns true if the message is a regular membership message, false if not.
   * @return true if the message is a regular membership message, false if not.
   */
  bool is_regular_membership() const {
    return Is_reg_memb_mess(service());
  }

  /**
   * Returns true if the message is a transitional membership message,
   * false if not.
   * @return true if the message is a transitional membership message,
   * false if not.
   */
  bool is_transition() const {
    return Is_transition_mess(service());
  }

  /**
   * Returns true if the message is a self-leave membership message,
   * false if not.
   * @return true if the message is a self-leave membership message,
   * false if not.
   */
  bool is_self_leave() const {
    return Is_self_leave(service());
  }

  /**
   * Returns true if the membership message was caused by a group
   * join, false if not.
   * @return true if the membership message was caused by a group
   * join, false if not.
   */
  bool caused_by_join() const {
    return Is_caused_join_mess(service());
  }

  /**
   * Returns true if the membership message was caused by a group
   * leave, false if not.
   * @return true if the membership message was caused by a group
   * leave, false if not.
   */
  bool caused_by_leave() const {
    return Is_caused_leave_mess(service());
  }

  /**
   * Returns true if the membership message was caused by a client
   * disconnect, false if not.
   * @return true if the membership message was caused by a client
   * disconnect, false if not.
   */
  bool caused_by_disconnect() const {
    return Is_caused_disconnect_mess(service());
  }

  /**
   * Returns true if the membership message was caused by a network
   * partition, false if not.
   * @return true if the membership message was caused by a network
   * partition, false if not.
   */
  bool caused_by_network() const {
    return Is_caused_network_mess(service());
  }
};

#endif

__END_NS_SSRC_SPREAD

#endif
