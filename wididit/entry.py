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

import time
import requests

from wididit import utils
from wididit.i18n import _
from wididit import People
from wididit import exceptions
from wididit.wididitobject import WididitObject

def editable_property_factory(name, assert_type=None, docstring=None):
    def get_property(self):
        return getattr(self, '_' + name)
    def set_property(self, value):
        if assert_type is not None and not isinstance(value, assert_type):
            raise ValueError()
        state = self.as_serializable
        state[name] = value
        response = self.author.server.put(self.api_path, data=state)
        if response.status_code == requests.codes.ok:
            setattr(self, '_' + name, value)
            response = self.author.server.get(self.api_path)
            assert response.status_code == requests.codes.ok
            reply = self.author.server.unserialize(response.content)
            self._updated = time.strptime(reply['updated'], self._time_format)
        elif response.status_code == requests.codes.forbidden:
            raise exceptions.Forbidden(_('edit this entry'))
        else:
            raise exceptions.ServerException(response.status_code)
    return property(get_property, set_property, docstring)

class Entry(WididitObject):
    """Representation of a Wididit entry.

    :param author: The author of the entry. Can be any representation of a
                   People object (see :py:meth:`wididit.People.from_anything`)
    :param id: The ID of this entry (only unique against the author). Do not
               give this parameter if you don't want to sync (yet) with the
               server.
    """
    _singleton = True
    def __new__(cls, author, id=None, *args, **kwargs):
        author = People.from_anything(author)
        return super(Entry, cls).__new__(cls, author, id)

    def __init__(self, author, id=None, **initial_data):
        author = People.from_anything(author)
        self._author = author
        self._id = id
        if id is None:
            self._sync(initial_data)
        else:
            self._sync()
        missing_attr = [x for x in self._fields if not hasattr(self, x)]
        assert len(missing_attr) == 0, \
                'This attributes are missing: %s' % ', '.join(missing_attr)

    _time_format = '%Y-%m-%d %H:%M:%S'

    @property
    def author(self):
        """The author of this entry."""
        return self._author

    @property
    def id(self):
        """The ID of this entry."""
        return self._id

    @property
    def entryid(self):
        """The EntryID of this entry."""
        return '%s/%s' % (self.author.userid, self.id)

    content = editable_property_factory('content', str)
    category = editable_property_factory('category', str)
    contributors = editable_property_factory('contributors', list)
    generator = editable_property_factory('generator', list)
    rights = editable_property_factory('rights', list)
    source = editable_property_factory('source', list)
    subtitle = editable_property_factory('subtitle', list)
    summary = editable_property_factory('summary', list)
    title = editable_property_factory('title', list)

    @property
    def published(self):
        return self._published

    @property
    def updated(self):
        return self._updated

    @property
    def api_path(self):
        """The path to this entry in the API."""
        if self.id is None:
            return '/entry/'
        else:
            return '/entry/%s/%s/' % (self.author.userid, self.id)

    @property
    def _fields(self):
        return ('content author category contributors generator '
                'published rights source subtitle summary title updated') \
                .split()


    @property
    def as_serializable(self):
        """A serializable representation of this Entry.

        It is composed of basic data, such as integers, strings, None, lists
        and integers.
        """
        dict_ = {}
        for name in self._fields:
            dict_[name] = getattr(self, name)
        dict_['author'] = dict_['author'].userid
        dict_['contributors'] = [x.userid for x in dict_['contributors']]
        dict_['published'] = time.strftime(self._time_format,
                dict_['published'])
        dict_['updated'] = time.strftime(self._time_format, dict_['updated'])
        return dict_

    def _sync(self, initial_data=None):
        if initial_data is None:
            assert self.id is not None
            response = self.author.server.get(self.api_path)
            if response.status_code == requests.codes.not_found:
                raise exceptions.NotFound(_('entry %s') % self.entryid)
            elif response.status_code != requests.codes.ok:
                raise exceptions.ServerException(response.status_code)
            reply = self.author.server.unserialize(response.content)
            self._content = reply['content']
            self._category = reply['category']
            self._contributors = [People.from_anything(x)
                    for x in reply['contributors']]
            self._generator = reply['generator']
            self._published = time.strptime(reply['published'], self._time_format)
            self._rights = reply['rights']
            self._source = reply['source']
            self._subtitle = reply['subtitle']
            self._summary = reply['summary']
            self._title = reply['title']
            self._updated = time.strptime(reply['updated'], self._time_format)
        else:
            assert self.id is None
            initial_data['author'] = self.author.userid
            if 'generator' not in initial_data:
                initial_data['generator'] = 'Wididit python library'
            response = self.author.server.post(self.api_path,
                    data=initial_data)
            if response.status_code == requests.codes.forbidden:
                raise exceptions.Forbidden(_('create an entry'))
            elif response.status_code != requests.codes.created:
                raise exceptions.ServerException(response.status_code)
            else:
                self._id = int(response.content)
                self._sync()

    class Query(object):
        """Get entries from the server. Default mode is MODE_TIMELINE.

        Queries are lazy. They perform the request to the server as late as
        possible (that's to say when you access items).

        As all filtering methods return the query itself, you can chain calls:

        .. code-block:: python

            server = Server('example.com')
            entries = Query(server).filterAuthor('ProgVal') \\
                    .filterContent('lol').filterContent('test').fetch()
        """
        MODE_ALL = 1
        """Fetch entries from all sources."""
        MODE_TIMELINE = 2
        """Fetch entries only from user's subscriptions. Only available if
        you are connected to the server."""
        def __init__(self, server, mode=MODE_TIMELINE):
            self._server = server
            if mode == self.MODE_ALL:
                self._url = '/entry/'
            elif mode == self.MODE_TIMELINE:
                assert server.connected_as is not None
                self._url = '/entry/timeline/'
            else:
                raise ValueError('Invalid mode.')
            self._params = {}

        def filterAuthor(self, author):
            """Only get results by this author.

            Using this method twice is handled as a OR clause by the server.

            :param author: A valid representation of a people.
            """
            if 'author' not in self._params:
                self._params['author'] = []
            self._params['author'].append(People.from_anything(author).userid)
            return self

        def filterContent(self, text):
            """Only get results containing this text.

            Using this method twice is handled as a AND clause by the server.

            :param text: Some text to be filtered.
            """
            if 'content' not in self._params:
                self._params['content'] = []
            self._params['content'].append(text)
            return self

        def native(self, value=True):
            """(Dis)allow native queries. If this method is not called, it
            defaults to True.

            See also :py:meth:`wididit.Entry.Query.shared`.

            :param value: Defines whether native entries are allowed or not.
            """
            if value and 'nonative' in self._params:
                del self._params['nonative']
            elif not value:
                self._params['nonative'] = None
            return self

        def shared(self, value=False):
            """(Dis)allow shared queries. If this method is not called, it
            defaults to False.

            See also :py:meth:`wididit.Entry.Query.native`.

            :param value: Defines whether shared entries are allowed or not.
            """
            if value:
                self._params['shared'] = None
            elif not value and 'shared' in self._params:
                del self._params['shared']
            return self

        def fetch(self):
            """Return all entries matching this query.
            """
            response = self._server.get(self._url, params=self._params)
            if response.status_code != requests.codes.ok:
                raise exceptions.ServerException(response.status_code)
            reply = self._server.unserialize(response.content)
            entries = []
            for data in reply:
                entry = Entry(People.from_anything(data['author']), data['id'],
                    initial_data=data)
                entries.append(entry)
            return entries
