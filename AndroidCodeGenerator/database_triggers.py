from db_table import Trigger

class DatabaseTriggers(object):
    """Creates DatabaseTriggers.java

    Examples:

    >>> t1 = Trigger('tr_archive').temp.if_not_exists.before.delete_on('notes')\
    .do_sql('INSERT INTO archive (noteid,notetext) VALUES (old._id,old.text)')

    >>> t2 = Trigger('tr_log').if_not_exists.before.update_on('notes')\
    .do_sql('INSERT INTO log (noteid,notetext) VALUES (new._id,new.text)')

    >>> DatabaseTriggers(t1, t2)
    package com.example.appname.database;
    <BLANKLINE>
    import android.database.sqlite.SQLiteDatabase;
    <BLANKLINE>
    public class DatabaseTriggers {
    <BLANKLINE>
        /**
         * Create permanent triggers. They are dropped first,
         * if they already exist.
         */
        public static void create(final SQLiteDatabase db) {
            db.execSQL("DROP TRIGGER IF EXISTS tr_log";
            db.execSQL(tr_log);
        }
    <BLANKLINE>
        /**
         * Create temporary triggers. Nothing is done if they
         * already exist.
         */
        public static void createTemp(final SQLiteDatabase db) {
            db.execSQL(tr_archive);
        }
    <BLANKLINE>
        private static final String tr_archive =
    "CREATE TEMP TRIGGER IF NOT EXISTS tr_archive"
    +"  BEFORE DELETE ON notes"
    +"  BEGIN"
    +"    INSERT INTO archive (noteid,notetext) VALUES (old._id,old.text);"
    +"  END";
        private static final String tr_log =
    "CREATE  TRIGGER IF NOT EXISTS tr_log"
    +"  BEFORE UPDATE  ON notes"
    +"  BEGIN"
    +"    INSERT INTO log (noteid,notetext) VALUES (new._id,new.text);"
    +"  END";
    }

    """

    def __init__(self, *triggers, **kwargs):
        if 'pkg' in kwargs:
            self.pkg = kwargs['pkg']
        else:
            self.pkg = "com.example.appname.database"

        self.triggers = []
        if triggers is not None and len(triggers) > 0:
            self.add(*triggers)

    def add(self, *triggers):
        self.triggers.extend(triggers)

    def __repr__(self):
        return _J_T.format(self)

    @property
    def create_perm(self):
        result = ""
        for trigger in self.triggers:
            if not trigger.is_temp:
                result += _C_P.format(trigger)
        return result.strip()

    @property
    def create_temp(self):
        result = ""
        for trigger in self.triggers:
            if trigger.is_temp:
                result += _C_T.format(trigger)
        return result.strip()

    @property
    def def_triggers(self):
        result = ""
        for trigger in self.triggers:
            result += _D_T.format(trigger)

        return result.strip()

_D_T = '''
    private static final String {0.name} =
"{0.java_string}";'''

_C_P = '''
        db.execSQL("DROP TRIGGER IF EXISTS {0.name}";
        db.execSQL({0.name});
'''

_C_T = '''        db.execSQL({0.name});'''


_J_T = '''package {0.pkg};

import android.database.sqlite.SQLiteDatabase;

public class DatabaseTriggers {{

    /**
     * Create permanent triggers. They are dropped first,
     * if they already exist.
     */
    public static void create(final SQLiteDatabase db) {{
        {0.create_perm}
    }}

    /**
     * Create temporary triggers. Nothing is done if they
     * already exist.
     */
    public static void createTemp(final SQLiteDatabase db) {{
        {0.create_temp}
    }}

    {0.def_triggers}
}}'''
