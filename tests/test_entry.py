#!/usr/bin/env python

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

import sys
import json
import unittest
import requests

import wididit
from wididit import exceptions
from wididit import Server, People, Entry
from wididittestcase import WididitTestCase

class TestPeople(WididitTestCase):
    queries = []
    def get(self, url, **kwargs):
        response = requests.Response()
        if url.startswith('/people/'):
            userid = url.split('/')[2]
            username, hostname = userid.split('@')
            response.status_code = requests.codes.ok
            response._content = json.dumps(
                    {'username': username,
                     'biography': 'biography of user %s' % userid,
                     'server': {'hostname': hostname}})
        elif url.startswith('/entry/'):
            # The server is free to set whatever it wants whenever it wants;
            # the library should allow that.
            data = {
                    'content': 'the content',
                    'author': 'tester@test.wididit.net',
                    'category': '',
                    'contributors': [],
                    'generator': 'the generator',
                    'published': '2011-12-30 15:54:00',
                    'rights': '',
                    'source': '',
                    'subtitle': '',
                    'summary': '',
                    'title': 'the title',
                    'updated': '2011-12-30 15:55:05',
                    }
            response.status_code = requests.codes.ok
            response._content = Server.serialize(data)
        else:
            response.status_code = requests.codes.forbidden
        return response
    def post(self, url, data, headers={}, **kwargs):
        response = requests.Response()
        if 'auth' not in kwargs or kwargs['auth'] is None:
            response.status_code = requests.codes.forbidden
        elif url.startswith('/entry/'):
            response.status_code = requests.codes.created
            self.queries.append(('post', 'entry', data))
            response._content = '1'
        return response

    def testCreation(self):
        tester = wididit.People('tester', 'test.wididit.net', 'password',
                connect=True)
        entry = Entry(tester, title='my title', content='my content')
        self.assertEqual(len(self.queries), 1)
        query = self.queries.pop()
        self.assertEqual(query[0], 'post')
        self.assertEqual(query[1], 'entry')
        self.assertEqual(query[2]['content'], 'my content')
        self.assertEqual(query[2]['title'], 'my title')
        self.assertNotIn('azerty', query[2])
        self.assertEqual(entry.content, 'the content')
        self.assertEqual(entry.author.server.connected_as, tester)

    def testGet(self):
        entry = Entry('tester@test.wididit.net', 1)
        self.assertEqual(entry.content, 'the content')
        tester = People('tester', 'test.wididit.net')
        self.assertEqual(entry.author, tester)


if __name__ == '__main__':
    unittest.main()

