#!/usr/bin/env python

#-----------------------------------------------------------------------
# search.py
# Author: Louis Pang
#-----------------------------------------------------------------------

from sqlite3 import connect
from contextlib import closing
from sys import stderr

#-----------------------------------------------------------------------

DATABASE_URL = 'file:reg.sqlite?mode=ro'

#----------------------------------------------------------------------
# returns a tuple with the variables which the cursor will use
def format_input(tuple):
    tup = [tuple[0], tuple[1], tuple[2], tuple[3]]
    for i in range(4):
        if tup[i] is not None:
            tup[i] = tup[i].replace('%', ';%')
            tup[i] = tup[i].replace('_', ';_')
            tup[i] = '%' + tup[i] + '%'
        else:
            tup[i] = '%'
    # Use individual entries of arr to match type
    return [tup[0], tup[1], tup[2], tup[3]]

#----------------------------------------------------------------------

def overview_search(raw_input):
    if len(raw_input) != 4:
        str_out = 'Input is wrong length'
        print(str_out, file=stderr)
    output = []
    input_new = format_input(raw_input)

    print(input_new)

    try:
        with connect(DATABASE_URL, isolation_level=None,
        uri=True) as connection:

            with closing(connection.cursor()) as cursor:
                # the prepared statement for the query
                stmt_str="SELECT classid, dept, coursenum, area, title "
                stmt_str += "FROM classes, courses, crosslistings "
                stmt_str += "WHERE courses.courseid=classes.courseid "
                stmt_str += "AND courses."
                stmt_str += "courseid=crosslistings.courseid"
                stmt_str += " AND dept LIKE ? "
                stmt_str += "AND coursenum LIKE ? "
                stmt_str += "AND area LIKE ? "
                stmt_str += "AND title LIKE ? "
                stmt_str += "ESCAPE ';' ORDER BY "
                stmt_str += "dept ASC, coursenum ASC, classid ASC"

                print(stmt_str)

                cursor.execute(stmt_str, input_new)
                row = cursor.fetchone()
                while row is not None:
                    output.append(row)
                    row = cursor.fetchone()

        return output

    except TypeError:
        print('reg_overview.py: no class with classid {0} exists'
            .format(input_new[1]), file=stderr)
        return None

    except Exception as ex:
        print("reg_overview: " + str(ex), file=stderr)
        return None

#----------------------------------------------------------------------
