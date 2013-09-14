AndroidCodeGenerator
====================

This is a python module which generates Android classes. It is most useful for creating an initial database and contentprovider for a project.

I plan on adding all necessary classes for a database with a contentprovider to start with. More types
of classes might follow as I see a need for them.

The database structure is basically the same as the one I present in my [tutorial](https://github.com/spacecowboy/AndroidTutorialContentProvider).

An example generation
can be seen below where quite a simple table is created and
then a java OrmClass is generated.

```python
    from db_table import Table, Column, ForeignKey, Unique

    t = Table('Album').cols(Column('_id').integer.primary_key,\
                            Column('albumname').text.not_null.default("''"), \
                            Column('artistname').text.not_null)\
    .constraints(ForeignKey('artistname').references('artist', 'name')\
              .on_delete_cascade,\
             Unique('albumname').on_conflict_replace)

    get_orm_class(t)
```

Result:

```java
    package com.example.appname.database;

    import android.content.ContentValues;
    import android.database.Cursor;

    /**
     * Represents Album in the database.
     *
     */
    public class AlbumItem {
        public static final String TABLE_NAME = "Album";
        // Column names
        public static final String COL__ID = "_id";
        public static final String COL_ALBUMNAME = "albumname";
        public static final String COL_ARTISTNAME = "artistname";

        // For database projection so order is consistent
        public static final String[] FIELDS = { COL__ID, COL_ALBUMNAME, COL_ARTISTNAME };

        public long _id = -1;
        public String albumname = "";
        public String artistname;

        public AlbumItem() {
        }

        public AlbumItem(final Cursor cursor) {
            // Projection expected to match FIELDS array
            this._id = cursor.getLong(0);
            this.albumname = cursor.getString(1);
            this.artistname = cursor.getString(2);
        }

        public ContentValues getContent() {
            ContentValues values = new ContentValues();
            values.put(COL__ID, _id);
            values.put(COL_ALBUMNAME, albumname);
            values.put(COL_ARTISTNAME, artistname);

            return values;
        }

        public static final String CREATE_TABLE =
    "CREATE TABLE Album
      (_id INTEGER PRIMARY KEY,
      albumname TEXT NOT NULL DEFAULT '',
      artistname TEXT NOT NULL

      FOREIGN KEY (artistname) REFERENCES artist(name) ON DELETE CASCADE,
      UNIQUE(albumname) ON CONFLICT REPLACE)";
    }
```
