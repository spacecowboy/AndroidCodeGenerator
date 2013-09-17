"""Generate a sample project with triggers"""

from AndroidCodeGenerator.generator import Generator
from AndroidCodeGenerator.db_table import (Table, Column, ForeignKey, Unique,
                                           Trigger)

living = Table('LivePerson').cols(Column('firstname').text.not_null.default("''"),\
                                   Column('lastname').text.not_null.default("''"),\
                                   Column('bio').text.not_null.default("''"))

dead = Table('DeadPerson').cols(Column('firstname').text.not_null.default("''"),\
                                   Column('lastname').text.not_null.default("''"),\
                                   Column('bio').text.not_null.default("''"))

# Generate a trigger that copies living people to the list of dead people
# automatically when they are deleted from the living table.

trigger = Trigger('death').temp.if_not_exists

trigger.instead_of.after.before

trigger.update_on(living.name).update_on(living.name, *[x.name for x in living._columns])
trigger.insert_on(living.name)

trigger.delete_on(living.name)

# Raw sql
trigger.do_sql("INSERT INTO {tablename} ({cols}) VALUES\
 ({oldcols})".format(tablename=dead.name,
                     cols=dead.list_column_names(),
                     oldcols=living.list_column_names(prefix="old.")))

print(trigger)

#g = Generator(path='./sample/src/com/example/appname/database/')

#g.write()
