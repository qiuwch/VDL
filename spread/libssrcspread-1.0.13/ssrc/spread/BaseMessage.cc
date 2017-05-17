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

#include <ssrc/spread/MembershipInfo.h>

__BEGIN_NS_SSRC_SPREAD

#ifdef LIBSSRCSPREAD_ENABLE_MEMBERSHIP_INFO

/**
 * Gets the vs_set members from a vs_set using the virtual
 * sp_get_vs_set_members method, so the proper SP_ call is used based
 * on whether or not the message is a scatter message.  On an
 * Error::BufferTooShort error, automatically resizes the member group
 * list and tries again
 */
void BaseMessage::get_vs_set_members(const Spread::vs_set_info *vs_set,
                                     GroupList *members,
                                     unsigned int offset) const
{
  int result;

  members->resize(members->capacity());

 try_again:
  result =
    sp_get_vs_set_members(vs_set, members->groups() + offset,
                          members->size() - offset);

  if(result == Error::BufferTooShort) {
    result = vs_set->num_members;
    if(result > 0) {
      members->resize(offset + result);
      goto try_again;
    } else
      members->resize(offset);
  } else if(result > 0)
    members->resize(offset + result);
  else
    members->resize(offset);
}

/**
 * Extracts the membership information contained in this message and
 * stores it in the supplied MembershipInfo object.  Only call this
 * method if the message is a membership message.
 *
 * <b>Warning:</b> This method is available only when compiled against
 * %Spread 4.x and greater.
 *
 * @param info A reference to a MembershipInfo that will store the membership
 * information.
 * @throw Error If the structure of the message or its service type does
 * not comprise a valid membership message.
 */
void BaseMessage::get_membership_info(MembershipInfo & info) const
  SSRC_DECL_THROW(Error)
{
  int result = sp_get_membership_info(&info._info);

  if(result <= 0)
    throw Error(result);

  info.set_service(service());

  get_vs_set_members(&info._info.my_vs_set, &info._local_members);

  if(info._info.num_vs_sets > 0) {
    detail::Buffer<Spread::vs_set_info> vs_sets(info._info.num_vs_sets);
    unsigned int index = 0;

    vs_sets.resize(info._info.num_vs_sets);
    result = sp_get_vs_sets_info(&vs_sets[0], vs_sets.size(), &index);

    if(result > 0) {

      // Just in case.
      if(static_cast<unsigned int>(result) != vs_sets.size())
        vs_sets.resize(result);

      info._non_local_members.clear();

      for(int i = 0; i < result; ++i) {
        if(static_cast<unsigned int>(i) != index)
          get_vs_set_members(&vs_sets[i], &info._non_local_members,
                             info._non_local_members.size());
      }

    } else
      throw Error(result);
  }
}

#endif

__END_NS_SSRC_SPREAD
