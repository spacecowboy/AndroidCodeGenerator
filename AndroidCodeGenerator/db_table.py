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

_C_TR = \
"""CREATE {0._temp} TRIGGER {0._ifnotexists} {0.name}
  {0._when} {0._action}
  BEGIN
    {body}
  END"""

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
    @property
    def default_current_timestamp(self):
        '''Use with timestamp type to default to now.
        Stored as YYYY-MM-DD HH:MM:SS'''
        return self.set_constraint(self.constraint,
                                   "DEFAULT CURRENT_TIMESTAMP")


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
        return "UNIQUE ({}) {}".format(", ".join(self.colnames),
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


class Check(object):
    """Check constraint on a table

    Example:

    >>> Check("name = 'bob'")
    CHECK (name = 'bob')

    >>> Check('name', ' > 0')
    CHECK (name > 0)

    >>> Check('name1', '<=', 'name2')
    CHECK (name1 <= name2)

    >>> Check(' bob ', '  <  ', 36)
    CHECK (bob < 36)
    """

    def __init__(self, *args):
        if len(args) < 1:
            raise ValueError("Must specify at least one argument!")

        self.args = args

    def __repr__(self):
        return "CHECK ({})".format(" "\
                                   .join([str(x).strip() for x in self.args]))


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

    >>> Table('People').add_cols(Column('name').text.not_null.default("''"), \
                                 Column('age').integer.not_null.default(18))
    CREATE TABLE People
      (_id INTEGER PRIMARY KEY,
      name TEXT NOT NULL DEFAULT '',
      age INTEGER NOT NULL DEFAULT 18
    <BLANKLINE>
      )

    >>> Table('Albums').add_cols(Column('albumname').text.not_null.default("''"), \
                                 Column('artistname').text.not_null)\
.add_constraints(ForeignKey('artistname').references('artist', 'name')\
              .on_delete_cascade,\
             Unique('albumname').on_conflict_replace)
    CREATE TABLE Albums
      (_id INTEGER PRIMARY KEY,
      albumname TEXT NOT NULL DEFAULT '',
      artistname TEXT NOT NULL,
    <BLANKLINE>
      FOREIGN KEY (artistname) REFERENCES artist(name) ON DELETE CASCADE,
      UNIQUE (albumname) ON CONFLICT REPLACE)

    """

    def __init__(self, name):
        self.name = name
        self._columns = [Column('_id').integer.primary_key]
        self._constraints = []
        self.fts3_cols = None

    def __repr__(self):
        constraints = ",\n  ".join(map(str, self._constraints))
        columns = ",\n  ".join(map(str, self._columns))

        if len(constraints) > 0:
            # Add a comma at the end
            columns += ","

        return _C_T.format(table_name = self.name,
                           columns = columns,
                           constraints = constraints)

    def add_cols(self, *columns):
        self._columns.extend(columns)
        return self

    def add_constraints(self, *constraints):
        self._constraints.extend(constraints)
        return self

    def list_column_names(self, sep=",", withid=False, prefix="",
                          exclude=None):
        """Use to get a single string of column names. By default, it
        will exclude the _id column. Give an empty list to include
        _id. If you want to exclude as many columns as you like.

        Examples:

        >>> living = Table('LivePerson').add_cols(\
                        Column('firstname').text.not_null.default("''"),\
                        Column('lastname').text.not_null.default("''"),\
                        Column('bio').text.not_null.default("''"))

        >>> living.list_column_names()
        'firstname,lastname,bio'

        >>> living.list_column_names(exclude=[])
        '_id,firstname,lastname,bio'

        >>> living.list_column_names(exclude=['_id'])
        'firstname,lastname,bio'

        >>> living.list_column_names(exclude=['lastname', 'bio'])
        '_id,firstname'

        >>> living.list_column_names(withid=True, prefix='old.')
        'old._id,old.firstname,old.lastname,old.bio'
        """
        cols = self._columns
        if exclude is None:
            exclude = ["_id"]
        if not withid:
            cols = []
            for c in self._columns:
                if c.name not in exclude:
                    cols.append(c)

        return sep.join([prefix + c.name for c in cols])


class Trigger(object):
    """Create an sql trigger

    Examples:

    >>> Trigger('tr_archive').temp.if_not_exists.before.delete_on('notes')\
    .do_sql('INSERT INTO archive (noteid,notetext) VALUES (old._id,old.text)')
    CREATE TEMP TRIGGER IF NOT EXISTS tr_archive
      BEFORE DELETE ON notes
      BEGIN
        INSERT INTO archive (noteid,notetext) VALUES (old._id,old.text);
      END
    """

    def __init__(self, name):
        self.name = name
        self._temp = ""
        self._ifnotexists = ""
        self._action = None
        self._when = None
        self._body = []

    @property
    def java_string(self):
        sql = str(self)
        return '"\n+"'.join(sql.split('\n'))

    def __repr__(self):
        if self._when is None:
            raise ValueError('You must specify a trigger time, like:\
            Trigger("bob").after, .before or .instead_of')

        if self._action is None:
            raise ValueError('You must specify a trigger action, like:\
            Trigger("bob").update_on("sometable)')

        if len(self._body) < 1:
            raise ValueError('You must specify a trigger body, like:\
            Trigger("bob").do("SQL")')

        return _C_TR.format(self,
                            body="\n".join(self._body))

    @property
    def temp(self):
        self._temp = "TEMP"
        return self

    @property
    def is_temp(self):
        return len(self._temp) > 0

    @property
    def if_not_exists(self):
        self._ifnotexists = "IF NOT EXISTS"
        return self

    @property
    def before(self):
        self._when = "BEFORE"
        return self

    @property
    def after(self):
        self._when = "AFTER"
        return self

    @property
    def instead_of(self):
        self._when = "INSTEAD OF"
        return self

    def delete_on(self, tablename):
        self._action = "DELETE ON {}".format(tablename)
        return self

    def insert_on(self, tablename):
        self._action = "INSERT ON {}".format(tablename)
        return self

    def update_on(self, tablename, *cols):
        of_cols = ""
        if cols is not None and len(cols) > 0:
            of_cols = "OF {}".format(",".join(cols))

        self._action = "UPDATE {} ON {}".format(of_cols,
                                                tablename)
        return self

    def do_sql(self, sqlstatement):
        end = ""
        if not sqlstatement.strip().endswith(";"):
            end = ";"
        self._body.append(sqlstatement.strip() + end)
        return self


class TableFTS3(object):
    '''Create a virtual table using fts3, and triggers to keep it up
    to date.

    Example:

    >>> TableFTS3("tasks").use_cols("title", "note")
    CREATE VIRTUAL TABLE tasks_fts3 USING FTS3 (_id, title, note);
    <BLANKLINE>
    CREATE  TRIGGER  tr_tasks_fts3_ins
      AFTER INSERT ON tasks
      BEGIN
        INSERT INTO tasks_fts3(_id, title, note) VALUES (new._id, new.title, new.note);
      END
    <BLANKLINE>
    CREATE  TRIGGER  tr_tasks_fts3_del
      AFTER DELETE ON tasks
      BEGIN
        DELETE FROM tasks_fts3 WHERE _id IS old._id;
      END
    <BLANKLINE>
    CREATE  TRIGGER  tr_tasks_fts3_up
      AFTER UPDATE OF title,note ON tasks
      BEGIN
        UPDATE tasks_fts3 SET title = new.title, note = new.note WHERE _id IS new._id;
      END

    '''

    def __init__(self, tablename):
        '''Argument is the table which fts3 should search in'''
        self.tablename = tablename
        self.name = tablename + "_fts3"
        self.cols = []

    def use_cols(self, *cols):
        self.cols.extend(cols)
        return self

    def _cols(self, prefix="", suffix=""):
        cols = self.cols
        if '_id' not in cols:
            cols = ['_id'] + cols
        cols = ["{}{}{}".format(prefix, col, suffix)\
                for col in cols]
        return ", ".join(cols)

    @property
    def table_stmt(self):
        if len(self.cols) < 1:
            raise ValueError('Need some columns!')
        stmt = "CREATE VIRTUAL TABLE {} USING FTS3 ({});"
        return stmt.format(self.name,
                           self._cols())

    @property
    def trigger_stmts(self):
        return [str(t) for t in self.triggers]

    @property
    def triggers(self):
        if len(self.cols) < 1:
            raise ValueError('Need some columns!')
        triggers = []
        # Insert trigger
        tr_ins = Trigger("tr_" + self.name + "_ins").after.insert_on(self.tablename)
        tr_ins.do_sql("INSERT INTO {}\
({}) VALUES ({})".format(self.name,
                         self._cols(),
                         self._cols(prefix="new.")))
        triggers.append(tr_ins)
        # Delete trigger
        tr_del = Trigger("tr_" + self.name + "_del").after.delete_on(self.tablename)
        tr_del.do_sql("DELETE FROM {} WHERE _id IS old._id".format(self.name))
        triggers.append(tr_del)
        # Update trigger
        tr_up = Trigger("tr_" +
                        self.name +
                        "_up").after.update_on(self.tablename,
                                               *self.cols)
        s = "UPDATE {} SET {} WHERE _id IS new._id"
        setters = ["{0} = new.{0}".format(col) for col in self.cols]
        tr_up.do_sql(s.format(self.name,
                          ", ".join(setters)))
        triggers.append(tr_up)

        return triggers

    def __repr__(self):
        return "\n\n".join([self.table_stmt] + self.trigger_stmts)
