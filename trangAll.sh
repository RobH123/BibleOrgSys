#!/bin/sh
#
# trangAll.sh
#
#   Last modified: 2010-11-12 RJH
#
# Create the rng files for the RNC schema files in the DataFiles folder
#
echo "Creating RelaxNG files from rnc files..."

trang DataFiles/iso_639_3.rnc DerivedFiles/iso_639_3.rng
trang DataFiles/BibleBooksCodes.rnc DerivedFiles/BibleBooksCodes.rng
trang DataFiles/VersificationSystems/BibleVersificationSystem.rnc DerivedFiles/BibleVersificationSystem.rng
trang DataFiles/BookOrders/BibleBookOrder.rnc DerivedFiles/BibleBookOrder.rng
trang DataFiles/BookNames/BibleBooksNames.rnc DerivedFiles/BibleBooksNames.rng
trang DataFiles/BibleOrganizationalSystems.rnc DerivedFiles/BibleOrganizationalSystems.rng
