/* Copyright 2006-2011 Savarese Software Research Corporation
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
 * This header contains documentation only and is not part of the
 * actual source code.
 */

#include <ssrc/libssrcspread.h>

__BEGIN_NS_SSRC_SPREAD

/**
@mainpage

For instructions on building the software and information about the
Lua, Perl, Python, and Ruby bindings, see:
- @subpage build
- @subpage script_notes

@section licensing Licensing

Ssrc C++/Lua/Perl/Python/Ruby Bindings for %Spread is Copyright 2006-2017 by
<a href="http://www.savarese.com/">Savarese Software Research
Corporation</a> and licensed under the 
<a href="http://www.savarese.com/software/ApacheLicense-2.0">Apache
License 2.0</a> as described in the files accompanying the source
distribution:
  - LICENSE
  - NOTICE

This product uses software developed by %Spread Concepts LLC for
use in the %Spread toolkit. For more information about %Spread, see
%http://www.spread.org/.

@section contact Contact

For inquiries about the software see http://www.savarese.com/contact.html

@section overview Overview

Ssrc C++/Lua/Perl/Python/Ruby Bindings for %Spread provides group communication
classes that wrap the %Spread Toolkit's C API.  Even though you can
use the %Spread C API directly in C++ code, error handling and data
structure manipulation can be cumbersome.
Ssrc C++/Lua/Perl/Python/Ruby Bindings for %Spread takes some of that pain away
by providing automatic operation retries, automatic resizing of
message and group buffers, exceptions for true errors, and safe
connection management via the "resource acquisition is initialization"
idiom.

To use the library add:
<pre>\#include <ssrc/libssrcspread.h></pre>
or
<pre>\#include <ssrc/spread.h></pre>
to the top of your C++ source file.  The first form will pick up any
future additions to the library that fall into a namespace other than
ssrc::spread (e.g., possibly ssrc::fl_spread).  The second form will pick
up only the ssrc::spread namespace.  At the moment, there are no
additional namespaces, so they are currently equivalent.

The main entry point to using the API is the Mailbox class, which
is used to establish a connection with the %Spread daemon,
join/leave groups, and send/receive messages.

@section notes Notes

Knowledge of the %Spread C API is required to make use of the
Ssrc C++/Lua/Perl/Python/Ruby Bindings for %Spread.  This documentation does not
attempt to explain how to use %Spread or how it works.  It documents
only the C++ API.

Ssrc C++/Lua/Perl/Python/Ruby Bindings for %Spread currently wraps only the SP_
functions from the spread-core library.  The flush FL_ functions are
not wrapped.  Given the similarity of the SP_ and FL_ functions, a
future version of the library could use generic programming techniques
to wrap both and avoid code duplication.  Such a change may break
compatibility with earlier versions of the library.  If there is user
demand to wrap the view synchrony flush API or a patch is submitted,
we'll try to do this for a 2.0 release.

@page build Compiling and Installation Instructions

@section dependencies Dependencies

Ssrc C++/Lua/Perl/Python/Ruby Bindings for %Spread is not a standalone library.
You must first install and configure the %Spread Toolkit from %Spread
Concepts LLC before you can compile programs with libssrcspread.  Also,
you must link against %Spread as well as Ssrc C++/Lua/Perl/Python/Ruby Bindings
for %Spread.

Prior to version 0.7.4, only %Spread Toolkit version 4.x was
supported.  Starting with version 0.7.4, %Spread Toolkit version
3.17.3 is also supported.  However, MembershipInfo,
Error::NetErrorOnSession, and Mailbox::kill() are removed from the API
when compiling against version 3.17.3.

At the moment, Ssrc C++/Lua/Perl/Python/Ruby Bindings for %Spread
depends on the GNU development tool chain (g++, gmake, autoconf,
automake, and libtool).  To compile on Win32 platforms you will need a
GNU development environment such as Cygwin or MinGW.  The software has
been tested on Linux 32/64-bit (2.6.x series kernel), FreeBSD 8.1,
Solaris 10 32/64-bit, and Mac OS X 10.6.7.

The unit tests require Boost (www.boost.org) to compile
and run.  Generation of test code coverage data requires lcov
(ltp.sourceforge.net/coverage/lcov.php).  Generation of documentation
requires doxygen (www.doxygen.org).  None of these packages is
required to compile the library.

@section compiling Compiling

Run the configure script to generate the Makefiles.
<pre>  configure --help</pre>
will list the configuration options.  If the %Spread C API headers
and libraries are not installed in a default system location, you
will have to tell configure how to find them with:
<pre>  configure --with-spread=PATHNAME</pre>

Also, you may decide to use the <code>--disable-namespace-versioning</code>
option to avoid having to recompile dynamically linked programs after
upgrading the library.

To install:
<pre>  make install</pre>

If Doxygen is available on your system, you can generate API documentation
with:
<pre>  make apidocs</pre>

If Boost is available on your system, you can compile and run the unit
tests with:
<pre>  make test</pre>

If lcov is available on your system in addition to Boost, then you can
generate the code coverage data with:
<pre>  make coverage</pre>

@section bindings Lua, Perl, Python, and Ruby Bindings

The Lua, Perl, Python, and Ruby bindings are built using SWIG (www.swig.org).
SWIG is detected automatically.  If it cannot be found, you can
specify its location with:
<pre>  configure --with-swig=path</pre>

The Lua binding is built if lua is detected on your system.
The Perl5 binding is built if perl is detected on your system.
The Python binding is built if python is detected on your system,
and the Ruby binding is built if ruby is detected on your system.

You can change the installation directory of the Lua binding with:
<pre>  configure --with-lua-sitedir=path</pre>
You can change the installation directory of the Perl binding with:
<pre>  configure --with-perl-sitedir=path</pre>
You can change the installation directory of the Ruby binding with:
<pre>  configure --with-ruby-sitedir=path</pre>
Otherwise, the Lua, Perl, and Ruby bindings are installed relative
to the system-default Ruby and Perl installation trees.

The Python binding currently is installed relative to the
installation prefix.  If you want to install it somewhere else, you
will have to copy the files manually or run the setup.py script
in the <code>swig/python</code> subdirectory as follows:
<pre>  setup.py install --prefix=path</pre>

If you use custom installation locations for the modules, you can access
them from your scripts by adding the directory containing the
<code>ssrc</code> module for each language to your <code>PERL5LIB</code>,
<code>PYTHONPATH</code>, and <code>RUBYLIB</code> environment variables.
The <code>LUA_CPATH</code> environment variable may have to point to the actual
_spread.so dynamic shared object instead of the directory where it is stored and
the <code>LUA_PATH</code> environment variable may have to be set as well in
order to find ssrc/spread.lua.  The Ssrc C++/Lua/Perl/Python/Ruby Bindings
for %Spread C++ shared library and the %Spread C shared library must also be
available (e.g., via <code>LD_LIBRARY_PATH</code> or a default system
library location).

@subsection problems Compilation Problems

You may run into problems compiling the Ruby binding with the GNU
compiler (currently the only one supported by the build system).  The
GNU <code>&lt;unistd.h&gt;</code> header defines
<code>eaccess()</code> as throwing an exception, but the Ruby
<code>intern.h</code> header does not (at least for versions 1.8.4 and 1.8.5).
This difference produces a compiler error.  To work around this problem
you can modify the <code>eaccess</code> declaration in
<code>intern.h</code> to look as follows:
@verbatim
 \#ifndef __USE_GNU
 int eaccess _((const char*, int));
 \#endif
@endverbatim

Finally, these bindings have been tested and verified with SWIG 2.0.3
Lua 5.1.4, Perl 5.12.3, Python 3.2, and Ruby 1.9.2, but may work with other
versions.

@subsection bit64_problems 64-bit Compilation Problems

You may also run into problems compiling any of the bindings on 64-bit
systems if you are not careful with your compilation options and scripting
environment.  If you are not using a system-supplied compiler and are instead
using a custom version of GCC, you may have to use
@verbatim
LDFLAGS="-m64 -shared-libgcc -Wl,-m,elf_x86_64"
@endverbatim
Also, you must ensure that the binding language and %Spread libraries are
also compiled with the same 64-bit options as well as <code>-fPIC</code>
in <code>CFLAGS</code>.  The libssrcspread configure script will
automatically add <code>-fPIC</code> to <code>CXXFLAGS</code>.

The %Spread Toolkit will not function properly on some 64-bit systems.
Although it may work properly on Linux, it will fail on FreeBSD and Solaris
without the following patch (created against version 4.1.0):
<a href="spread-4.1.0-64-bit.patch" title="64-bit patch for Spread 4.1.0">spread-4.1.0-64-bit.patch</a>.

@verbinclude spread-4.1.0-64-bit.patch

@page script_notes Lua/Perl/Python/Ruby API Differences

The Lua, Perl, Python, and Ruby bindings use the same naming scheme as the C++
API in almost every case.  No attempt has been made to customize
the API to the idioms of the respective scripting languages.  This
allows you to use the C++ API documentation for all environments.
However, a few differences are forced upon the API by the
languages.  See the unit tests in  <code>tests/swig/lua</code>,
<code>tests/swig/perl</code>, <code>tests/swig/python</code>, and
<code>tests/swig/ruby</code> for usage examples.

@section lua_diff Lua Differences

- <code>\#include &lt;ssrc/spread.h&gt;</code> becomes
  <code>require("ssrc.spread")</code>
- ssrc::spread::foo becomes ssrc.spread.foo
- Static constants and enums that are class members cannot be accessed via
  the dot operator.  Instead they are mapped to the class name followed
  by an underscore followed by the constant name.  For example,
  <code>ssrc::spread::BaseMessage::SelfDiscard</code> becomes
  <code>ssrc.spread.BaseMessage_SelfDiscard</code>.
- When you reference class constants, you must reference the
  class in which they are defined.  For example, use
  <code>ssrc.spread.BaseMessage_SelfDiscard</code> instead of
  <code>ssrc.spread.Message_SelfDiscard</code>
- There are no bitwise logical operators in Lua.  Therefore, you cannot
  use bitmasks.  Instead of
  <code>ssrc::spread::BaseMessage::Reliable | ssrc::spread::BaseMessage::SelfDiscard</code>
  use <code>ssrc.spread.BaseMessage_ReliableSelfDiscard</code>.
- Error and BufferSizeError cannot be caught in Lua, but you can prevent
  your program from exiting by using <code>pcall</code>.  For example, the
  Lua unit tests do the following:
@verbatim
  function test_error()
    local succeeded, message = pcall(mbox.join, mbox, "####");
    assert(not succeeded)
  end
@endverbatim

@section perl_diff Perl Differences

- <code>\#include &lt;ssrc/spread.h&gt;</code> becomes
  <code>use ssrc::spread;</code>
- ssrc::spread::foo becomes ssrc::spread::foo
- split_private_group() is not implemented
- When you reference class constants, you must reference the
  class in which they are defined.  For example, use
  <code>$ssrc::spread::BaseMessage::SelfDiscard</code> instead of
  <code>$ssrc::spread::Message::SelfDiscard</code>
- Error and BufferSizeError can be caught in Perl only via the use of
  <code>eval</code>, which makes the exception available via the
  <code>$\@</code> special variable.  For example, the Perl unit tests do
  the following:
@verbatim
  sub test_error {
    eval { $mbox->join("####"); };
    is($@->error(), $ssrc::spread::Error::IllegalGroup);
  }
@endverbatim

@section py_diff Python Differences
- <code>\#include &lt;ssrc/spread.h&gt;</code> becomes
  <code>import ssrc.spread</code>
- ssrc::spread::foo becomes ssrc.spread.foo
- Error::print() becomes Error._print()

@section rb_diff Ruby Differences

- <code>\#include &lt;ssrc/spread.h&gt;</code> becomes
  <code>require 'ssrc/spread'</code>
- ssrc::spread::foo becomes Ssrc::Spread::foo

@section shared_diff Shared Differences

- The %Spread C API is not available in the %Spread namespace.

- split_private_group() (not implemented in Perl) expects only the
  private group name as a parameter and returns an array (Ruby) or
  tuple (Python).  For example:
@verbatim
  private_name, proc_name = ssrc.spread.split_private_group("#foo#bar")
  private_name == "foo" # This expression evaluates to True
  proc_name == "bar" # This expression evaluates to True
@endverbatim
  In Lua split_private_group() returns a C++-style pair with .first
  and .second members, just like the C++ API.<br />
  You don't really need split_private_group() in the scripting
  environment because the same result can be obtained via string
  manipulation functions or regular expressions.
- operator=() becomes copy()<br />
  For example:
@verbatim
  g1 = ssrc.spread.GroupList()
  g2 = ssrc.spread.GroupList()
  g1.add("foo")
  g2.copy(g1)
  g2.group(0) == "foo" # This expression evaluates to True.
@endverbatim
- operator[] is unavailable.  Use the corresponding accessor method
  instead.  For example, use GroupList::group.
- Messages are treated as strings.  If there is user demand, functions
  for creating raw memory buffers can be exported into the scripting
  environment.  But for now, we feel it is best to serialize script
  objects into strings (e.g., with Python pickling) or create script
  bindings of your C++ data types that are sent as messages instead of
  trying to manipulate memory allocation in the scripting environment.
- Message::read returns a string and Message::write expects a
  string parameter.  Message::read expects the maximum number of
  bytes to read as a parameter.  For example:
@verbatim
  m = ssrc.spread.Message()
  m.write("foobar")
  m.rewind()
  s = m.read(m.size())
  "foobar" == s # This expression evaluates to True.
@endverbatim
- The C++ versions of Message::read and Message::write are
  available as <code>readn</code> and <code>writen</code>.  Note,
  that <code>readn</code> is dangerous (e.g., strings are
  supposed to be immutable in Python) and should be avoided unless you
  know exactly what you're doing.
- ScatterMessage::add(const void *, unsigned int) and
  Mailbox::add_message_part(const void *, unsigned int) expect only a
  string as a parameter (same as the Message::write mapping).  You
  should avoid using this form of the method for receives.  Instead,
  use Message parts for receives, or you may overwrite script data
  structures in unpredictable ways.

@section considerations Additional Considerations

The Mailbox class uses the C++ idiom of resource acquisition is
initialization.  Therefore, no disconnect method is exposed and the
disconnect happens in the destructor.  In a garbage-collected
scripting language, this means the disconnect may not happen at a
predictable point when you stop using the object.  You can invoke
Mailbox::kill to free the file descriptor immediately, but don't
continue to use the object afterward.

In order to specify a connection timeout, you may use the
Timeout class or you may specify a timeout in seconds with a single
integer.  For example, to specify a connection timeout of 3 seconds
in Python, you could use:
@verbatim
mbox = ssrc.spread.Mailbox("4803@localhost", "", True, ssrc.spread.Timeout(3));@endverbatim
or:
@verbatim
mbox = ssrc.spread.Mailbox("4803@localhost", "", True, 3);@endverbatim

You can't access the contents of a Message directly via
<code>&Message[0]</code> as in C++.  Instead, you always have to read
and write the contents using Message::read and
Message::write.  Because messages are treated as strings in the
script environment, your data shouldn't contain null/0 characters.
For example, if you write two strings to a message in a row and read
them back into one string, you'll find that the result is treated as
only the first string because of the null termination.  For example:
@verbatim
m = ssrc.spread.Message()
m.write("foo")
m.write("bar")
m.rewind()
s = m.read(m.size())
"foo" == s # This expression evaluates to True.
"foobar" == s # This expression evaluates to False.
m.rewind()
s1 = m.read(4)
s2 = m.read(4)
"foo" == s1 # This expression evaluates to True.
"bar" == s2 # This expression evaluates to True.
@endverbatim
As long as you use the script environment's object serialization
mechanisms, you shouldn't run into any problems in this regard.

Don't add raw data parts (things that are not of type Message) to
ScatterMessage::add or Mailbox::add_message_part if
they will be garbage-collected before a send.  For example:
@verbatim
s = "foo"
mbox.add_message_part(s)
s = None # Don't do this before the send or you may segfault!
mbox.send()
@endverbatim

*/

__END_NS_SSRC_SPREAD
