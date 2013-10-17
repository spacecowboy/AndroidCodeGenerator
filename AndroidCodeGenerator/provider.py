"""Generates the ContentProvider that matches the other files

>>> from db_table import Table, Column, ForeignKey, Unique

>>> from dbitem import DBItem

>>> pkg = "com.example.appname.database"
>>> t = Table('Album').add_cols(Column('albumname').text.not_null.default("''"), \
                               Column('artistname').text.not_null)\
.add_constraints(ForeignKey('artistname').references('artist', 'name')\
              .on_delete_cascade,\
             Unique('albumname').on_conflict_replace)

>>> p = Provider("MyProvider", pkg)
>>> p.add_dbitems(DBItem(t, pkg))
"""

from dbitem import DBItem
from database_handler import DatabaseHandler

class Provider(object):
    def __init__(self, classname, pkg):
        """Must specify pkg and classname"""
        self.pkg = pkg
        self.classname = classname
        self.dbitems = []

    def add_dbitems(self, *items):
        self.dbitems.extend(items)

    @property
    def match_uris(self):
        result = "\n        "\
                 .join([MATCH_URI_TEMPLATE\
                        .format(classname=item.classname) for item in self.dbitems])
        return result

    @property
    def match_types(self):
        #result = ""
        #for item in self.dbitems:
        result = "".join([MATCH_TYPE_TEMPLATE\
                          .format(classname=item.classname) for item in self.dbitems])
        return result

    @property
    def match_query(self):
        return "".join([MATCH_QUERY_TEMPLATE.format(classname=item.classname)\
                          for item in self.dbitems])

    @property
    def delete_cases(self):
        return "".join([DELETE_CASE_TEMPLATE.format(classname=item.classname)\
                        for item in self.dbitems])

    def __repr__(self):
      return PROVIDER_TEMPLATE.format(provider=self)

    @property
    def manifest_entry(self):
        return MANIFEST_TEMPLATE.format(self)

# When formatting this, just give a provider to format
MANIFEST_TEMPLATE = """<provider
    android:name="{0.pkg}.{0.classname}"
    android:authorities="{0.pkg}.AUTHORITY"
    android:enabled="true"
    android:exported="false" />
"""

MATCH_URI_TEMPLATE = "{classname}.addMatcherUris(sURIMatcher);"

MATCH_TYPE_TEMPLATE = """
        case {classname}.BASEITEMCODE:
            return {classname}.TYPE_ITEM;
        case {classname}.BASEURICODE:
            return {classname}.TYPE_DIR;"""

MATCH_QUERY_TEMPLATE = """
        case {classname}.BASEITEMCODE:
            id = Long.parseLong(uri.getLastPathSegment());
            result = handler.get{classname}Cursor(id);
            result.setNotificationUri(getContext().getContentResolver(), uri);
            break;
        case {classname}.BASEURICODE:
            result = handler.getAll{classname}sCursor(selection, args, sortOrder);
            result.setNotificationUri(getContext().getContentResolver(), uri);
            break;
"""

DELETE_CASE_TEMPLATE = """
        case {classname}.BASEITEMCODE:
            table = {classname}.TABLE_NAME;
            if (selection != null && !selection.isEmpty()) {{
                sb.append(" AND ");
            }}
            sb.append({classname}.COL_ID + " IS ?");
            args.add(uri.getLastPathSegment());
            // Alternative is this
            // values.put({classname}.COL_DELETED, 1);
            break;
"""

PROVIDER_TEMPLATE = """
package {provider.pkg};

import android.content.ContentProvider;
import android.content.ContentValues;
import android.content.UriMatcher;
import android.database.Cursor;
import android.net.Uri;

public class {provider.classname} extends ContentProvider {{
    public static final String AUTHORITY = "{provider.pkg}.AUTHORITY";
    public static final String SCHEME = "content://";

    private static final UriMatcher sURIMatcher = new UriMatcher(
            UriMatcher.NO_MATCH);
    static {{
        {provider.match_uris}
    }}

    @Override
    public boolean onCreate() {{
        return true;
    }}


    @Override
    public int delete(Uri uri, String selection, String[] selectionArgs) {{
        // Setup some common parsing and stuff
        final String table;
        final ContentValues values = new ContentValues();
        final ArrayList<String> args = new ArrayList<String>();
        if (selectionArgs != null) {{
            for (String arg : selectionArgs) {{
                args.add(arg);
            }}
        }}
        final StringBuilder sb = new StringBuilder();
        if (selection != null && !selection.isEmpty()) {{
            sb.append("(").append(selection).append(")");
        }}

        // Configure table and args depending on uri
        switch (sURIMatcher.match(uri)) {{
        {provider.delete_cases}
        default:
            throw new IllegalArgumentException("Unknown URI " + uri);
        }}

        // Write to DB
        final SQLiteDatabase db = DatabaseHandler.getInstance(getContext())
                .getWritableDatabase();
        final String[] argArray = new String[args.size()];
        final int result = db.delete(table, sb.toString(),
                args.toArray(argArray));
        // Or alternatively
        //final int result = db.update(table, values, sb.toString(),
        //        args.toArray(argArray));

        if (result > 0) {{
            // Support upload sync
            getContext().getContentResolver().notifyChange(uri, null, true);
        }}
        return result;
    }}

    @Override
    public Uri insert(Uri uri, ContentValues values) {{
        // TODO: Implement this to handle requests to insert a new row.
        throw new UnsupportedOperationException("Not yet implemented");
    }}

    @Override
    public int update(Uri uri, ContentValues values, String selection,
            String[] selectionArgs) {{
        // TODO: Implement this to handle requests to update one or more rows.
        throw new UnsupportedOperationException("Not yet implemented");
    }}

    @Override
    public String getType(Uri uri) {{
        switch (sURIMatcher.match(uri)) {{
        {provider.match_types}
        default:
            throw new IllegalArgumentException("Unknown URI " + uri);
        }}
    }}

    @Override
    public Cursor query(Uri uri, String[] projection, String selection,
            String[] args, String sortOrder) {{
        Cursor result = null;
        final long id;
        final DatabaseHandler handler = DatabaseHandler.getInstance(getContext());

        switch (sURIMatcher.match(uri)) {{
        {provider.match_query}
        default:
            throw new IllegalArgumentException("Unknown URI " + uri);
        }}

        return result;
    }}
}}
"""
