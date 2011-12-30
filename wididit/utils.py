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

import re

from wididit import constants

def userid2tuple(userid, default_server=None):
    """Takes a userid and returns a tuple (username, server).

    If the userid contains '@', it will split it and return it as the tuple.
    If not, returns the userid and the default server."""
    if '@' in userid:
        parts = userid.split('@')
        assert len(parts) in (1, 2)
        return tuple(parts)
    else:
        if default_server is None:
            raise ValueError()
        return (userid, default_server)

_tag_regexp = re.compile('(?<!\S)(#[^ .,;:?!]{,%i})' %
        (constants.MAX_TAG_LENGTH))
def get_tags(content):
    """Returns all :ref:`concepts-tags` from the text."""
    return _tag_regexp.findall(content)

def _tag_process_tree(tree, tags):
    if len(tags) == 0:
        return
    tag = ''
    while tag == '':
        tag = tags.pop(0)
    if tag not in tree:
        tree.update({tag: {}})
    _tag_process_tree(tree[tag], tags)
def get_tag_tree(content):
    """Returns all tags in the text, and processes :ref:`concepts-tag-trees`
    as dicts."""
    raw_tags = get_tags(content)
    tree = {}
    for tag in raw_tags:
        tags = tag.split('#')
        _tag_process_tree(tree, tags)
    return tree
