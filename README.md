AndroidCodeGenerator
====================

This is a python module which generates Android classes. It is most useful for creating an initial database and contentprovider for a project.

I plan on adding all necessary classes for a database with a contentprovider to start with. More types
of classes might follow as I see a need for them.

The database structure is basically the same as the one I present in my [tutorial](https://github.com/spacecowboy/AndroidTutorialContentProvider).

Please see _sample.py_ for an example of how to generate all the database files and the
sample project in _/sample/_ where they are used. The sample is a modified version of the
tutorial project mentioned above so check that out for a preview of the app itself.

An example generation
can be seen below where quite a simple table is created and
then a java OrmClass is generated.

```python
from AndroidCodeGenerator.db_table import Table, Column, ForeignKey, Unique
from AndroidCodeGenerator.dbitem import DBItem

t = Table('Album').cols(Column('albumname').text.not_null.default("''"), \
                        Column('artistname').text.not_null)\
                  .constraints(ForeignKey('artistname').references('artist', 'name')\
                                         .on_delete_cascade,\
                               Unique('albumname').on_conflict_replace)

print(DBItem(t))
```

Result:

```java
package com.example.appname.database;

import android.content.ContentValues;
import android.content.UriMatcher;
import android.database.Cursor;
import android.net.Uri;

/**
 * Represents Album in the database.
 *
 */
public class AlbumItem extends DBItem {
    public static final String TABLE_NAME = "Album";

    public static Uri URI() {
        return Uri.withAppendedPath(
            Uri.parse(ItemProvider.SCHEME
                      + ItemProvider.AUTHORITY), TABLE_NAME);
    }

    // Column names
    public static final String COL__ID = "_id";
    public static final String COL_ALBUMNAME = "albumname";
    public static final String COL_ARTISTNAME = "artistname";

    // For database projection so order is consistent
    public static final String[] FIELDS = { COL__ID, COL_ALBUMNAME, COL_ARTISTNAME };

    public long _id = -1;
    public String albumname = "";
    public String artistname;

    public static final int BASEURICODE = 3993119;
    public static final int BASEITEMCODE = 1102568;

    public static void addMatcherUris(UriMatcher sURIMatcher) {
        sURIMatcher.addURI(ItemProvider.AUTHORITY, TABLE_NAME, BASEURICODE);
        sURIMatcher.addURI(ItemProvider.AUTHORITY, TABLE_NAME + "/#", BASEITEMCODE);
    }

    public static final String TYPE_DIR = "vnd.android.cursor.dir/vnd.example." + TABLE_NAME;
    public static final String TYPE_ITEM = "vnd.android.cursor.item/vnd.example." + TABLE_NAME;

    public AlbumItem() {
        super();
    }

    public AlbumItem(final Cursor cursor) {
        super();
        // Projection expected to match FIELDS array
        this._id = cursor.getLong(0);
        this.albumname = cursor.getString(1);
        this.artistname = cursor.getString(2);
    }

    public ContentValues getContent() {
        ContentValues values = new ContentValues();
        values.put(COL_ALBUMNAME, albumname);
        values.put(COL_ARTISTNAME, artistname);

        return values;
    }

    public String getTableName() {
        return TABLE_NAME;
    }

    public String[] getFields() {
        return FIELDS;
    }

    public long getId() {
        return _id;
    }

    public void setId(final long id) {
        _id = id;
    }

    public static final String CREATE_TABLE =
"CREATE TABLE Album"
+"  (_id INTEGER PRIMARY KEY,"
+"  albumname TEXT NOT NULL DEFAULT '',"
+"  artistname TEXT NOT NULL"
+""
+"  FOREIGN KEY (artistname) REFERENCES artist(name) ON DELETE CASCADE,"
+"  UNIQUE(albumname) ON CONFLICT REPLACE)";
}
```

The program can generate the java files directly, as follows:
```python
"""Generate a sample project"""

from AndroidCodeGenerator.generator import Generator
from AndroidCodeGenerator.db_table import Table, Column, ForeignKey, Unique

persons = Table('Person').cols(Column('firstname').text.not_null.default("''"),\
                               Column('lastname').text.not_null.default("''"),\
                               Column('bio').text.not_null.default("''"))

g = Generator(path='./sample/src/com/example/appname/database/')

g.add_tables(persons)

g.write()

```
