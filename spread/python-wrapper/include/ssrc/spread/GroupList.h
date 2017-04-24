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
 * This header defines the GroupList class.
 */

#ifndef __SSRC_SPREAD_GROUP_LIST_H
#define __SSRC_SPREAD_GROUP_LIST_H

#include <string>
#include <ostream>

#include <ssrc/spread/detail/Buffer.h>

// sp.h includes stddef.h, so we need to include it before sp.h in
// order to ensure it gets skipped while inside the Spread namespace.
#include <cstddef>

__BEGIN_NS_SPREAD_INCLUDE
# include <sp.h>
  /** This is an internal typedef not meant for use in end-user code. */
  typedef char group_type[MAX_GROUP_NAME];
__END_NS_SPREAD_INCLUDE

__BEGIN_NS_SSRC_SPREAD

using std::string;

enum {
  /**
   * Maximum number of characters in a private name.  This is
   * inconsistent with MaxSizeProcessName and MaxSizeGroupName
   * (which are max + 1), but it's how the %Spread Toolkit does it;
   * so we don't deviate, even though we'd rather they all be
   * consistently defined as maximum values.
   */
  MaxSizePrivateName = MAX_PRIVATE_NAME,
  /** Maximum number of characters in the name of a daemon process + 1. */
  MaxSizeProcessName = MAX_PROC_NAME,
  /** The maximum number of characters in a group name + 1. */
  MaxSizeGroupName = MAX_GROUP_NAME,
  /** The minimum value of a valid group name character. */
  MinValidGroupNameChar = 36,
  /** The maximum value of a valid group name character. */
  MaxValidGroupNameChar = 126,
  /** The value of the group name character separator. */
  GroupNameSeparatorChar = 35
};


/**
 * Splits a private group name into its private name and process name
 * components.  This functions assumes it is provided a valid private
 * group name, otherwise its behavior is undefined.
 *
 * @param private_group The private group name to split.
 * @return A std::pair<string,string> where the first element is the
 * private name component and the second element is the process name
 * component.
 */
inline
std::pair<string,string> split_private_group(const string & private_group) {
  string::size_type length = private_group.find(GroupNameSeparatorChar, 1) - 1;
  return std::pair<string,string>(string(private_group, 1, length),
                                  string(private_group, length + 2,
                                         private_group.size() - length - 2));
}

/**
 * GroupList is a container for %Spread group names.  You use it to
 * determine the destination of a message or ascertain membership
 * information.  A GroupList can be resized by its friend classes as
 * needed so that you don't have to pre-allocate a very large list or
 * handle short buffer errors.
 */
class GroupList {
private:
  struct group_type {
    Spread::group_type group;
  };

  typedef detail::Buffer<group_type> group_vector;

  group_vector _groups;

  const Spread::group_type *groups() const {
    return reinterpret_cast<const Spread::group_type *>(&_groups[0]);
  }

  Spread::group_type *groups() {
    return
      const_cast<Spread::group_type *>(reinterpret_cast<const Spread::group_type *>(&_groups[0]));
  }

  unsigned int capacity() const {
    return _groups.capacity();
  }

  void resize(const unsigned int size) {
    _groups.resize(size);
  }

public:

  /**
   * Creates an empty GroupList with the specified initial capacity.
   */
  explicit GroupList(const unsigned int capacity = 10) : _groups(capacity) { }

  /**
   * Appends a group name to the list.
   *
   * @param group The group name to add.
   */
  void add(const string & group) {
    int size;
    group_type gname;
    size = group.copy(gname.group, sizeof(Spread::group_type) - 1);
    gname.group[size] = 0;
    _groups.add(gname);
  }

  /**
   * Appends the contents another GroupList to this one.
   *
   * @param groups The GroupList to append.
   */
  void add(const GroupList & groups) {
    if(&groups != this) {
      unsigned int offset = size();
      resize(size() + groups.size());
      std::memcpy(GroupList::groups() + offset, groups.groups(),
                  groups.size()*sizeof(group_type));
    }
  }

  /**
   * Returns the group name at the specified index.  No bounds checking
   * is performed; it is the responsibility of the caller to ensure a
   * valid index is provided.
   *
   * @param index The index of the group name to return.
   * @return The group name at the specified index.
   */
  string group(const unsigned int index) const {
    return _groups[index].group;
  }

  /** Same as {@link #group group(index)}. */
  string operator[](const unsigned int index) const {
    return group(index);
  }

  /**
   * Assigns the value of another GroupList to this one.
   *
   * @param groups The GroupList to copy.
   * @return *this
   */
  GroupList & operator=(const GroupList & groups) {
    if(&groups != this) {
      resize(groups.size());
      std::memcpy(GroupList::groups(), groups.groups(),
                  size()*sizeof(group_type));
    }
    return *this;
  }

  /** Empties the list. */
  void clear() {
    _groups.clear();
  }

  /**
   * Returns the number of groups in the list.
   * @return The number of groups in the list.
   */
  unsigned int size() const {
    return _groups.size();
  }

private:
  friend class Mailbox;
  friend class BaseMessage;

  /**
   * Tests that two GroupLists contain the exact same number of groups
   * with the exact same values in the exact same order.  Use namespace
   * std::rel_ops to gain the != operator.
   *
   * @param groups1 The first GroupList in the comparison.
   * @param groups2 The second GroupList in the comparison.
   * @return true if the GroupLists contain the same groups in the
   * same order, false if not.
   */
  friend bool operator==(const GroupList & groups1,
                         const GroupList & groups2)
  {
    unsigned int size = groups1.size();

    if(size != groups2.size())
      return false;
    else
      while(size-- > 0) {
        if(std::strncmp(groups1.groups()[size], groups2.groups()[size],
                        MaxSizeGroupName))
          return false;
      }

    return true;
  }

  /**
   * Outputs the group names contained in the list&mdash;one per line.
   *
   * @param output The ostream to write to.
   * @param groups The GroupList to output.
   * @return The std::ostream output parameter.
   */
  friend std::ostream & operator<<(std::ostream & output,
                                   const GroupList & groups)
  {
    for(unsigned int i = 0; i < groups.size(); ++i)
      output << groups._groups[i].group << std::endl;
    return output;
  }
};

__END_NS_SSRC_SPREAD

#endif
