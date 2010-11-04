#!/bin/sh
#
# runAll.sh
#
#   Last modified: 2010-11-03 RJH
#
# Run xmllint on all the XML files in the DataFiles folder
# Then run Python code for each module
#
# Run xmllint on all the XML files in the DataFiles folder
sh checkAll.sh

echo "Running Python modules..."

python3 iso_639_3.py --convert
python3 BibleBooksCodes.py --convert
python3 BibleOrganizationalSystems.py

echo "Testing .py table files..."
python3 DerivedFiles/iso_639_3Tables.py
python3 DerivedFiles/BibleBooksCodesTables.py

echo "Testing compilation of .h files..."
cc include_test.c
