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

import json
import base64
import requests

import wididit
from wididit.wididitobject import WididitObject


class RealServer(WididitObject):
    """Representation of a Wididit server.

    :param hostname: The hostname of the server.
    """
    def __new__(cls, hostname, *args, **kwargs):
        return super(RealServer, cls).__new__(cls, hostname)

    def __init__(self, hostname, connect_as=None, **kwargs):
        super(RealServer, self).__init__(**kwargs)
        self._hostname = hostname
        self.connected_as = connect_as

    def __repr__(self):
        return "wididit.server.Server('%s')" % self.hostname

    @property
    def hostname(self):
        """The hostname of the server. It should be unique across the whole
        universe."""
        return self._hostname

    @property
    def api_base(self):
        return 'http://%s/api/json' % self._hostname

    def get_connected_as(self):
        return self._connected_as
    def set_connected_as(self, value):
        self._connected_as = value
    def del_connected_as(self):
        self._connected_as = None
    connected_as = property(get_connected_as, set_connected_as,
            del_connected_as,
            'The People instance used to connect to authenticate to the '
            'server.')

    def _auth(self, headers):
        """Add the authentication token if any.

        :param headers: The headers to be modified.
        """
        if self.connected_as is not None:
            token = base64.b64encode(':'.join([self.connected_as.username,
                    self.connected_as.password]))
            headers.update({'HTTP_AUTHORIZATION': 'Basic ' + token})
        return headers
    def _auth_on_kwargs(self, kwargs):
        """Add the authentication token, if any.

        :param kwargs: The keyword-arguments, as ``requests`` take them.
        """
        if 'headers' not in kwargs:
            kwargs['headers'] = {}
        kwargs['headers'] = self._auth(kwargs['headers'])
        return kwargs

    def _get(self, url, **kwargs):
        return requests.get(self.api_base + url, **kwargs)
    def get(self, url, **kwargs):
        """Perform a GET request to the server.

        :param url: The URL to which perform the request
        :param **kwargs: Optional arguments that ``requests`` takes.
        """
        kwargs = self._auth_on_kwargs(kwargs)
        return self._get(url, **kwargs)

    def _post(self, url, **kwargs):
        return requests.post(self.api_base + url, **kwargs)
    def post(self, url, **kwargs):
        """Perform a POST request to the server.

        :param url: The URL to which perform the request
        :param **kwargs: Optional arguments that ``requests`` takes.
        """
        kwargs = self._auth_on_kwargs(kwargs)
        return self._post(url, **kwargs)

    def _put(self, url, **kwargs):
        return requests.put(self.api_base + url, **kwargs)
    def put(self, url, **kwargs):
        """Perform a PUT request to the server.

        :param url: The URL to which perform the request
        :param **kwargs: Optional arguments that ``requests`` takes.
        """
        kwargs = self._auth_on_kwargs(kwargs)
        return self._put(url, **kwargs)

    def _delete(self, url, **kwargs):
        return requests.delete(self.api_base + url, **kwargs)
    def delete(self, url, **kwargs):
        """Perform a DELETE request to the server.

        :param url: The URL to which perform the request
        :param **kwargs: Optional arguments that ``requests`` takes.
        """
        kwargs = self._auth_on_kwargs(kwargs)
        return self._delete(url, **kwargs)

    def serialize(self, data):
        """Serialize data to be sent to the server.

        :param data: The data to be serialized."""
        return json.dumps(data)

    def unserialize(self, data):
        """Unserialize data from the server.

        :param data: The data to be unserialized."""
        return json.loads(data)

class FakeServer(RealServer):
    """Mocks a Wididit server (for testing purposes)."""
    def __init__(self, *args, **kwargs):
        if wididit._test_callback is None:
            raise ImportError('No callback defined for tests.')
        super(FakeServer, self).__init__(*args, **kwargs)

    def _get(self, url, **kwargs):
        return wididit._test_callback.get(url, **kwargs)
    def _post(self, url, **kwargs):
        return wididit._test_callback.post(url, **kwargs)
    def _put(self, url, **kwargs):
        return wididit._test_callback.put(url, **kwargs)
    def _delete(self, url, **kwargs):
        return wididit._test_callback.delete(url, **kwargs)

import sys
Server = FakeServer if 'unittest' in sys.modules else RealServer