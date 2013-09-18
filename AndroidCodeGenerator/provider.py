"""Generates the ContentProvider that matches the other files

>>> from db_table import Table, Column, ForeignKey, Unique

>>> from dbitem import DBItem

>>> t = Table('Album').add_cols(Column('albumname').text.not_null.default("''"), \
                               Column('artistname').text.not_null)\
.add_constraints(ForeignKey('artistname').references('artist', 'name')\
              .on_delete_cascade,\
             Unique('albumname').on_conflict_replace)

>>> p = Provider(DBItem(t))

"""

from dbitem import DBItem
from database_handler import DatabaseHandler

class Provider(object):
    def __init__(self, *items, **kwargs):
        self.pkg = "com.example.appname.database"
        if 'pkg' in kwargs:
            self.pkg = kwargs['pkg']
        self.dbitems = []
        if items is not None and len(items) > 0:
            self.add_dbitems(*items)

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
        result = "".join([MATCH_QUERY_TEMPLATE\
                          .format(classname=item.classname) for item in self.dbitems])
        return result

    @property
    def classname(self):
        return "ItemProvider";

    def __repr__(self):
      return PROVIDER_TEMPLATE.format(provider=self)

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

PROVIDER_TEMPLATE = """
package {provider.pkg};

import android.content.ContentProvider;
import android.content.ContentValues;
import android.content.UriMatcher;
import android.database.Cursor;
import android.net.Uri;

public class {provider.classname} extends ContentProvider {{
    public static final String AUTHORITY = "com.example.appname.AUTHORITY";
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
        // Implement this to handle requests to delete one or more rows.
        throw new UnsupportedOperationException("Not yet implemented");
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
