import MySQLdb
db = MySQLdb.connect(host="localhost", user="metabolomics", passwd="metabolomics", db="metabolomics")
c = db.cursor()

import sqlalchemy.types
from db_objects import *
from copy import copy
import xml.etree.cElementTree as ET #permits xml parsing trees
import sys

import csv


def main():
    fh = open("Fecal-meatbolites.csv", "r")
    f = csv.reader(fh)

    f.next()
    f.next()

    res = []
    stack = []
    for r in f:
        if len(r[0]) > 0:
            if len(stack) > 0:
                res.append(stack)
            stack = []
        stack.append(r)
    res.append(stack)

    mapping = []

    for r in res:
        print r[0][2]
        if len(r[0][2]) == 0:
            continue
        q = "select metabolite_id, hmdb_id from hmdb_metabolites where hmdb_id = '%s'" % r[0][2]
        print q
        cursor.execute(q)
        dbr = cursor.fetchall()
        if len(dbr) > 0:
            print dbr
            mapping.append(dbr[0])
            q = "insert into fecal_metabolites (metabolite_id, hmdb_id) values (%s, '%s') " %  ( dbr[0][0], dbr[0][1] )
            cursor.execute(q)
        mydb.commit()

    print mapping


if __name__ == "__main__":
    main()

