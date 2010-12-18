#!/bin/sh
#
# runAll.sh
#
#   Last modified: 2010-12-16 by RJH
#
# Run xmllint on all the XML files in the DataFiles folder
# Then run Python code for each module
#

# Run xmllint on all the XML files in the DataFiles folder
sh checkAll.sh

Python="python3"

echo "Running Python modules in demo mode..."
$Python ISO_639_3_Languages.py
$Python BibleBooksCodes.py
$Python BibleChaptersVerses.py
$Python BibleBookOrders.py
$Python BibleBooksNames.py
$Python BibleOrganizationalSystems.py

echo "Running Python module exports..."
$Python ISO_639_3_Languages.py --export
$Python BibleBooksCodes.py --export
$Python BibleChaptersVerses.py --export
$Python BibleBookOrders.py --export
$Python BibleBooksNames.py --export
$Python BibleOrganizationalSystems.py --export

#$Python BibleChaptersVerses.py --scrape
#$Python BibleOrganizationalSystems.py --scrape

echo "Testing .py table files..."
# These should all give no output (no errors)
$Python DerivedFiles/iso_639_3_Languages_Tables.py
$Python DerivedFiles/BibleBooksCodes_Tables.py
$Python DerivedFiles/BibleBookOrders_Tables.py
$Python DerivedFiles/BibleBooksNames_Tables.py

Compile="gcc -c"

echo "Testing compilation of .c files..."
# These should all give no output (no errors)
$Compile DerivedFiles/iso_639_3_Languages_Tables.c
$Compile DerivedFiles/BibleBooksCodes_Tables.c
$Compile DerivedFiles/BibleBookOrders_Tables.c
$Compile DerivedFiles/BibleBooksNames_Tables.c

