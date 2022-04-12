#!/usr/bin/env python

#-----------------------------------------------------------------------
# details.py
# Author: Louis Pang
#-----------------------------------------------------------------------

from sqlite3 import connect
from contextlib import closing
from sys import stderr

#-----------------------------------------------------------------------

DATABASE_URL = 'file:reg.sqlite?mode=ro'

def detail(raw_input):
    class_id = int(raw_input)
    output = {}

    try:
        with connect(DATABASE_URL, isolation_level=None,
            uri=True) as connection:

            with closing(connection.cursor()) as cursor:
                # query for the courseid, days, starttime, endtime,
                # building and room number
                stmt = "SELECT classes.courseid, days, "
                stmt += "starttime, endtime, bldg, roomnum "
                stmt += "FROM classes WHERE classes.classid = ?"
                cursor.execute(stmt, [class_id])
                row = cursor.fetchone()

                # throwing an error if there is no class with that id
                # redundant now that course_id is taken from table
                if row is None:
                    # split string to reduce line length for pylint
                    str_out = 'regdetails.py: no class with '
                    str_out += 'classid {0} exists'
                    print(str_out.format(class_id), file=stderr)
                    return None

                course_id = row[0]

                output["courseid"] = row[0]
                output["days"] = row[1]
                output["start_time"] = row[2]
                output["end_time"] = row[3]
                output["building"] = row[4]
                output["room"] = row[5]

                # querying for the department and course number
                stmt = "SELECT dept, coursenum FROM crosslistings "
                stmt += "WHERE crosslistings.courseid = ? "
                stmt += "ORDER BY dept ASC, coursenum ASC"
                cursor.execute(stmt, [course_id])
                row = cursor.fetchone()
                depts = []
                coursenums = []
                while row is not None:
                    depts.append(row[0])
                    coursenums.append(row[1])
                    row = cursor.fetchone()

                output["departments"] = depts
                output["course numbers"] = coursenums

                # querying for area, title, description, and
                # prerequisites
                stmt = "SELECT area, title, descrip, prereqs "
                stmt += "FROM courses "
                stmt += "WHERE courses.courseid = ?"
                cursor.execute(stmt, [course_id])
                row = cursor.fetchone()

                output["area"] = row[0]
                output["title"] = row[1]
                output["description"] = row[2]
                output["prerequisites"] = row[3]

                # querying for the profIds
                stmt = "SELECT profid FROM coursesprofs "
                stmt += "WHERE coursesprofs.courseid = ?"
                cursor.execute(stmt, [course_id])
                row = cursor.fetchall()

                # querying for the professors using the profIds
                stmt = "SELECT profname FROM "
                stmt += "profs WHERE profs.profid = ?"
                stmt += "ORDER BY profname ASC"
                profs =[]
                for prof_id in row:
                    cursor.execute(stmt, prof_id)
                    row2 = cursor.fetchone()
                    profs.append(row2[0])

                output["professors"] = profs

        return output

    except TypeError:
        print('reg_details.py: no class with classid {0} exists'
            .format(class_id), file=stderr)
        return None

    except Exception as ex:
        print('reg_details.py: ' + str(ex), file=stderr)
        return None

#----------------------------------------------------------------------
