"""Generate a sample project"""

from AndroidCodeGenerator.generator import Generator
from AndroidCodeGenerator.db_table import Table, Column, ForeignKey, Unique

persons = Table('Person').add_cols(Column('firstname').text.not_null.default("''"),\
                               Column('lastname').text.not_null.default("''"),\
                               Column('bio').text.not_null.default("''"))


g = Generator(path='./sample/src/com/example/appname/database/')

g.add_tables(persons)

g.write()
