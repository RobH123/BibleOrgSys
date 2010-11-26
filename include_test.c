/* include_test.c       This file is just for testing
/*                      to make sure that the include files compile ok
/*
/* Last modified: 2010-11-03
/*
/* The .h files included below are created by xxxConvertor.py programs
/*
/* If the .h files are formed correctly, compiling this file should give no errors.
/*
/* Under Linux use:
/*      gcc -c include_test.c
*/

/*  Include the .h files that we wish to test for errors */
# 
#include "DerivedFiles/iso_639_3_Tables.h"
#include "DerivedFiles/BibleBooksCodes_Tables.h"
#include "DerivedFiles/BibleVersificationSystems_Tables.h"
#include "DerivedFiles/BibleBooksOrders_Tables.h"
/*#include "DerivedFiles/BibleBooksNames_Tables.h"*/
/*#include "DerivedFiles/BibleOrganizationalSystems_Tables.h"*/

/* A dummy main program to keep the compiler happy */
main() {}

/* end of include_test.c */
