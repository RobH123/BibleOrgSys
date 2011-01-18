#!/bin/sh
#
# checkAll.sh
#
#   Last modified: 2011-01-18 RJH
#
# Run xmllint on all the XML files in the DataFiles folder
#
# First ensure that the RelaxNG schema files are all up-to-date
sh trangAll.sh

echo "Checking xml files for consistency..."

xmllint --noout --relaxng DerivedFiles/iso_639_3.rng --valid DataFiles/iso_639_3.xml 2>&1 | grep -v validates
xmllint --noout --relaxng DerivedFiles/BibleBooksCodes.rng --valid DataFiles/BibleBooksCodes.xml 2>&1 | grep -v validates
xmllint --noout --relaxng DerivedFiles/BibleOrganizationalSystems.rng --valid DataFiles/BibleOrganizationalSystems.xml 2>&1 | grep -v validates

xmllint --noout --relaxng DerivedFiles/BibleVersificationSystem.rng --valid DataFiles/VersificationSystems/BibleVersificationSystem_Original.xml 2>&1 | grep -v validates
xmllint --noout --relaxng DerivedFiles/BibleVersificationSystem.rng --valid DataFiles/VersificationSystems/BibleVersificationSystem_English.xml 2>&1 | grep -v validates
xmllint --noout --relaxng DerivedFiles/BibleVersificationSystem.rng --valid DataFiles/VersificationSystems/BibleVersificationSystem_Catholic.xml 2>&1 | grep -v validates
xmllint --noout --relaxng DerivedFiles/BibleVersificationSystem.rng --valid DataFiles/VersificationSystems/BibleVersificationSystem_Catholic2.xml 2>&1 | grep -v validates
xmllint --noout --relaxng DerivedFiles/BibleVersificationSystem.rng --valid DataFiles/VersificationSystems/BibleVersificationSystem_DutchTraditional.xml 2>&1 | grep -v validates
xmllint --noout --relaxng DerivedFiles/BibleVersificationSystem.rng --valid DataFiles/VersificationSystems/BibleVersificationSystem_KJV.xml 2>&1 | grep -v validates
xmllint --noout --relaxng DerivedFiles/BibleVersificationSystem.rng --valid DataFiles/VersificationSystems/BibleVersificationSystem_NRSV.xml 2>&1 | grep -v validates
xmllint --noout --relaxng DerivedFiles/BibleVersificationSystem.rng --valid DataFiles/VersificationSystems/BibleVersificationSystem_GNT92.xml 2>&1 | grep -v validates
xmllint --noout --relaxng DerivedFiles/BibleVersificationSystem.rng --valid DataFiles/VersificationSystems/BibleVersificationSystem_GNTUK.xml 2>&1 | grep -v validates
xmllint --noout --relaxng DerivedFiles/BibleVersificationSystem.rng --valid DataFiles/VersificationSystems/BibleVersificationSystem_NIV84.xml 2>&1 | grep -v validates
xmllint --noout --relaxng DerivedFiles/BibleVersificationSystem.rng --valid DataFiles/VersificationSystems/BibleVersificationSystem_NLT96.xml 2>&1 | grep -v validates
xmllint --noout --relaxng DerivedFiles/BibleVersificationSystem.rng --valid DataFiles/VersificationSystems/BibleVersificationSystem_NRS89.xml 2>&1 | grep -v validates
xmllint --noout --relaxng DerivedFiles/BibleVersificationSystem.rng --valid DataFiles/VersificationSystems/BibleVersificationSystem_REB89.xml 2>&1 | grep -v validates
xmllint --noout --relaxng DerivedFiles/BibleVersificationSystem.rng --valid DataFiles/VersificationSystems/BibleVersificationSystem_RSV52.xml 2>&1 | grep -v validates
xmllint --noout --relaxng DerivedFiles/BibleVersificationSystem.rng --valid DataFiles/VersificationSystems/BibleVersificationSystem_Luther.xml 2>&1 | grep -v validates
xmllint --noout --relaxng DerivedFiles/BibleVersificationSystem.rng --valid DataFiles/VersificationSystems/BibleVersificationSystem_RussianCanonical.xml 2>&1 | grep -v validates
xmllint --noout --relaxng DerivedFiles/BibleVersificationSystem.rng --valid DataFiles/VersificationSystems/BibleVersificationSystem_RussianOrthodox.xml 2>&1 | grep -v validates
xmllint --noout --relaxng DerivedFiles/BibleVersificationSystem.rng --valid DataFiles/VersificationSystems/BibleVersificationSystem_Septuagint.xml 2>&1 | grep -v validates
xmllint --noout --relaxng DerivedFiles/BibleVersificationSystem.rng --valid DataFiles/VersificationSystems/BibleVersificationSystem_SeptuagintBE.xml 2>&1 | grep -v validates
xmllint --noout --relaxng DerivedFiles/BibleVersificationSystem.rng --valid DataFiles/VersificationSystems/BibleVersificationSystem_Spanish.xml 2>&1 | grep -v validates
xmllint --noout --relaxng DerivedFiles/BibleVersificationSystem.rng --valid DataFiles/VersificationSystems/BibleVersificationSystem_Synodal.xml 2>&1 | grep -v validates
xmllint --noout --relaxng DerivedFiles/BibleVersificationSystem.rng --valid DataFiles/VersificationSystems/BibleVersificationSystem_Vulgate.xml 2>&1 | grep -v validates
xmllint --noout --relaxng DerivedFiles/BibleVersificationSystem.rng --valid DataFiles/VersificationSystems/BibleVersificationSystem_Vulgate2.xml 2>&1 | grep -v validates
xmllint --noout --relaxng DerivedFiles/BibleVersificationSystem.rng --valid DataFiles/VersificationSystems/BibleVersificationSystem_Cebuano_BUGV.xml 2>&1 | grep -v validates

xmllint --noout --relaxng DerivedFiles/BibleBookOrder.rng --valid DataFiles/BookOrders/BibleBookOrder_ArmenianNewTestament.xml 2>&1 | grep -v validates
xmllint --noout --relaxng DerivedFiles/BibleBookOrder.rng --valid DataFiles/BookOrders/BibleBookOrder_CatholicBible.xml 2>&1 | grep -v validates
xmllint --noout --relaxng DerivedFiles/BibleBookOrder.rng --valid DataFiles/BookOrders/BibleBookOrder_EthiopianNewTestament.xml 2>&1 | grep -v validates
xmllint --noout --relaxng DerivedFiles/BibleBookOrder.rng --valid DataFiles/BookOrders/BibleBookOrder_EthiopianProtestantOldTestament.xml 2>&1 | grep -v validates
xmllint --noout --relaxng DerivedFiles/BibleBookOrder.rng --valid DataFiles/BookOrders/BibleBookOrder_EthiopianProtestantBible.xml 2>&1 | grep -v validates
xmllint --noout --relaxng DerivedFiles/BibleBookOrder.rng --valid DataFiles/BookOrders/BibleBookOrder_EuropeanProtestantBible.xml 2>&1 | grep -v validates
xmllint --noout --relaxng DerivedFiles/BibleBookOrder.rng --valid DataFiles/BookOrders/BibleBookOrder_EuropeanProtestantNewTestament.xml 2>&1 | grep -v validates
xmllint --noout --relaxng DerivedFiles/BibleBookOrder.rng --valid DataFiles/BookOrders/BibleBookOrder_EuropeanProtestantOldTestament.xml 2>&1 | grep -v validates
xmllint --noout --relaxng DerivedFiles/BibleBookOrder.rng --valid DataFiles/BookOrders/BibleBookOrder_GutenbergNewTestament.xml 2>&1 | grep -v validates
xmllint --noout --relaxng DerivedFiles/BibleBookOrder.rng --valid DataFiles/BookOrders/BibleBookOrder_HebrewLetteris.xml 2>&1 | grep -v validates
xmllint --noout --relaxng DerivedFiles/BibleBookOrder.rng --valid DataFiles/BookOrders/BibleBookOrder_HebrewStuttgart.xml 2>&1 | grep -v validates
xmllint --noout --relaxng DerivedFiles/BibleBookOrder.rng --valid DataFiles/BookOrders/BibleBookOrder_KJVwithApocrypha.xml 2>&1 | grep -v validates
xmllint --noout --relaxng DerivedFiles/BibleBookOrder.rng --valid DataFiles/BookOrders/BibleBookOrder_LatinNewTestament.xml 2>&1 | grep -v validates
xmllint --noout --relaxng DerivedFiles/BibleBookOrder.rng --valid DataFiles/BookOrders/BibleBookOrder_Leningradensis.xml 2>&1 | grep -v validates
xmllint --noout --relaxng DerivedFiles/BibleBookOrder.rng --valid DataFiles/BookOrders/BibleBookOrder_LutheranBible.xml 2>&1 | grep -v validates
xmllint --noout --relaxng DerivedFiles/BibleBookOrder.rng --valid DataFiles/BookOrders/BibleBookOrder_LutheranNewTestament.xml 2>&1 | grep -v validates
xmllint --noout --relaxng DerivedFiles/BibleBookOrder.rng --valid DataFiles/BookOrders/BibleBookOrder_MasoreticText.xml 2>&1 | grep -v validates
xmllint --noout --relaxng DerivedFiles/BibleBookOrder.rng --valid DataFiles/BookOrders/BibleBookOrder_MatigsalugNewTestamentPlus.xml 2>&1 | grep -v validates
xmllint --noout --relaxng DerivedFiles/BibleBookOrder.rng --valid DataFiles/BookOrders/BibleBookOrder_ModernJewish.xml 2>&1 | grep -v validates
xmllint --noout --relaxng DerivedFiles/BibleBookOrder.rng --valid DataFiles/BookOrders/BibleBookOrder_NRSVwithApocrypha.xml 2>&1 | grep -v validates
xmllint --noout --relaxng DerivedFiles/BibleBookOrder.rng --valid DataFiles/BookOrders/BibleBookOrder_Septuagint.xml 2>&1 | grep -v validates
xmllint --noout --relaxng DerivedFiles/BibleBookOrder.rng --valid DataFiles/BookOrders/BibleBookOrder_SlavonicNewTestament.xml 2>&1 | grep -v validates
xmllint --noout --relaxng DerivedFiles/BibleBookOrder.rng --valid DataFiles/BookOrders/BibleBookOrder_SynodalBible.xml 2>&1 | grep -v validates
xmllint --noout --relaxng DerivedFiles/BibleBookOrder.rng --valid DataFiles/BookOrders/BibleBookOrder_SyriacNewTestament.xml 2>&1 | grep -v validates
xmllint --noout --relaxng DerivedFiles/BibleBookOrder.rng --valid DataFiles/BookOrders/BibleBookOrder_VulgateBible.xml 2>&1 | grep -v validates
xmllint --noout --relaxng DerivedFiles/BibleBookOrder.rng --valid DataFiles/BookOrders/BibleBookOrder_VulgateOldTestament.xml 2>&1 | grep -v validates

xmllint --noout --relaxng DerivedFiles/BibleBooksNames.rng --valid DataFiles/BookNames/BibleBooksNames_eng_traditional.xml 2>&1 | grep -v validates
xmllint --noout --relaxng DerivedFiles/BibleBooksNames.rng --valid DataFiles/BookNames/BibleBooksNames_deu_traditional.xml 2>&1 | grep -v validates
xmllint --noout --relaxng DerivedFiles/BibleBooksNames.rng --valid DataFiles/BookNames/BibleBooksNames_fra_traditional.xml 2>&1 | grep -v validates
xmllint --noout --relaxng DerivedFiles/BibleBooksNames.rng --valid DataFiles/BookNames/BibleBooksNames_mbt.xml 2>&1 | grep -v validates

xmllint --noout --relaxng DerivedFiles/BiblePunctuationSystem.rng --valid DataFiles/PunctuationSystems/BiblePunctuationSystem_English.xml 2>&1 | grep -v validates
xmllint --noout --relaxng DerivedFiles/BiblePunctuationSystem.rng --valid DataFiles/PunctuationSystems/BiblePunctuationSystem_English_brief.xml 2>&1 | grep -v validates
xmllint --noout --relaxng DerivedFiles/BiblePunctuationSystem.rng --valid DataFiles/PunctuationSystems/BiblePunctuationSystem_Matigsalug.xml 2>&1 | grep -v validates

