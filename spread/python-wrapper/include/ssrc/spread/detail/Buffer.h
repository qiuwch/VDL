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
 * This header defines the Buffer class.
 */

#ifndef __SSRC_SPREAD_DETAIL_BUFFER_H
#define __SSRC_SPREAD_DETAIL_BUFFER_H

#include <cstring>
#include <iterator>

#include <ssrc/libssrcspread-packages.h>

__BEGIN_NS_SSRC_SPREAD

namespace detail {

  /**
   * Buffer defines a limited set of operations for managing a memory
   * buffer.  It is intended only for internal use by the library.
   * Please do not subclass Buffer, but do examine its public methods
   * that are inherited by its subclasses.
   *
   * We define Buffer instead of using std::vector because we
   * want to avoid the overhead of std::vector::clear() and
   * std::vector::resize(), both of which cause unused data elements
   * to be erased.  The buffers used by the library may be resized
   * often (potentially on every send and receive).  We are
   * unconcerned with erasing (or initializing) unused elements
   * because we read and write to the buffer's raw memory.  Therefore,
   * we merely require an index that tracks the size of the buffer.
   */
  template<typename type>
  class Buffer {

    unsigned int _capacity;
    unsigned int _size;
    type * _data;
    
  public:
    typedef type value_type;
    typedef value_type & reference;
    typedef const reference const_reference;
    typedef value_type* pointer;
    typedef const value_type* const_pointer;
    typedef pointer iterator;
    typedef const_pointer const_iterator;
    typedef std::reverse_iterator<iterator> reverse_iterator;
    typedef std::reverse_iterator<const_iterator> const_reverse_iterator;

    /**
     * Creates a buffer with the specified capacity and sets its size to zero.
     *
     * @param capacity The initial capacity of the buffer.
     */
    explicit Buffer(const unsigned int capacity) :
      _capacity(capacity), _size(0), _data(new value_type[capacity])
    { }

    /**
     * Deallocates all memory used by the buffer.
     */
    ~Buffer() { delete[] _data; }

    /**
     * Returns the maximum number of elements that can be written to the
     * buffer without reallocating memory.
     *
     * @return The buffer capacity.
     */
    unsigned int capacity() const {
      return _capacity;
    }

    /**
     * Returns the element at the specified index.
     *
     * @param index The index of the element to retrieve.
     * @return The element at the specified index.
     */
    reference operator[](const unsigned int index) {
      return _data[index];
    }

    /**
     * Returns the element at the specified index.
     *
     * @param index The index of the element to retrieve.
     * @return The element at the specified index.
     */
    const_reference operator[](const unsigned int index) const {
      return _data[index];
    }

    /**
     * Returns an iterator pointing to the first element in the buffer.
     *
     * @return An iterator pointing to the first element in the buffer.
     */
    iterator begin() {
      return _data;
    }

    /**
     * Returns a const iterator pointing to the first element in the buffer.
     *
     * @return A const iterator pointing to the first element in the buffer.
     */
    const_iterator begin() const {
      return _data;
    }

    /**
     * Returns an iterator pointing to one position beyond the last element
     * in the buffer.
     *
     * @return An iterator pointing to one position beyond the last element
     *         in the buffer.
     */
    iterator end() {
      return (_data + _size);
    }

    /**
     * Returns an iterator pointing to one position beyond the last element
     * in the buffer.
     *
     * @return An iterator pointing to one position beyond the last element
     *         in the buffer.
     */
    const_iterator end() const {
      return (_data + _size);
    }

    /**
     * Returns reverse_iterator(end()).
     *
     * @return reverse_iterator(end()).
     */
    reverse_iterator rbegin() {
      return reverse_iterator(end());
    }

    /**
     * Returns const_reverse_iterator(end()).
     *
     * @return const_reverse_iterator(end()).
     */
    const_reverse_iterator rbegin() const {
      return const_reverse_iterator(end());
    }

    /**
     * Returns reverse_iterator(begin()).
     *
     * @return reverse_iterator(begin()).
     */
    reverse_iterator rend() {
      return reverse_iterator(begin());
    }

    /**
     * Returns const_reverse_iterator(begin()).
     *
     * @return const_reverse_iterator(begin()).
     */
    const_reverse_iterator rend() const {
      return const_reverse_iterator(begin());
    }

    /**
     * Increases the buffer capacity to the specified size.  If the
     * new size is less than or equal to the buffer capacity, no
     * action is performed.  If the size is greater than the capacity,
     * new memory is reserved, increasing the capacity while
     * preserving the existing buffer contents.
     *
     * @param capacity The new buffer capacity.
     */
    void reserve(const unsigned int capacity) {
      if(capacity > _capacity) {
        pointer new_data = new value_type[capacity];
        std::memcpy(new_data, _data, _size*sizeof(value_type));
        delete[] _data;
        _data = new_data;
        _capacity = capacity;
      }
    }

    /**
     * Resizes the buffer to the specified size.  If the new size is
     * less than or equal to the buffer capacity, the size is simply
     * set to the new value.  If the size is greater than the
     * capacity, new memory is reserved&mdash;preserving the existing
     * buffer contents&mdash;before setting the size to the new value.
     *
     * @param size The new buffer size.
     */
    void resize(const unsigned int size) {
      reserve(size);
      _size = size;
    }

    /**
     * Returns the number of elements contained in the buffer.
     * @return The number of elements contained in the buffer.
     */
    unsigned int size() const {
      return _size;
    }

    /** Same as {@link #resize resize(0)}. */
    void clear() {
      resize(0);
    }

    /**
     * Appends a value to the end of the buffer and increments the
     * size by one.  If the buffer is at full capacity, its capacity
     * is increased to be able to hold more data.  Currently, this is
     * done by doubling the current capacity, but you should not rely
     * on that behavior.
     *
     * @param value The value to append to the buffer.
     */
    void add(const type & value) {
      if(capacity() <= _size) {
        reserve(_size << 1);
      }
      _data[_size++] = value;
    }
  };
}

__END_NS_SSRC_SPREAD

#endif
