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

import requests

from wididit.i18n import _
from wididit import Server
from wididit import exceptions
from wididit.wididitobject import WididitObject

class People(WididitObject):
    """Representation of a Wididit user.

    :param username: The username of the user.
    :param hostname: The hostname of the server where the user is registered.
    """
    def __new__(cls, username, hostname, *args, **kwargs):
        return super(People, cls).__new__(cls, username, hostname)

    def __init__(self, username, hostname, password=None, connect=False):
        super(People, self).__init__()
        self._username = username
        self._password = password
        if connect:
            self._server = Server(hostname, self)
        else:
            self._server = Server(hostname)
        self.sync()

    def __eq__(self, other):
        return other is self

    def sync(self):
        """Update the state of this object.

        This method updates attributes of this object according to server, but
        also discards all modifications you made without saving it.
        However, all modifications are saved by default."""
        response = self.server.get(self.api_path)
        if response.status_code != requests.codes.ok:
            raise exceptions.ServerException(response.status_code)
        response = self.server.unserialize(response.content)
        self._biography = response['biography']

    @property
    def username(self):
        """The username of the user."""
        return self._username

    @property
    def server(self):
        """The Server instance of the server where the user is registered."""
        return self._server

    @property
    def userid(self):
        """The unique representation of the user across the universe."""
        return '%s@%s' % (self.username, self.server.hostname)

    @property
    def api_path(self):
        """The path to this user in the API."""
        return '/people/%s/' % self.userid

    def get_password(self):
        return self._password
    def set_password(self, value):
        response = self.server.put(self.api_path, data={'password': value})
        if response.status_code == requests.codes.forbidden:
            raise exceptions.Forbidden(_('change the password'))
        elif response.status_code != requests.codes.ok:
            raise exceptions.ServerException(response.status_code)
        self._password = value
    password = property(get_password, set_password,
            'The password of the user.')

    def get_biography(self):
        return self._biography
    def set_biography(self, value):
        response = self.server.put(self.api_path, data={
            'username': self.username,
            'biography': value
            })
        if response.status_code == requests.codes.forbidden:
            raise exceptions.Forbidden(_('change the biography'))
        elif response.status_code == requests.codes.unauthorized:
            raise exceptions.Forbidden(_('change the biography'))
        elif response.status_code != requests.codes.ok:
            raise exceptions.ServerException(response.status_code)
        self._biography = value
    biography = property(get_biography, set_biography,
            'The biography of the user.')
