"""This file facilitates creating a DatabaseHandler


>>> from db_table import Table, Column, ForeignKey, Unique
>>> from dbitem import DBItem

>>> t = Table('Album').cols(Column('albumname').text.not_null.default("''"), \
                            Column('artistname').text.not_null)\
.constraints(ForeignKey('artistname').references('artist', 'name')\
              .on_delete_cascade,\
             Unique('albumname').on_conflict_replace)

>>> handler = DatabaseHandler("MusicDB", DBItem(t))
"""

from dbitem import DBItem

class DatabaseHandler(object):
    """Generates a DatabaseHandler.java file"""

    def __init__(self, databasename, *items):
        self.databasename = databasename
        self.dbitems = []
        if items is not None and len(items) > 0:
            self.add_dbitems(*items)

    def add_dbitems(self, *items):
        self.dbitems.extend(items)

    def create_tables(self):
        result = ""
        for table in self.dbitems:
            result += CREATE_DROP_TEMPLATE.format(classname=table.classname)
        return result

    def table_getters(self):
        result = ""
        for table in self.dbitems:
            result += GETITEM_TEMPLATE.format(classname=table.classname)
            result += GETALL_TEMPLATE.format(classname=table.classname)
        return result

    @property
    def classname(self):
        return "DatabaseHandler"

    def __repr__(self):
        return HANDLER_TEMPLATE.format(classname=self.classname,
                                       databasename=self.databasename,
                                       create_tables=self.create_tables(),
                                       table_getters=self.table_getters())

CREATE_DROP_TEMPLATE = """
        db.execSQL("DROP TABLE IF EXISTS " + {classname}.TABLE_NAME);
        db.execSQL({classname}.CREATE_TABLE);
"""

GETITEM_TEMPLATE = """
    public synchronized Cursor get{classname}Cursor(final long id) {{
        final SQLiteDatabase db = this.getReadableDatabase();
        final Cursor cursor = db.query({classname}.TABLE_NAME,
                {classname}.FIELDS, {classname}.COL_ID + " IS ?",
                new String[] {{ String.valueOf(id) }}, null, null, null, null);
        return cursor;
    }}

    public synchronized {classname} get{classname}(final long id) {{
        final Cursor cursor = get{classname}Cursor(id);
        final {classname} result;
        if (cursor.moveToFirst()) {{
            result = new {classname}(cursor);
        }}
        else {{
            result = null;
        }}

        cursor.close();
        return result;
    }}
"""

GETALL_TEMPLATE = """
    public synchronized Cursor getAll{classname}sCursor(final String selection,
                                                        final String[] args,
                                                        final String sortOrder) {{
        final SQLiteDatabase db = this.getReadableDatabase();

        final Cursor cursor = db.query({classname}.TABLE_NAME,
                {classname}.FIELDS, selection, args, null, null, sortOrder, null);

        return cursor;
    }}

    public synchronized List<{classname}> getAll{classname}s(final String selection,
                                                             final String[] args,
                                                             final String sortOrder) {{
        final List<{classname}> result = new ArrayList<{classname}>();

        final Cursor cursor = getAll{classname}sCursor(selection, args, sortOrder);

        while (cursor.moveToNext()) {{
            {classname} q = new {classname}(cursor);
            result.add(q);
        }}

        cursor.close();
        return result;
    }}
"""

HANDLER_TEMPLATE = """package com.example.appname.database;

import java.util.ArrayList;
import java.util.List;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;

/**
 * Database handler, SQLite wrapper and ORM layer.
 *
 */
public class {classname} extends SQLiteOpenHelper {{

    // All Static variables
    // Database Version
    private static final int DATABASE_VERSION = 1;

    // Database Name
    private static final String DATABASE_NAME = "{databasename}";
    private final Context context;

    private static DatabaseHandler instance = null;

    public synchronized static DatabaseHandler getInstance(Context context) {{
        if (instance == null)
            instance = new DatabaseHandler(context.getApplicationContext());
        return instance;
    }}

    public DatabaseHandler(Context context) {{
        super(context.getApplicationContext(), DATABASE_NAME, null,
                DATABASE_VERSION);
        this.context = context.getApplicationContext();
    }}

    @Override
    public void onOpen(SQLiteDatabase db) {{
        super.onOpen(db);
        if (!db.isReadOnly()) {{
            // Enable foreign key constraints
            // This line requires android16
            // db.setForeignKeyConstraintsEnabled(true);
            // This line works everywhere though
            db.execSQL("PRAGMA foreign_keys=ON;");
        }}
    }}

    @Override
    public synchronized void onCreate(SQLiteDatabase db) {{
        {create_tables}
    }}

    // Upgrading database
    @Override
    public synchronized void onUpgrade(SQLiteDatabase db, int oldVersion,
            int newVersion) {{
        // Try to drop and recreate. You should do something clever here
        onCreate(db);
    }}

    // Convenience methods
    public synchronized boolean putItem(final DBItem item) {{
        boolean success = false;
        int result = 0;
        final SQLiteDatabase db = this.getWritableDatabase();
        final ContentValues values = item.getContent();

        if (item.getId() > -1) {{
            result += db.update(item.getTableName(), values,
                    DBItem.COL_ID + " IS ?",
                    new String[] {{ String.valueOf(item.getId()) }});
        }}

        // Update failed or wasn't possible, insert instead
        if (result < 1) {{
            final long id = db.insert(item.getTableName(), null, values);

            if (id > 0) {{
                item.setId(id);
                success = true;
            }}
        }}
        else {{
            success = true;
        }}

        if (success) {{
            item.notifyProvider(context);
        }}
        return success;
    }}

    public synchronized int deleteItem(DBItem item) {{
        final SQLiteDatabase db = this.getWritableDatabase();
        final int result = db.delete(item.getTableName(), DBItem.COL_ID
                + " IS ?", new String[] {{ Long.toString(item.getId()) }});

        if (result > 0) {{
            item.notifyProvider(context);
        }}

        return result;
    }}

    {table_getters}
}}
"""
