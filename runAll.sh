#!/bin/sh
#
# runAll.sh
#
#   Last modified: 2010-11-26 / RJH
#
# Run xmllint on all the XML files in the DataFiles folder
# Then run Python code for each module
#
# Run xmllint on all the XML files in the DataFiles folder
sh checkAll.sh

echo "Running Python modules..."

python3 ISO_639_3.py
python3 BibleBooksCodes.py
python3 BibleChaptersVerses.py
python3 BibleBookOrders.py
python3 BibleBooksNames.py
python3 BibleOrganizationalSystems.py

echo "Running Python module exports..."

python3 ISO_639_3.py --export
python3 BibleBooksCodes.py --export
python3 BibleChaptersVerses.py --export
python3 BibleBookOrders.py --export
python3 BibleBooksNames.py --export
python3 BibleOrganizationalSystems.py --export

#python3 BibleChaptersVerses.py --scrape
#python3 BibleOrganizationalSystems.py --scrape

echo "Testing .py table files..."
python3 DerivedFiles/iso_639_3_Tables.py
python3 DerivedFiles/BibleBooksCodes_Tables.py
python3 DerivedFiles/BibleBookOrders_Tables.py
python3 DerivedFiles/BibleBooksNames_Tables.py

echo "Testing compilation of .h files..."
cc include_test.c
