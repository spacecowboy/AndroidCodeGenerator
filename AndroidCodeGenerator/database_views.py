from db_table import View

class DatabaseViews(object):
    """Creates DatabaseView.java

    Examples:

    """

    def __init__(self, pkg):
        self.pkg = pkg
        self.views = []

    def add(self, *views):
        self.views.extend(views)

    def __repr__(self):
        return _J_T.format(self)

    @property
    def create_perm(self):
        result = ""
        for view in self.views:
            if not view.is_temp:
                result += _C_P.format(view)
        return result.strip()

    @property
    def create_temp(self):
        result = ""
        for view in self.views:
            if view.is_temp:
                result += _C_T.format(view)
        return result.strip()

    @property
    def def_views(self):
        result = ""
        for view in self.views:
            result += _D_T.format(view)

        return result.strip()

_D_T = '''
    private static final String {0.name} =
"{0.java_string}";'''

_C_P = '''
        db.execSQL("DROP VIEW IF EXISTS {0.name}";
        db.execSQL({0.name});
'''

_C_T = '''        db.execSQL({0.name});'''


_J_T = '''package {0.pkg};

import android.database.sqlite.SQLiteDatabase;

public class DatabaseViews {{

    /**
     * Create permanent views. They are dropped first,
     * if they already exist.
     */
    public static void create(final SQLiteDatabase db) {{
        {0.create_perm}
    }}

    /**
     * Create temporary views. Nothing is done if they
     * already exist.
     */
    public static void createTemp(final SQLiteDatabase db) {{
        {0.create_temp}
    }}

    {0.def_views}
}}'''
