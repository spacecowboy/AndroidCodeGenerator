"""Writes the generated classes to file

>>> g = Generator()
"""

import os, errno
import dbitem
from dbitem import DBItem
from database_handler import DatabaseHandler
from database_triggers import DatabaseTriggers
from provider import Provider

class Generator(object):

    def __init__(self, path = "./", pkg="com.example.appname.database"):
        self.path = path
        self.pkg = pkg
        self.tables = []
        self.triggers = []

    def add_tables(self, *sqltables):
        self.tables.extend(sqltables)

    def add_triggers(self, *triggers):
        self.triggers.extend(triggers)

    def write(self):
        mkdir_p(self.path)

        db_handler = DatabaseHandler("SampleDB", pkg=self.pkg)
        provider = Provider(pkg=self.pkg)

        # Generate dbitem files
        for table in self.tables:
            item = DBItem(table, pkg=self.pkg)
            filename = item.classname + ".java"
            fpath = os.path.join(self.path, filename)
            with open(fpath, 'w') as javafile:
                javafile.write(str(item))

            # Add to other classes
            db_handler.add_dbitems(item)
            provider.add_dbitems(item)

        # Abstract DBItem
        fpath = os.path.join(self.path,
                             "DBItem.java")
        with open(fpath, 'w') as javafile:
            javafile.write(dbitem.DBITEM_CLASS)

        # Triggers
        fpath = os.path.join(self.path,
                             "DatabaseTriggers.java")
        with open(fpath, 'w') as javafile:
            javafile.write(str(DatabaseTriggers(*self.triggers,
                                                pkg=self.pkg)))

        # Database handler
        fpath = os.path.join(self.path,
                             db_handler.classname + ".java")
        with open(fpath, 'w') as javafile:
            javafile.write(str(db_handler))

        # Provider
        fpath = os.path.join(self.path,
                             provider.classname + ".java")
        with open(fpath, 'w') as javafile:
            javafile.write(str(provider))


def mkdir_p(path):
    """Like mkdir -p it creates all directories
    in a path if they do not exist"""
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise
