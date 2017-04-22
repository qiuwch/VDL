#!/usr/bin/env perl
#
#
# Copyright 2006 Savarese Software Research Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.savarese.com/software/ApacheLicense-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

use strict;
use Test::More tests => 3;
use ssrc::spread;

sub test_error {
  my $error = new ssrc::spread::Error($ssrc::spread::Error::ConnectionClosed);
  is($error->error(), $ssrc::spread::Error::ConnectionClosed); 
}

sub test_buffer_size_error {
  my $error =
      new ssrc::spread::BufferSizeError($ssrc::spread::Error::BufferTooShort,
                                        10);
  is($error->error(), $ssrc::spread::Error::BufferTooShort);
  is($error->size(), 10);
}

test_error();
test_buffer_size_error();
