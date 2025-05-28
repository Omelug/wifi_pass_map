"""
Motivation download database from https://3wifi.dev/dbs.html and
make small passwords lists for each country

1 - Download p3wifi database from megaupload
2 - Load it to mysql
3 - downaload geojson polygons

Options:
A - make country specific database
B - generate wifi worldlist for country
    Ba(with count)
    Bb(without count)
C - generate wifi worldlist for all countries

"""

"""
:argument
 cc - country code
 i/import - path to folder/sql file
 o/output - path to folder
"""

if __name__ == "__main__":

    print("This is for get data from ")