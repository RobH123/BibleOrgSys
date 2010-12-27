// DerivedFiles/BiblePunctuationSystems_Tables.h
//
// This UTF-8 file was automatically generated by BiblePunctuationSystems.py on 2010-12-27 16:31:34.159294
//

#ifndef BIBLEPUNCTUATIONSYSTEMS_Tables_h
#define BIBLEPUNCTUATIONSYSTEMS_Tables_h

typedef struct punctuationByRefEntryStruct {
    const unsigned char referenceAbbreviation[3+1];
    const int indexNumber;
} punctuationByRefEntry;

typedef struct punctuationByIndexEntryStruct {
    const int indexNumber;
    const unsigned char referenceAbbreviation[3+1];
} punctuationByIndexEntry;

typedef struct tableEntryStruct {
    const unsigned char* systemName;
    punctuationByRefEntry* byReference;
    punctuationByIndexEntry* byBook;
} tableEntry;

#endif // BIBLEPUNCTUATIONSYSTEMS_Tables_h

// end of BiblePunctuationSystems_Tables.h