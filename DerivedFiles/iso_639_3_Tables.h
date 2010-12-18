// DerivedFiles/iso_639_3_Tables.h
//
// This UTF-8 file was automatically generated by BibleBooksCodes.py on 2010-12-16 17:49:41.862525
//

#ifndef ISO_639_3_Tables_h
#define ISO_639_3_Tables_h

typedef struct IDDictEntryStruct {
    const unsigned char* ID;
    const unsigned char* Name;
    const unsigned char Type;
    const unsigned char Scope;
    const unsigned char* Part1Code;
    const unsigned char* Part2Code;
} IDDictEntry;

typedef struct NameDictEntryStruct {
    const unsigned char* Name;
    const unsigned char* ID;
    const unsigned char Type;
    const unsigned char Scope;
    const unsigned char* Part1Code;
    const unsigned char* Part2Code;
} NameDictEntry;

#endif // ISO_639_3_Tables_h

// end of iso_639_3_Tables.h