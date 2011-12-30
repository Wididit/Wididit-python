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
from wididit import Server, People
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
        else:
            response.status_code = requests.codes.forbidden
        return response
    def put(self, url, data, headers={}, **kwargs):
        response = requests.Response()
        if 'auth' not in kwargs or kwargs['auth'] is None:
            response.status_code = requests.codes.forbidden
        elif url.startswith('/people/'):
            userid = url.split('/')[2]
            response.status_code = requests.codes.ok
            self.queries.append(('people', userid, data))
        return response

    def testBasics(self):
        people = People('tester', 'test.wididit.net')
        self.assertEqual(repr(people),
                "wididit.people.People('tester', 'test.wididit.net')")
        people2 = People('tester', 'test.wididit.net')
        people3 = People('tester', 'test2.wididit.net')
        people4 = People('tester2', 'test.wididit.net')
        self.assertEqual(people, people2)
        self.assertNotEqual(people, people3)
        self.assertNotEqual(people, people4)

    def testBiography(self):
        people = People('tester', 'test.wididit.net', 'foo', connect=True)
        self.assertEqual(people.biography,
                'biography of user tester@test.wididit.net')
        self.queries = []
        people.biography = 'foo'
        self.assertEqual(self.queries.pop(),
                ('people', 'tester@test.wididit.net', {
                    'username': 'tester',
                    'biography': 'foo'}))
        self.assertEqual(people.biography, 'foo')

    def testAuthentication(self):
        people = People('tester', 'test.wididit.net', 'foo')
        self.assertEqual(people.biography,
                'biography of user tester@test.wididit.net')
        self.assertRaises(exceptions.Forbidden, setattr,
                people, 'biography', 'foo')

    def testFromAnything(self):
        people = People.from_anything('tester@dev.progval.42')
        self.assertEqual(people.userid, 'tester@dev.progval.42')
        people = People.from_anything(people)
        self.assertEqual(people.userid, 'tester@dev.progval.42')
        people = People.from_anything(('tester', 'dev.progval.42'))
        self.assertEqual(people.userid, 'tester@dev.progval.42')

if __name__ == '__main__':
    unittest.main()

