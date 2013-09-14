"""Generate a sample project"""

from AndroidCodeGenerator.generator import Generator
from AndroidCodeGenerator.db_table import Table, Column, ForeignKey, Unique

artists = Table('Artist').cols(Column('artistname').text.not_null.default("''"),\
                               Column('label').text.not_null.default("''"))\
                         .constraints(Unique('artistname').on_conflict_replace)

albums = Table('Album').cols(Column('albumname').text.not_null.default("''"), \
                             Column('artistid').integer)\
                        .constraints(ForeignKey('artist')\
                                     .references('artist')\
                                     .on_delete_cascade,\
                                     Unique('albumname').on_conflict_replace)

persons = Table('Person').cols(Column('firstname').text.not_null.default("''"),\
                               Column('lastname').text.not_null.default("''"),\
                               Column('bio').text.not_null.default("''"))
                         #.constraints(Unique('firstname').on_conflict_replace\


g = Generator(path='./sample/src/com/example/appname/database/')

g.add_tables(persons)
#g.add_tables(artists)
#g.add_tables(albums)


g.write()
