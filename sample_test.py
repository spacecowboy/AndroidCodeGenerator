
from AndroidCodeGenerator.generator import Generator
from AndroidCodeGenerator.db_table import (Table, Column, ForeignKey, Unique,
                                           Trigger)
from AndroidCodeGenerator.database_triggers import DatabaseTriggers
from AndroidCodeGenerator.sql_validator import SQLTester

persons = Table('Person').add_cols(Column('firstname').text.not_null.default("''"),\
                               Column('lastname').text.not_null.default("''"),\
                               Column('bio').text.not_null.default("''"))\
                         .add_constraints(Unique('firstname').on_conflict_replace)

log = Table('Log').add_cols(Column('pId').integer.not_null,
                        Column('firstname').text.not_null,
                        Column('lastname').text.not_null,
                        Column('bio').text.not_null,
                        Column('time').timestamp.default_current_timestamp)

# Create a trigger that keeps the log up to date
# I recommend using temp triggers unless you see a performance hit
trigger = Trigger('tr_log').temp.if_not_exists

# Here I have given the wrong table name on purpose. Notice that the sql
# creation will fail because there is no table named bob.
trigger.after.update_on("bob")
#trigger.after.update_on(log.name)

# Raw sql
trigger.do_sql("INSERT INTO {table} ({cols}) VALUES\
 ({oldcols})".format(table=log.name,
                     cols=log.list_column_names(exclude=['_id','time']),
                     oldcols=persons.list_column_names(exclude=[],
                                                       prefix="old.")))

# Let's try to create the SQL
st = SQLTester()
st.add_tables(persons, log)
st.add_triggers(trigger)

st.test_create()
