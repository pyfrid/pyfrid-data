#  Copyright 2012 Denis Korolkov
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from pyfrid.utils.odict import odict

class InvalidDatasetType(Exception):
    "Only Datasets can be added to a DataBook"

class InvalidDimensions(Exception):
    "Invalid size"

class InvalidDatasetIndex(Exception):
    "Outside of Dataset size"

class HeadersNeeded(Exception):
    "Header parameter must be given when appending a column in this Dataset."

class UnsupportedFormat(NotImplementedError):
    "Format is not supported"


class Row(object):

    __slots__ = ['_row']

    def __init__(self, row=list()):
        self._row = list(row)

    def __iter__(self):
        return (col for col in self._row)

    def __len__(self):
        return len(self._row)

    def __repr__(self):
        return repr(self._row)

    def __getslice__(self, i, j):
        return self._row[i,j]

    def __getitem__(self, i):
        return self._row[i]

    def __setitem__(self, i, value):
        self._row[i] = value

    def __delitem__(self, i):
        del self._row[i]

    def append(self, value):
        self.rpush(value)

    def insert(self, index, value):
        self._row.insert(index, value)

    def __contains__(self, item):
        return (item in self._row)

    @property
    def tuple(self):
        """Tuple representation of :class:`Row`."""
        return tuple(self._row)

    @property
    def list(self):
        """List representation of :class:`Row`."""
        return list(self._row)


class Dataset(object):
    """The :class:`Dataset` object is the heart of Tablib. It provides all core
    functionality.

    Usually you create a :class:`Dataset` instance in your main module, and append
    rows as you collect data. ::

        data = tablib.Dataset()
        data.headers = ('name', 'age')

        for (name, age) in some_collector():
            data.append((name, age))


    Setting columns is similar. The column data length must equal the
    current height of the data and headers must be set ::

        data = tablib.Dataset()
        data.headers = ('first_name', 'last_name')

        data.append(('John', 'Adams'))
        data.append(('George', 'Washington'))

        data.append_col((90, 67), header='age')


    You can also set rows and headers upon instantiation. This is useful if dealing
    with dozens or hundres of :class:`Dataset` objects. ::

        headers = ('first_name', 'last_name')
        data = [('John', 'Adams'), ('George', 'Washington')]

        data = tablib.Dataset(*data, headers=headers)

    :param \*args: (optional) list of rows to populate Dataset
    :param headers: (optional) list strings for Dataset header row


    .. admonition:: Format Attributes Definition

     If you look at the code, the various output/import formats are not
     defined within the :class:`Dataset` object. To add support for a new format, see
     :ref:`Adding New Formats <newformats>`.

    """

    def __init__(self, *args, **kwargs):
        self._data = list(Row(arg) for arg in args)
        self.__headers = None

        # ('title', index) tuples
        self._separators = []

        # (column, callback) tuples
        self._formatters = []

        try:
            self.headers = kwargs['headers']
        except KeyError:
            self.headers = None

    def __len__(self):
        return self.height

    def __getitem__(self, key):
        if isinstance(key, str) or isinstance(key, unicode):
            if key in self.headers:
                pos = self.headers.index(key) # get 'key' index from each data
                return [row[pos] for row in self._data]
            else:
                raise KeyError
        else:
            _results = self._data[key]
            if isinstance(_results, Row):
                return _results.tuple
            else:
                return [result.tuple for result in _results]

    def __setitem__(self, key, value):
        self._validate(value)
        self._data[key] = Row(value)

    def __delitem__(self, key):
        if isinstance(key, str) or isinstance(key, unicode):

            if key in self.headers:

                pos = self.headers.index(key)
                del self.headers[pos]

                for i, row in enumerate(self._data):

                    del row[pos]
                    self._data[i] = row
            else:
                raise KeyError
        else:
            del self._data[key]


    def __repr__(self):
        return '<dataset object>'

    def _validate(self, row=None, col=None, safety=False):
        """Assures size of every row in dataset is of proper proportions."""
        if row:
            is_valid = (len(row) == self.width) if self.width else True
        elif col:
            if len(col) < 1:
                is_valid = True
            else:
                is_valid = (len(col) == self.height) if self.height else True
        else:
            is_valid = all((len(x) == self.width for x in self._data))
            
        if is_valid:
            return True
        else:
            if not safety:
                raise InvalidDimensions
            return False

    def _package(self, dicts=True, ordered=True):
        """Packages Dataset into lists of dictionaries for transmission."""
        # TODO: Dicts default to false?
        _data = list(self._data)
        if ordered:
            dict_pack = odict
        else:
            dict_pack = dict
        # Execute formatters
        if self._formatters:
            for row_i, row in enumerate(_data):
                for col, callback in self._formatters:
                    try:
                        if col is None:
                            for j, c in enumerate(row):
                                _data[row_i][j] = callback(c)
                        else:
                            _data[row_i][col] = callback(row[col])
                    except IndexError:
                        raise InvalidDatasetIndex
        if self.headers:
            if dicts:
                data = [dict_pack(list(zip(self.headers, data_row))) for data_row in _data]
            else:
                data = [list(self.headers)] + list(_data)
        else:
            data = [list(row) for row in _data]

        return data



    def _get_headers(self):
        """An *optional* list of strings to be used for header rows and attribute names.

        This must be set manually. The given list length must equal :class:`Dataset.width`.

        """
        return self.__headers


    def _set_headers(self, collection):
        """Validating headers setter."""
        self._validate(collection)
        if collection:
            try:
                self.__headers = list(collection)
            except TypeError:
                raise TypeError
        else:
            self.__headers = None

    headers = property(_get_headers, _set_headers)


    def _clean_col(self, col):
        """Prepares the given column for insert/append."""

        col = list(col)

        if self.headers:
            header = [col.pop(0)]
        else:
            header = []

        if len(col) == 1 and hasattr(col[0], '__call__'):

            col = list(map(col[0], self._data))
        col = tuple(header + col)

        return col


    @property
    def height(self):
        """The number of rows currently in the :class:`Dataset`.
           Cannot be directly modified.
        """
        return len(self._data)


    @property
    def width(self):
        """The number of columns currently in the :class:`Dataset`.
           Cannot be directly modified.
        """

        try:
            return len(self._data[0])
        except IndexError:
            try:
                return len(self.headers)
            except TypeError:
                return 0

    # ----
    # Rows
    # ----

    def insert(self, index, row):
        """Inserts a row to the :class:`Dataset` at the given index.

        Rows inserted must be the correct size (height or width).

        The default behaviour is to insert the given row to the :class:`Dataset`
        object at the given index.
       """

        self._validate(row)
        self._data.insert(index, Row(row))

    def append(self, row):
        """Adds a row to the :class:`Dataset`.
        See :class:`Dataset.insert` for additional documentation.
        """

        self.insert(self.height, row=row)

    def extend(self, rows):
        """Adds a list of rows to the :class:`Dataset` using
        :class:`Dataset.append`
        """
        for row in rows:
            self.append(row)

    def pop(self):
        """Removes and returns the last row of the :class:`Dataset`."""

        cache = self[-1]
        del self[-1]

        return cache

    # -------
    # Columns
    # -------

    def insert_col(self, index, col=None, header=None):
        """Inserts a column to the :class:`Dataset` at the given index.

        Columns inserted must be the correct height.

        You can also insert a column of a single callable object, which will
        add a new column with the return values of the callable each as an
        item in the column. ::

            data.append_col(col=random.randint)

        If inserting a column, and :class:`Dataset.headers` is set, the
        header attribute must be set, and will be considered the header for
        that row.

        See :ref:`dyncols` for an in-depth example.

        .. versionchanged:: 0.9.0
           If inserting a column, and :class:`Dataset.headers` is set, the
           header attribute must be set, and will be considered the header for
           that row.

        .. versionadded:: 0.9.0
           If inserting a row, you can add :ref:`tags <tags>` to the row you are inserting.
           This gives you the ability to :class:`filter <Dataset.filter>` your
           :class:`Dataset` later.

        """

        if col is None:
            col = []

        # Callable Columns...
        if hasattr(col, '__call__'):
            col = list(map(col, self._data))

        col = self._clean_col(col)
        self._validate(col=col)

        if self.headers:
            # pop the first item off, add to headers
            if not header:
                raise HeadersNeeded()

            # corner case - if header is set without data
            elif header and self.height == 0 and len(col):
                raise InvalidDimensions

            self.headers.insert(index, header)


        if self.height and self.width:

            for i, row in enumerate(self._data):

                row.insert(index, col[i])
                self._data[i] = row
        else:
            self._data = [Row([row]) for row in col]


    def insert_separator(self, index, text='-'):
        """Adds a separator to :class:`Dataset` at given index."""

        sep = (index, text)
        self._separators.append(sep)


    def append_separator(self, text='-'):
        """Adds a :ref:`separator <separators>` to the :class:`Dataset`."""

        # change offsets if headers are or aren't defined
        if not self.headers:
            index = self.height if self.height else 0
        else:
            index = (self.height + 1) if self.height else 1

        self.insert_separator(index, text)


    def append_col(self, col, header=None):
        """Adds a column to the :class:`Dataset`.
        See :class:`Dataset.insert_col` for additional documentation.
        """

        self.insert_col(self.width, col, header)


    def get_col(self, index):
        """Returns the column from the :class:`Dataset` at the given index."""

        return [row[index] for row in self._data]

    def add_formatter(self, col, handler):
        """Adds a :ref:`formatter` to the :class:`Dataset`.

        .. versionadded:: 0.9.5
           :param col: column to. Accepts index int or header str.
           :param handler: reference to callback function to execute
           against each cell value.
        """

        if isinstance(col, str):
            if col in self.headers:
                col = self.headers.index(col) # get 'key' index from each data
            else:
                raise KeyError

        if not col > self.width:
            self._formatters.append((col, handler))
        else:
            raise InvalidDatasetIndex

        return True

    def clear(self, headers=True):
        """Removes all content and headers from the :class:`Dataset` object."""
        self._data = list()
        if headers:
            self.__headers = None

