// DerivedFiles/BibleBookOrders_Tables.h
//
// This UTF-8 file was automatically generated by BibleBookOrders.py on 2010-12-16 22:20:19.689716
//

#ifndef BIBLEBOOKORDERS_Tables_h
#define BIBLEBOOKORDERS_Tables_h

typedef struct bookOrderByRefEntryStruct {
    const unsigned char referenceAbbreviation[3+1];
    const int indexNumber;
} bookOrderByRefEntry;

typedef struct bookOrderByIndexEntryStruct {
    const int indexNumber;
    const unsigned char referenceAbbreviation[3+1];
} bookOrderByIndexEntry;

typedef struct tableEntryStruct {
    const unsigned char* systemName;
    bookOrderByRefEntry* byReference;
    bookOrderByIndexEntry* byBook;
} tableEntry;

#endif // BIBLEBOOKORDERS_Tables_h

// end of BibleBookOrders_Tables.h