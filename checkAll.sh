#!/bin/sh
#
# checkAll.sh
#
#   Last modified: 2010-11-12 RJH
#
# Run xmllint on all the XML files in the DataFiles folder
#
# First ensure that the RelaxNG schema files are all up-to-date
sh trangAll.sh

echo "Checking xml files for consistency..."

xmllint --noout --relaxng DerivedFiles/iso_639_3.rng --valid DataFiles/iso_639_3.xml
xmllint --noout --relaxng DerivedFiles/BibleBooksCodes.rng --valid DataFiles/BibleBooksCodes.xml
xmllint --noout --relaxng DerivedFiles/BibleOrganizationalSystems.rng --valid DataFiles/BibleOrganizationalSystems.xml

xmllint --noout --relaxng DerivedFiles/BibleVersificationSystem.rng --valid DataFiles/VersificationSystems/BibleVersificationSystem_Original.xml
xmllint --noout --relaxng DerivedFiles/BibleVersificationSystem.rng --valid DataFiles/VersificationSystems/BibleVersificationSystem_English.xml
xmllint --noout --relaxng DerivedFiles/BibleVersificationSystem.rng --valid DataFiles/VersificationSystems/BibleVersificationSystem_Catholic.xml
xmllint --noout --relaxng DerivedFiles/BibleVersificationSystem.rng --valid DataFiles/VersificationSystems/BibleVersificationSystem_Catholic2.xml
xmllint --noout --relaxng DerivedFiles/BibleVersificationSystem.rng --valid DataFiles/VersificationSystems/BibleVersificationSystem_DutchTraditional.xml
xmllint --noout --relaxng DerivedFiles/BibleVersificationSystem.rng --valid DataFiles/VersificationSystems/BibleVersificationSystem_KJV.xml
xmllint --noout --relaxng DerivedFiles/BibleVersificationSystem.rng --valid DataFiles/VersificationSystems/BibleVersificationSystem_NRSV.xml
xmllint --noout --relaxng DerivedFiles/BibleVersificationSystem.rng --valid DataFiles/VersificationSystems/BibleVersificationSystem_GNT92.xml
xmllint --noout --relaxng DerivedFiles/BibleVersificationSystem.rng --valid DataFiles/VersificationSystems/BibleVersificationSystem_GNTUK.xml
xmllint --noout --relaxng DerivedFiles/BibleVersificationSystem.rng --valid DataFiles/VersificationSystems/BibleVersificationSystem_NIV84.xml
xmllint --noout --relaxng DerivedFiles/BibleVersificationSystem.rng --valid DataFiles/VersificationSystems/BibleVersificationSystem_NLT96.xml
xmllint --noout --relaxng DerivedFiles/BibleVersificationSystem.rng --valid DataFiles/VersificationSystems/BibleVersificationSystem_NRS89.xml
xmllint --noout --relaxng DerivedFiles/BibleVersificationSystem.rng --valid DataFiles/VersificationSystems/BibleVersificationSystem_REB89.xml
xmllint --noout --relaxng DerivedFiles/BibleVersificationSystem.rng --valid DataFiles/VersificationSystems/BibleVersificationSystem_RSV52.xml
xmllint --noout --relaxng DerivedFiles/BibleVersificationSystem.rng --valid DataFiles/VersificationSystems/BibleVersificationSystem_Luther.xml
xmllint --noout --relaxng DerivedFiles/BibleVersificationSystem.rng --valid DataFiles/VersificationSystems/BibleVersificationSystem_RussianCanonical.xml
xmllint --noout --relaxng DerivedFiles/BibleVersificationSystem.rng --valid DataFiles/VersificationSystems/BibleVersificationSystem_RussianOrthodox.xml
xmllint --noout --relaxng DerivedFiles/BibleVersificationSystem.rng --valid DataFiles/VersificationSystems/BibleVersificationSystem_Septuagint.xml
xmllint --noout --relaxng DerivedFiles/BibleVersificationSystem.rng --valid DataFiles/VersificationSystems/BibleVersificationSystem_SeptuagintBE.xml
xmllint --noout --relaxng DerivedFiles/BibleVersificationSystem.rng --valid DataFiles/VersificationSystems/BibleVersificationSystem_Spanish.xml
xmllint --noout --relaxng DerivedFiles/BibleVersificationSystem.rng --valid DataFiles/VersificationSystems/BibleVersificationSystem_Synodal.xml
xmllint --noout --relaxng DerivedFiles/BibleVersificationSystem.rng --valid DataFiles/VersificationSystems/BibleVersificationSystem_Vulgate.xml
xmllint --noout --relaxng DerivedFiles/BibleVersificationSystem.rng --valid DataFiles/VersificationSystems/BibleVersificationSystem_Vulgate2.xml
xmllint --noout --relaxng DerivedFiles/BibleVersificationSystem.rng --valid DataFiles/VersificationSystems/BibleVersificationSystem_Cebuano_BUGV.xml

xmllint --noout --relaxng DerivedFiles/BibleBookOrder.rng --valid DataFiles/BookOrders/BibleBookOrder_EuropeanProtestantOT.xml
xmllint --noout --relaxng DerivedFiles/BibleBookOrder.rng --valid DataFiles/BookOrders/BibleBookOrder_EuropeanProtestantNT.xml
xmllint --noout --relaxng DerivedFiles/BibleBookOrder.rng --valid DataFiles/BookOrders/BibleBookOrder_EuropeanProtestantBible.xml
xmllint --noout --relaxng DerivedFiles/BibleBookOrder.rng --valid DataFiles/BookOrders/BibleBookOrder_ArmenianNT.xml
xmllint --noout --relaxng DerivedFiles/BibleBookOrder.rng --valid DataFiles/BookOrders/BibleBookOrder_EthiopianNT.xml
xmllint --noout --relaxng DerivedFiles/BibleBookOrder.rng --valid DataFiles/BookOrders/BibleBookOrder_EthiopianProtestantOT.xml
xmllint --noout --relaxng DerivedFiles/BibleBookOrder.rng --valid DataFiles/BookOrders/BibleBookOrder_EthiopianProtestantBible.xml
xmllint --noout --relaxng DerivedFiles/BibleBookOrder.rng --valid DataFiles/BookOrders/BibleBookOrder_GutenbergNT.xml
xmllint --noout --relaxng DerivedFiles/BibleBookOrder.rng --valid DataFiles/BookOrders/BibleBookOrder_HebrewLetteris.xml
xmllint --noout --relaxng DerivedFiles/BibleBookOrder.rng --valid DataFiles/BookOrders/BibleBookOrder_HebrewStuttgart.xml
xmllint --noout --relaxng DerivedFiles/BibleBookOrder.rng --valid DataFiles/BookOrders/BibleBookOrder_LatinNT.xml
xmllint --noout --relaxng DerivedFiles/BibleBookOrder.rng --valid DataFiles/BookOrders/BibleBookOrder_LutheranNT.xml
xmllint --noout --relaxng DerivedFiles/BibleBookOrder.rng --valid DataFiles/BookOrders/BibleBookOrder_LXX.xml
xmllint --noout --relaxng DerivedFiles/BibleBookOrder.rng --valid DataFiles/BookOrders/BibleBookOrder_ModernJewish.xml
xmllint --noout --relaxng DerivedFiles/BibleBookOrder.rng --valid DataFiles/BookOrders/BibleBookOrder_SlavonicNT.xml
xmllint --noout --relaxng DerivedFiles/BibleBookOrder.rng --valid DataFiles/BookOrders/BibleBookOrder_SyriacNT.xml
xmllint --noout --relaxng DerivedFiles/BibleBookOrder.rng --valid DataFiles/BookOrders/BibleBookOrder_Vulgate.xml

xmllint --noout --relaxng DerivedFiles/BibleBooksNames.rng --valid DataFiles/BookNames/BibleBooksNames_eng_traditional.xml
