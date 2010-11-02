/* include_test.c       This file is just for testing
/*                      to make sure that the include files compile ok
/*
/* Last modified: 2010-10-14
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
#include "DerivedFiles/iso_639_3.h"
#include "DerivedFiles/BibleBooksCodes.h"
/*#include "DerivedFiles/BibleBooksNames.h"*/
#include "DerivedFiles/BibleOrganizationalSystems.h"

/* A dummy main program to keep the compiler happy */
main() {}

/* end of include_test.c */
