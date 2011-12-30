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

class WididitObject(object):
    """Base class for all Wididit classes.

    All subclasses of this class with _singleton=True are parametric singletons,
    according to the parameters they give to super()'s __new__.
    This class also provides __repr__ and __eq__ based on class and parameters
    given to super()'s __new__.
    """
    _singleton = False
    __instances = {}
    def __new__(cls, *args):
        if not cls._singleton:
            instance = object.__new__(cls)
            instance._parameters = args
            return instance
        if cls not in cls.__instances:
            cls.__instances[cls] = {}
        if args not in cls.__instances[cls]:
            instance = object.__new__(cls)
            instance._parameters = args
            cls.__instances[cls][args] = instance
        return cls.__instances[cls][args]

    def __repr__(self):
        return '%s.%s(%s)' % (
                self.__class__.__module__,
                self.__class__.__name__,
                ', '.join([repr(x) for x in self._parameters])
                )

    def __eq__(self, other):
        return self.__class__ is other.__class__ and \
                self._parameters == other._parameters

    def sync(self):
        """Update the state of this object.

        This method updates attributes of this object according to server, but
        also discards all modifications you made without saving it.
        However, all modifications are saved by default."""
        self._sync()
