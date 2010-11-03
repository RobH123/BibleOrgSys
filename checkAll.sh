#!/bin/sh
#
# CheckAll.sh
#
#   Last modified: 2010-11-03 RJH
#
# Run xmllint on all the XML files in the DataFiles folder
#
# First ensure that the RelaxNG schema files are all up-to-date
sh trangAll.sh

echo "Checking xml files for consistency..."

xmllint --noout --relaxng DerivedFiles/iso_639_3.rng --valid DataFiles/iso_639_3.xml
xmllint --noout --relaxng DerivedFiles/BibleBooksCodes.rng --valid DataFiles/BibleBooksCodes.xml
xmllint --noout --relaxng DerivedFiles/BibleBooksNames.rng --valid DataFiles/BibleBooksNames.xml
xmllint --noout --relaxng DerivedFiles/BibleOrganizationalSystems.rng --valid DataFiles/BibleOrganizationalSystems.xml

xmllint --noout --relaxng DerivedFiles/BibleVersificationSystem.rng --valid DataFiles/BibleVersificationSystem.English.xml
xmllint --noout --relaxng DerivedFiles/BibleVersificationSystem.rng --valid DataFiles/BibleVersificationSystem.DutchTraditional.xml
xmllint --noout --relaxng DerivedFiles/BibleVersificationSystem.rng --valid DataFiles/BibleVersificationSystem.Original.xml
xmllint --noout --relaxng DerivedFiles/BibleVersificationSystem.rng --valid DataFiles/BibleVersificationSystem.RussianCanonical.xml
xmllint --noout --relaxng DerivedFiles/BibleVersificationSystem.rng --valid DataFiles/BibleVersificationSystem.RussianOrthodox.xml
xmllint --noout --relaxng DerivedFiles/BibleVersificationSystem.rng --valid DataFiles/BibleVersificationSystem.Septuagint.xml
xmllint --noout --relaxng DerivedFiles/BibleVersificationSystem.rng --valid DataFiles/BibleVersificationSystem.Spanish.xml
xmllint --noout --relaxng DerivedFiles/BibleVersificationSystem.rng --valid DataFiles/BibleVersificationSystem.Vulgate.xml
