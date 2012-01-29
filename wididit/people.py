# Copyright (C) 2011-2012, Valentin Lorentz
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

from wididit import utils
from wididit.i18n import _
from wididit import Server
from wididit import exceptions
from wididit.wididitobject import WididitObject

class People(WididitObject):
    """Representation of a Wididit user.

    :param username: The username of the user.
    :param hostname: The hostname of the server where the user is registered.
    :param password: An optionnal parameter used if you want to connect.
    :param email: The email of the user. Used only if `register` is True.
    :param connect: Determines whether or not you will connect to the server
                    as this user.
    :param register: Determines whether or not we will create this user in
                    the server database.
    """
    def __new__(cls, username, hostname, *args, **kwargs):
        assert None not in (username, hostname)
        return super(People, cls).__new__(cls, username, hostname)

    def __init__(self, username, hostname, password=None, email=None,
            connect=False, register=False):
        super(People, self).__init__()
        self._username = username
        self._password = password
        if connect:
            self._server = Server(hostname, self)
        else:
            self._server = Server(hostname)
        if register:
            if email is None:
                raise AttributeError('email cannot be empty if registering.')
            if password is None:
                raise AttributeError('password cannot be empty if registering.')
            response = self.server.post('/people/', data={
                'username': self.username,
                'password': self.password,
                'email': email,
                })
            if response.status_code != requests.codes.created:
                raise exceptions.ServerException(response.status_code)

        self.sync()

    @staticmethod
    def from_anything(data):
        """Return a People instance from any supported representation.

        Supported representation are People instances, userid strings,
        (username, hostname) tuples, and dictionnaries from server reply.

        :param data: A representation of a People object.
        """
        if isinstance(data, People):
            return data
        elif isinstance(data, str) or isinstance(data, unicode):
            try:
                username, hostname = utils.userid2tuple(data)
            except ValueError:
                raise exceptions.PeopleNotInstanciable(
                        _('hostname is missing.'))
            return People(username, hostname)
        elif isinstance(data, tuple) and len(data) == 2:
            return People(*data)
        elif isinstance(data, dict) and 'username' in data and \
                'server' in data and isinstance(data['server'], dict) and \
                'hostname' in data['server']:
            return People(data['username'], data['server']['hostname'])
        else:
            raise ValueError('Invalid representation of People object: %r' %
                    data)

    def _sync(self):
        response = self.server.get(self.api_path)
        if response.status_code == requests.codes.not_found:
            raise exceptions.NotFound(_('user %s') % self.userid)
        elif response.status_code != requests.codes.ok:
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

    @property
    def authenticated(self):
        """Query the server to check we are really authenticated."""
        return self.server.whoami == self.userid

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
