"""This class generates java classes for SQL tables that holds
the convenience methods for that table. An example generation
can be seen below where quite a simple table is created and
then a java OrmClass is generated.

>>> from db_table import Table, Column, ForeignKey, Unique

>>> t = Table('Album').add_cols(Column('albumname').text.not_null.default("''"), \
                                Column('artistname').text.not_null)\
.add_constraints(ForeignKey('artistname').references('artist', 'name')\
              .on_delete_cascade,\
             Unique('albumname').on_conflict_replace)

>>> dbitem = DBItem(t, pkg="com.ex.app.db")

"""
from hashlib import sha1
from db_table import Table

class DBItem(object):
    """Generates an ORM class for the given table"""

    def __init__(self, sql_table, pkg):
        self.sql_table = sql_table
        self.pkg = pkg

    def __repr__(self):
        java_cols = map(JavaColumn, self.sql_table._columns)

        content_value_mapping = []
        for i, java_col in enumerate(java_cols):
            cursor_get = java_col.cursor_get
            content_value_mapping.append("this.{} = {};".format(java_col.var_name,
                                                                cursor_get.format(i)))

        return CLASS_TEMPLATE.format(
                table=self.sql_table,
                pkg=self.pkg,
                sqltable='"\n+"'.join(str(self.sql_table).split('\n')),
                classname=self.classname,
                baseurihash=self.baseurihash,
                baseitemhash=self.baseitemhash,
                column_constants="\n    ".join([x.declare_const for x in java_cols]),
                column_constants_list=", ".join([x.const_name for x in java_cols]),
        column_vars="\n    ".join([x.declare_var for x in java_cols]),
                column_field_from_cursor="\n        ".join(content_value_mapping),
                to_content_values=self.to_content_values)

    @property
    def to_content_values(self):
        java_cols = map(JavaColumn, self.sql_table._columns)
        no_id = []
        for x in java_cols:
            if x.var_name != "_id":
                no_id.append(x)

        result = ""
        sep = "\n        "
        for java_col in no_id:
            if 'NOT NULL' in java_col.column.constraint:
                simple = True
            else:
                simple = False

            if "CURRENT_" in java_col.column.constraint:
                # Timestamp, special case here
                result = \
                sep.join([result,
                          "if ({1} != null)\
 values.put({0}, {1});".format(java_col.const_name,
                               java_col.var_name)])
            elif simple:
                result = \
                sep.join([result,
                          "values.put({0}, {1});".format(java_col.const_name,
                                                         java_col.var_name)])
            else:
                result = \
                sep.join([result,
                          "if ({1} != null) {{\n\
            values.put({0}, {1});\n\
        }} else {{\n\
            values.putNull({0});\n\
        }}".format(java_col.const_name,
                   java_col.var_name)])


        return result
#        return "\n        "\
#                .join(["values.put({}, {});"\
#                       .format(x.const_name, x.var_name) for x in no_id])

    @property
    def classname(self):
        return "{0.name}Item".format(self.sql_table)

    @property
    def baseurihash(self):
        s = sha1(self.classname)
        s.update("baseuri")
        return "0x" + s.hexdigest()[:7]

    @property
    def baseitemhash(self):
        s = sha1(self.classname)
        s.update("baseitem")
        return "0x" + s.hexdigest()[:7]

class JavaColumn(object):
    def __init__(self, sql_column):
        self.column = sql_column

    @property
    def declare_const(self):
        return COL_CONST_TEMPLATE.format(self.const_name,
                                         self.var_name)

    @property
    def var_name(self):
        return self.column.name

    @property
    def const_name(self):
        name = self.column.upper_name
        while name.startswith("_"):
            name = name[1:]
        return "COL_" + name

    @property
    def java_type(self):
        st = self.column.type

        if 'NOT NULL' in self.column.constraint:
            simple = True
        else:
            simple = False

        if st == "INTEGER":
            return "long" if simple else "Long"
        elif st == "REAL":
            return "float" if simple else "Float"
        elif st == "TIMESTAMP":
            return "String"
        else:
            return "String"

    @property
    def cursor_get(self):
        # Double braces are converted to single braces at the end of
        # function.
        base = "cursor.get{0}({{0}})"

        if ('NOT NULL' not in self.column.constraint
            and self.column.name != "_id"):
            base = "cursor.isNull({{0}}) ? null : cursor.get{0}({{0}})"

        st = self.column.type

        if st == "INTEGER":
            return base.format("Long")
        elif st == "REAL":
            return base.format("Float")
        elif st == "TIMESTAMP":
            return base.format("String")
        else:
            return base.format("String")


    @property
    def default_value(self):
        if "PRIMARY KEY" in self.column.constraint:
            return "= -1" #_id columns should have a non-null invalid value
        elif "CURRENT_" in self.column.constraint:
            return "= null"
        elif "DEFAULT" in self.column.constraint:
            val = self.column.constraint\
                  .replace('PRIMARY KEY', '')\
                  .replace('NOT NULL', '')\
                  .replace('DEFAULT', '', 1)\
                  .replace("'", '"').strip()
            return "= {}".format(val)
        else:
            # No need to define a default value
            return ""

    @property
    def declare_var(self):
        return "public {0.java_type} {0.var_name} {0.default_value}"\
               .format(self).strip() + ";"

COL_CONST_TEMPLATE = 'public static final String {0} = "{1}";'

CLASS_TEMPLATE = '''package {pkg};

import android.content.ContentValues;
import android.content.UriMatcher;
import android.database.Cursor;
import android.net.Uri;

/**
 * Represents {table.name} in the database.
 *
 */
public class {classname} extends DBItem {{
    public static final String TABLE_NAME = "{table.name}";

    public static Uri URI() {{
        return Uri.withAppendedPath(
            Uri.parse(ItemProvider.SCHEME
                      + ItemProvider.AUTHORITY), TABLE_NAME);
    }}

    // Column names
    {column_constants}

    // For database projection so order is consistent
    public static final String[] FIELDS = {{ {column_constants_list} }};

    {column_vars}

    public static final int BASEURICODE = {baseurihash};
    public static final int BASEITEMCODE = {baseitemhash};

    public static void addMatcherUris(UriMatcher sURIMatcher) {{
        sURIMatcher.addURI(ItemProvider.AUTHORITY, TABLE_NAME, BASEURICODE);
        sURIMatcher.addURI(ItemProvider.AUTHORITY, TABLE_NAME + "/#", BASEITEMCODE);
    }}

    public static final String TYPE_DIR = "vnd.android.cursor.dir/vnd.{pkg}." + TABLE_NAME;
    public static final String TYPE_ITEM = "vnd.android.cursor.item/vnd.{pkg}." + TABLE_NAME;

    public {classname}() {{
        super();
    }}

    public {classname}(final Cursor cursor) {{
        super();
        // Projection expected to match FIELDS array
        {column_field_from_cursor}
    }}

    public ContentValues getContent() {{
        ContentValues values = new ContentValues();
        {to_content_values}

        return values;
    }}

    public String getTableName() {{
        return TABLE_NAME;
    }}

    public String[] getFields() {{
        return FIELDS;
    }}

    public long getId() {{
        return _id;
    }}

    public void setId(final long id) {{
        _id = id;
    }}

    public static final String CREATE_TABLE =
"{sqltable}";
}}
'''

DBITEM_CLASS = '''package {pkg};

import android.content.Context;
import android.content.ContentValues;
import android.database.Cursor;
import android.net.Uri;

public abstract class DBItem {{
    public static final String COL_ID = "_id";

    public DBItem() {{}}

    public DBItem(final Cursor cursor) {{}}

    public abstract ContentValues getContent();

    public abstract String getTableName();

    public abstract long getId();

    public abstract void setId(final long id);

    public abstract String[] getFields();

    public Uri getUri() {{
        return Uri.withAppendedPath(getBaseUri(), Long.toString(getId()));
    }}

    public Uri getBaseUri() {{
        return Uri.withAppendedPath(
            Uri.parse(ItemProvider.SCHEME
                      + ItemProvider.AUTHORITY), getTableName());
    }}

    public void notifyProvider(final Context context) {{
        try {{
            context.getContentResolver().notifyChange(getUri(), null, false);
        }}
        catch (UnsupportedOperationException e) {{
           // Catch this for test suite. Mock provider cant notify
        }}
    }}

}}
'''
