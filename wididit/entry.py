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
            print response.content
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
        assert isinstance(author, People), \
                'author attribute should have been automatically converted' +\
                'to People instance.'
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
            if response.status_code != requests.codes.ok:
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
