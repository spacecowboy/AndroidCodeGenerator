"""Writes the generated classes to file
Will print to the terminal what is needed to
be added to the Manifest.

>>> g = Generator(srcdir="./src", pkg="com.ex.app.db")
"""

import os, errno
import dbitem
from dbitem import DBItem
from database_handler import DatabaseHandler
from database_triggers import DatabaseTriggers
from database_views import DatabaseViews
from provider import Provider

class Generator(object):

    def __init__(self, srcdir, pkg):
        """Need to specify srcdir and pkg. Srcdir
        is the directory where your java files lives.
        If srcdir is /projectdir/src for example,
        then inside you will get the directories:
        /projectdir/src/com/example/....

        given that your pkg was specified as
        com.example...

        So specify srcdir and package to be sensible values!

        To just see what the output is before you write to the
        final location, you can pass srcdir='./' and pkg='sample'
        for example"""
        self.srcdir = srcdir
        self.pkg = pkg
        self.tables = []
        self.triggers = []
        self.views = []

        # Make the full path to java dir
        self.path = os.path.join(srcdir, *pkg.split("."))

    def add_tables(self, *sqltables):
        self.tables.extend(sqltables)

    def add_triggers(self, *triggers):
        self.triggers.extend(triggers)

    def add_views(self, *views):
        self.views.extend(views)

    def write(self):
        mkdir_p(self.path)

        db_handler = DatabaseHandler("SampleDB", pkg=self.pkg)
        provider = Provider(classname="ItemProvider", pkg=self.pkg)

        db_triggers = DatabaseTriggers(pkg=self.pkg)
        db_triggers.add(*self.triggers)

        db_views = DatabaseViews(pkg=self.pkg)
        db_views.add(*self.views)

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
            javafile.write(dbitem.DBITEM_CLASS.format(pkg=self.pkg))

        # Triggers
        fpath = os.path.join(self.path,
                             "DatabaseTriggers.java")
        with open(fpath, 'w') as javafile:
            javafile.write(str(db_triggers))

        # Views
        fpath = os.path.join(self.path,
                             "DatabaseViews.java")
        with open(fpath, 'w') as javafile:
            javafile.write(str(db_views))

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

        # And print manifest stuff
        self.print_manifest(provider)

    def print_manifest(self, provider):
        """Print necessary manifest entries"""
        print("Make sure your AndroidManifest.xml contains the following:")
        print(provider.manifest_entry)

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
