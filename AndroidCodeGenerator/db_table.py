"""Contains methods that generate a database table structure
similar to what is presented in my
[tutorial](https://github.com/spacecowboy/AndroidTutorialContentProvider)
"""

# I make heavy use of string format
_C_T = \
"""CREATE TABLE {table_name}
  ({columns}

  {constraints})"""

_F_K = "FOREIGN KEY ({column_name}) REFERENCES \
{foreign_table}({foreign_column}) {cascade_case}"


class Column(object):
    """Used to build a column definition. Example usage:

    >>> Column('age').real.not_null.default(12)
    age REAL NOT NULL DEFAULT 12

    >>> Column('_id').integer.primary_key
    _id INTEGER PRIMARY KEY
    """

    def __init__(self, name):
        self.name = name
        self.type = "TEXT"
        self.constraint = ""

    @property
    def upper_name(self):
        '''return uppercase of name'''
        return self.name.upper()

    def __repr__(self):
        return " ".join([self.name, self.type, self.constraint]).strip()

    def set_type(self, typestring):
        '''Set the type of this column'''
        self.type = typestring.strip()
        return self

    @property
    def text(self):
        return self.set_type("TEXT")

    @property
    def integer(self):
        return self.set_type("INTEGER")

    @property
    def real(self):
        return self.set_type("REAL")

    @property
    def timestamp(self):
        return self.set_type("TIMESTAMP")

    def set_constraint(self, *constraints):
        '''Set the constraint on the column'''

        self.constraint = " ".join(constraints).strip()
        return self

    @property
    def not_null(self):
        return self.set_constraint(self.constraint, "NOT NULL")

    @property
    def primary_key(self):
        return self.set_constraint(self.constraint, "PRIMARY KEY")

    def default(self, val):
        return self.set_constraint(self.constraint,
                                   "DEFAULT {}".format(val))


class Unique(object):
    """Unique constraint on a table

    Example:

    >>> Unique('name')
    UNIQUE (name)

    >>> Unique('artist', 'album')
    UNIQUE (artist, album)

    >>> Unique('hash').on_conflict_replace
    UNIQUE (hash) ON CONFLICT REPLACE

    >>> Unique('hash').on_conflict_rollback
    UNIQUE (hash) ON CONFLICT ROLLBACK
    """

    def __init__(self, *colnames):
        self.colnames = colnames
        self.conflict_clause = ""

    def __repr__(self):
        return "UNIQUE({}) {}".format(", ".join(self.colnames),
                                       self.conflict_clause)\
               .strip()

    def _conflict(self, case):
        self.conflict_clause = "ON CONFLICT {}".format(case)
        return self

    @property
    def on_conflict_replace(self):
        return self._conflict("REPLACE")

    @property
    def on_conflict_rollback(self):
        return self._conflict("ROLLBACK")

    @property
    def on_conflict_abort(self):
        return self._conflict("ABORT")

    @property
    def on_conflict_fail(self):
        return self._conflict("FAIL")

    @property
    def on_conflict_ignore(self):
        return self._conflict("IGNORE")


class ForeignKey(object):
    """Foreign key constraint

    Example:

    >>> ForeignKey('listid').references('list', '_id').on_delete_cascade
    FOREIGN KEY (listid) REFERENCES list(_id) ON DELETE CASCADE
    """

    def __init__(self, column_name):
        self.column_name = column_name
        self.foreign_table = ""
        self.foreign_col = ""
        self.cascade_case = ""

    def __repr__(self):
        return _F_K.format(column_name=self.column_name,
                           foreign_table=self.foreign_table,
                           foreign_column=self.foreign_col,
                           cascade_case=self.cascade_case)

    def references(self, table_name, col_name="_id"):
        self.foreign_table = table_name
        self.foreign_col = col_name
        return self

    @property
    def on_delete_cascade(self):
        self.cascade_case = "ON DELETE CASCADE"
        return self

    @property
    def on_delete_set_null(self):
        self.cascade_case = "ON DELETE SET NULL"
        return self

    @property
    def on_delete_set_default(self):
        self.cascade_case = "ON DELETE SET DEFAULT"
        return self


class Table(object):
    """An SQL table which consists of columns
    and constraints. It is prepopualted with an _id column
    which is the primary key.

    Example usage:
    >>> Table('People')
    CREATE TABLE People
      (_id INTEGER PRIMARY KEY
    <BLANKLINE>
      )

    >>> Table('People').cols(Column('name').text.not_null.default("''"), \
                             Column('age').integer.not_null.default(18))
    CREATE TABLE People
      (_id INTEGER PRIMARY KEY,
      name TEXT NOT NULL DEFAULT '',
      age INTEGER NOT NULL DEFAULT 18
    <BLANKLINE>
      )

    >>> Table('Albums').cols(Column('albumname').text.not_null.default("''"), \
                             Column('artistname').text.not_null)\
.constraints(ForeignKey('artistname').references('artist', 'name')\
              .on_delete_cascade,\
             Unique('albumname').on_conflict_replace)
    CREATE TABLE Albums
      (_id INTEGER PRIMARY KEY,
      albumname TEXT NOT NULL DEFAULT '',
      artistname TEXT NOT NULL
    <BLANKLINE>
      FOREIGN KEY (artistname) REFERENCES artist(name) ON DELETE CASCADE,
      UNIQUE (albumname) ON CONFLICT REPLACE)

    """

    def __init__(self, name):
        self.name = name
        self._columns = [Column('_id').integer.primary_key]
        self._constraints = []

    def __repr__(self):
        return _C_T.format(table_name = self.name,
                           columns = ",\n  ".join(map(str, self._columns)),
                           constraints = ",\n  ".join(map(str,
                                                          self._constraints)))

    def cols(self, *columns):
        self._columns.extend(columns)
        return self

    def constraints(self, *constraints):
        self._constraints.extend(constraints)
        return self
