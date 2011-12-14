# Copyright (C) 2011, Valentin Lorentz
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

MAX_HOSTNAME_LENGTH = 1023
MIN_USERNAME_LENGTH = 3
MAX_USERNAME_LENGTH = 255
MAX_TAG_LENGTH = 255
MAX_GENERATOR_LENGTH = 1024
MAX_TITLE_LENGTH = 4096
MAX_SUBTITLE_LENGTH = 4096

USERNAME_REGEXP = '[a-z0-9_-]{%(min)i,%(max)i}' % {
        'min': MIN_USERNAME_LENGTH,
        'max': MAX_USERNAME_LENGTH,
        }
USERMASK_REGEXP = USERNAME_REGEXP + '@.*'
USER_MIX_REGEXP = USERNAME_REGEXP + '(@.*)?'
"""A regexp that allows both :ref:`wididit.constants.USERNAME_REGEXP` and
:ref:`wididit_constants.USERMASK_REGEXP`."""
