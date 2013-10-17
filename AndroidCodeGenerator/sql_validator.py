from __future__ import print_function, division
import sqlite3 as sql
import os

def clear_db(func):
    '''Removes the db-file before and after
    function call'''
    def _wrap(*args, **kwargs):
        try:
            os.remove('test.db')
        except OSError:
            pass

        func(*args, **kwargs)

        try:
            os.remove('test.db')
        except OSError:
            pass

    return _wrap

def set_pragmas(cur):
    cur.execute("PRAGMA foreign_keys = ON;")

class SQLTester(object):
    """This class actually creates an sql database
    and tries to create all the tables and triggers
    you have defined. That way you can verify that
    your schema actually works (in theory) without
    building your android project."""

    def __init__(self):
        self.tables = []
        self.triggers = []
        self.views = []

    def add_tables(self, *sqltables):
        self.tables.extend(sqltables)

    def add_triggers(self, *triggers):
        self.triggers.extend(triggers)

    def add_views(self, *views):
        self.views.extend(views)

    @clear_db
    def test_create(self):
        """Try creating all tables and triggers"""
        con = sql.connect('test.db')
        con.row_factory = sql.Row
        with con:
            cur = con.cursor()
            set_pragmas(cur)

            for table in self.tables:
                print("\n", table)
                cur.execute(str(table))

            for view in self.views:
                print("\n", view)
                cur.execute(str(view))

            for trigger in self.triggers:
                print("\n", trigger)
                cur.execute(str(trigger))
