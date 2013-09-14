"""This class generates java classes for SQL tables that holds
the convenience methods for that table. An example generation
can be seen below where quite a simple table is created and
then a java OrmClass is generated.

>>> from db_table import Table, Column, ForeignKey, Unique

>>> t = Table('Album').cols(Column('_id').integer.primary_key,\
                            Column('albumname').text.not_null.default("''"), \
                            Column('artistname').text.not_null)\
.constraints(ForeignKey('artistname').references('artist', 'name')\
              .on_delete_cascade,\
             Unique('albumname').on_conflict_replace)

>>> print(get_orm_class(t))

"""
from db_table import Table

def get_orm_class(sql_table):
    '''Given an SQL table, generates a java ORM class.
    '''

    java_cols = map(JavaColumn, sql_table._columns)

    content_value_mapping = []
    for i, java_col in enumerate(java_cols):
        cursor_get = java_col.cursor_get
        content_value_mapping.append("this.{} = {};".format(java_col.var_name,
                                                           cursor_get.format(i)))

    return CLASS_TEMPLATE.format(
        table=sql_table,
        column_constants="\n    ".join([x.declare_const for x in java_cols]),
        column_constants_list=", ".join(x.const_name for x in java_cols),
        column_vars="\n    ".join([x.declare_var for x in java_cols]),
        column_field_from_cursor="\n        ".join(content_value_mapping),
        to_content_values="\n        "\
        .join(["values.put({}, {});"\
               .format(x.const_name, x.var_name) for x in java_cols]))

class JavaColumn(object):
    def __init__(self, sql_column):
        self.column = sql_column

    @property
    def declare_const(self):
        return COL_CONST_TEMPLATE.format(self.column)

    @property
    def var_name(self):
        return self.column.name

    @property
    def const_name(self):
        return "COL_" + self.column.upper_name

    @property
    def java_type(self):
        st = self.column.type

        if st == "INTEGER":
            return "long"
        elif st == "REAL":
            return "float"
        elif st == "TIMESTAMP":
            return "long"
        else:
            return "String"

    @property
    def cursor_get(self):
        base = "cursor.get{}({{}})"
        st = self.column.type

        if st == "INTEGER":
            return base.format("Long")
        elif st == "REAL":
            return base.format("Float")
        elif st == "TIMESTAMP":
            return base.format("Long")
        else:
            return base.format("String")


    @property
    def default_value(self):
        if "PRIMARY KEY" in self.column.constraint:
            return "= -1" #_id columns should have a non-null invalid value
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

COL_CONST_TEMPLATE = 'public static final String COL_{0.upper_name} = "{0.name}";'

CLASS_TEMPLATE = '''package com.example.appname.database;

import android.content.ContentValues;
import android.database.Cursor;

/**
 * Represents {table.name} in the database.
 *
 */
public class {table.name}Item {{
    public static final String TABLE_NAME = "{table.name}";
    // Column names
    {column_constants}

    // For database projection so order is consistent
    public static final String[] FIELDS = {{ {column_constants_list} }};

    {column_vars}

    public {table.name}Item() {{
    }}

    public {table.name}Item(final Cursor cursor) {{
        // Projection expected to match FIELDS array
        {column_field_from_cursor}
    }}

    public ContentValues getContent() {{
        ContentValues values = new ContentValues();
        {to_content_values}

        return values;
    }}

    public static final String CREATE_TABLE =
"{table}";
}}
'''
