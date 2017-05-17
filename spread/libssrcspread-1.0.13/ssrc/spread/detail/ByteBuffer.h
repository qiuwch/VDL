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
 * This header defines the ByteBuffer class.
 */

#ifndef __SSRC_SPREAD_DETAIL_BYTE_BUFFER_H
#define __SSRC_SPREAD_DETAIL_BYTE_BUFFER_H

#include <ssrc/spread/detail/Buffer.h>

__BEGIN_NS_SSRC_SPREAD

namespace detail {

  /**
   * ByteBuffer provides the ability to write and read bytes to and
   * from a buffer and reuse the buffer for input or output.  The
   * class is not meant to be subclassed by library users, but it
   * needs to be documented publicly so you can use its methods in its
   * subclasses.
   *
   * ByteBuffer maintains a current offset into the buffer where reads
   * and writes will start.  The offset is not updated when the buffer
   * is resized.
   */
  class ByteBuffer : public detail::Buffer<char> {
    typedef detail::Buffer<char> super;

    unsigned int _offset;

  public:

    /**
     * Creates a buffer with the specified capacity and sets its size
     * and offset to zero.
     *
     * @param capacity The initial capacity of the buffer.
     */
    explicit ByteBuffer(const unsigned int capacity) : super(0), _offset(0) {
      super::reserve(capacity);
    }

    /**
     * Creates a copy of a ByteBuffer, including its contents, its
     * read/write position, size, and its capacity.
     *
     * @param buffer The ByteBuffer to copy.
     */
    ByteBuffer(const ByteBuffer & buffer) : super(0), _offset(0) {
      super::reserve(buffer.capacity());
      write(&buffer[0], buffer.size());
      seek(buffer.offset());
    }

    /**
     * Copies the contents of a ByteBuffer, its read/write position, and
     * its size, but does not necessarily copy its capacity.
     *
     * @param buffer The ByteBuffer to copy.
     * @return *this
     */
    ByteBuffer & operator=(const ByteBuffer & buffer) {
      if(&buffer != this) {
        clear();
        write(&buffer[0], buffer.size());
        seek(buffer.offset());
      }
      return *this;
    }

    /**
     * Returns the current read/write position.
     *
     * @return The current read/write position.
     */
    unsigned int offset() const {
      return _offset;
    }

    /**
     * Sets the read/write position to the specified value if the
     * value is less than or equal to the size of the buffer.
     * Otherwise, the current offset is left unchanged.
     *
     * @param offset The buffer offset of the new read/write position.
     * @return The new read/write position.
     */
    unsigned int seek(const unsigned int offset) {
      if(offset <= size())
        _offset = offset;
      return _offset;
    }

    /** Same as {@link #seek seek(0)}. */
    void rewind() {
      seek(0);
    }

    /**
     * Rewinds the read/write position befor resizing the buffer to zero.
     */
    void clear() {
      rewind();
      resize(0);
    }

    /**
     * Writes the specified number of bytes from the provided data into
     * the buffer at the current read/write position.  If the buffer is
     * not large enough to hold the data, it is resized automatically to
     * the current offset plus the size of the data to be written.
     * After writing the data, the read/write position is incremented by
     * the size of the data written.
     *
     * @param data A pointer to the data to be written.
     * @param size The number of bytes to write.
     */
    void write(const void *data, const unsigned int size) {
      unsigned int total = _offset + size;

      if(total > ByteBuffer::size())
        resize(total);

      std::memcpy(&(this->operator[](_offset)), data, size);

      _offset = total;
    }

    /**
     * Reads the specified number of bytes from the buffer into the
     * provided destination starting from the current read/write
     * position.  If the number of bytes to be read would result in
     * running off the end of the buffer, the read is truncated at the
     * end of the buffer.
     *
     * @param data A pointer to the read destination.
     * @param size The number of bytes to read.
     * @return The number of bytes read.
     */
    unsigned int read(void *data, unsigned int size) {
      if(_offset >= ByteBuffer::size())
        return 0;

      unsigned int total = _offset + size;

      if(total > ByteBuffer::size()) {
        total = ByteBuffer::size();
        size = total - _offset;
      }

      std::memcpy(data, &(this->operator[](_offset)), size);

      _offset = total;

      return size;
    }

  };

}

__END_NS_SSRC_SPREAD

#endif
