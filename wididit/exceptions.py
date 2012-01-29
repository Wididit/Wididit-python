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

from wididit.i18n import _

class WididitException(Exception):
    """Base exception for Wididit library."""
    pass

class ServerException(WididitException):
    """Base exception for server errors."""
    pass

class Unreachable(ServerException):
    """Server cannot be reached."""
    def __init__(self, hostname):
        super(Unreachable, self).__init__(
                _('Server %(hostname)s cannot be reached.') %
                {'hostname': hostname})

class NotFound(ServerException):
    """Object does not exist."""
    def __init__(self, object_):
        super(NotFound, self).__init__(
                _('%(object)s cannot be found.') % {'object': object_})

class Forbidden(ServerException):
    """Action not authorized."""
    def __init__(self, action):
        super(Forbidden, self).__init__(
                _('You are not authorized to %(action)s.') % {'action': action})


class PeopleException(WididitException):
    """Base exception for people errors."""
    pass

class PeopleNotInstanciable(PeopleException):
    """The people instance cannot be constructed."""
    pass
