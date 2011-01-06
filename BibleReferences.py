#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# BibleReferences.py
#
# Module for handling Bible references including ranges
#   Last modified: 2011-01-06 (also update versionString below)
#
# Copyright (C) 2010-2011 Robert Hunt
# Author: Robert Hunt <robert316@users.sourceforge.net>
# License: See gpl-3.0.txt
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Module for creating and manipulating Bible references.

This module recognises and handles OSIS Bible references.
    They are of the form bookAbbreviation.chapterNumber.verseNumber
        e.g., Gen.1.1 or Exod.20.10 or 2Chr.7.6 or Jude.1.2
    Note that the book abbreviation is not a constant length
            and may also start with a digit
        and that the same separator is repeated.

However, the native Bible reference string format in this system is more tightly defined
    e.g., GEN_1:1 or EXO_20:10 or CH2_7:6 or JDE_1:2b
We can see that
    1/ The Bible book code is always 3-characters, starting with a letter
        All letters are UPPERCASE
    2/ We use an underline character as the book / chapter separator
    3/ We use a colon as the chapter / verse separator
    4/ We treat all chapter and verse fields as strings
    5/ Verse numbers can include a lowercase letter suffix a..c
        representing very approximate portions of a verse

Internally, we represent it as a Bible reference tuple BBB,C,V,S where
    BBB is the three-character UPPERCASE reference abbreviation
    C is the chapter number string
    V is the verse number string
    S is the single lowercase letter suffix (see allowedVerseSuffixes below)

OSIS defines reference ranges
    e.g., Gen.1.1-Gen.1.2 or Gen.1.1-Gen.2.3 (inclusive)

Our ranges are slightly different (also inclusive)
    e.g., Gen_1:1-Gen_1:2 but Gen_1:1-Gen_2:3
    i.e., using a hyphen for a verse span but xxx for a span that crosses chapters.

OXES is different again.
"""

progName = "Bible References handler"
versionString = "0.16"


import os, logging

import Globals
from BibleBooksCodes import BibleBooksCodes
from BibleOrganizationalSystems import BibleOrganizationalSystem


allowedVerseSuffixes = ('a','b','c','d','e','f',) # Could be like verse 5b


class BibleSingleReference:
    """
    Class for creating and manipulating single Bible reference objects (no range allowed).
        Use this class only if a Bible reference must be just a single Bible verse.

    Uses a state-machine (rather than regular expressions) because I think it can give better error and warning messages.
        Not fully tested for all exceptional cases.
    """

    def __init__( self, BBCObject, BOSObject ):
        """ Initialize the object with necessary sub-systems. """
        assert( BBCObject )
        assert( BOSObject )
        self.__BibleBooksCodes = BBCObject
        self.__BibleOrganizationalSystem = BOSObject
        self.punctuationDict = self.__BibleOrganizationalSystem.getPunctuationDict()
        self.reference = ()
    # end of __init__

    def __str__( self ):
        """
        This method returns the string representation of a Bible object.
        
        @return: the name of a Bible object formatted as a string
        @rtype: string
        """
        result = "Bible Single Reference object"
        if self.reference: result += ('\n' if result else '') + "  %s" % str(self.reference)
        return result
    # end of __str__

    def parseReferenceString( self, referenceString ):
        """
        Returns a tuple with True/False result, haveWarnings, BBB, C, V, S
        """
        assert( referenceString )
        haveWarnings, haveErrors = False, False
        strippedReferenceString = referenceString.strip()
        if strippedReferenceString != referenceString:
            logging.warning( "Reference string '%s' contains surrounding space(s)" % referenceString )
            haveWarnings = True
        #statusList = {0:"gettingBookname", 1:"gettingBCSeparator", 2:"gettingChapter", 3:"gettingVerse", 4:"gotCV", 5:"done", 9:"finished"}
        status, bookNameOrAbbreviation, BBB, C, V, S, spaceCount = 0, '', None, '', '', '', 0
        for char in strippedReferenceString:
            #print( "Status: %s -- got '%s'" % (statusList[status],char) )
            if status == 0: # Getting bookname (with or without punctuation after book abbreviation)
                if char.isalnum():
                    if char.isdigit() and bookNameOrAbbreviation: # Could this be the chapter number?
                        BBB = self.__BibleOrganizationalSystem.getBBB( bookNameOrAbbreviation )
                        if BBB is None: # Don't seem to have a valid bookname yet
                            bookNameOrAbbreviation += char
                            continue
                        # else if seems we have a valid bookname -- let's assume this might be the chapter number
                        logging.error( "It seems that the bookname might be joined onto the chapter number in Bible reference '%s'" % (referenceString) )
                        status = 2 # Start getting the chapter number
                    else:
                        bookNameOrAbbreviation += char
                        continue
                elif char in self.punctuationDict['punctuationAfterBookAbbreviation']:
                    BBB = self.__BibleOrganizationalSystem.getBBB( bookNameOrAbbreviation )
                    status = 1 # Default to getting BCS
                    if BBB is None:
                        logging.error( "Invalid '%s' bookname in Bible reference '%s'" % ( bookNameOrAbbreviation, referenceString ) )
                        haveErrors = True
                    else: # we found an unambiguous bookname
                        shortBookName = self.__BibleOrganizationalSystem.getShortBookName( BBB )
                        if shortBookName == bookNameOrAbbreviation: # they entered the full bookname -- we didn't really expect this punctuation
                            if char in self.punctuationDict['bookChapterSeparator']: # ok, they are the same character
                                status = 2 # Just accept this as the BCS and go get the chapter number
                            else:
                                logging.warning( "Didn't expect '%s' punctuationAfterBookAbbreviation when the full book name was given in '%s'" % (self.punctuationDict['punctuationAfterBookAbbreviation'],referenceString) )
                                haveWarnings = True
                    continue
                elif char in self.punctuationDict['bookChapterSeparator']:
                    BBB = self.__BibleOrganizationalSystem.getBBB( bookNameOrAbbreviation )
                    if BBB is None:
                        logging.error( "Invalid '%s' bookname in Bible reference '%s'" % ( bookNameOrAbbreviation, referenceString ) )
                        haveErrors = True
                    else: # we found an unambiguous bookname
                        shortBookName = self.__BibleOrganizationalSystem.getShortBookName( BBB )
                        if shortBookName != bookNameOrAbbreviation: # they didn't enter the full bookname -- we really expect the punctuationAfterBookAbbreviation
                            logging.warning( "Missing '%s' punctuationAfterBookAbbreviation when the book name abbreviation was given in '%s'" % (self.punctuationDict['punctuationAfterBookAbbreviation'],referenceString) )
                            haveWarnings = True
                    spaceCount = 1 if char==' ' else 0
                    status = 2
                    continue
                else:
                    logging.error( "Unexpected '%s' character in Bible reference '%s' when getting book name" % ( char, referenceString ) )
                    haveErrors = True
                    continue
            if status == 1: # Getting book chapter separator
                if char in self.punctuationDict['bookChapterSeparator']:
                    BBB = self.__BibleOrganizationalSystem.getBBB( bookNameOrAbbreviation )
                    if BBB is None:
                        logging.error( "Invalid '%s' bookname in Bible reference '%s'" % ( bookNameOrAbbreviation, referenceString ) )
                        haveErrors = True
                    spaceCount = 1 if char==' ' else 0
                    status = 2
                    continue
                elif char.isdigit(): # Must have missed the BCS
                    logging.warning( "Missing '%s' book/chapter separator when the book name abbreviation was given in '%s'" % (self.punctuationDict['bookChapterSeparator'],referenceString) )
                    haveWarnings = True
                    status = 2 # Fall through below
                else:
                    logging.error( "Unexpected '%s' character in Bible reference '%s' when getting book/chapter separator" % ( char, referenceString ) )
                    haveErrors = True
                    continue
            if status == 2: # Getting chapter number (or could be the verse number of a one chapter book)
                if char==' ' and not C:
                    spaceCount += 1
                elif char.isdigit():
                    if self.punctuationDict['spaceAllowedAfterBCS']=='Y' and spaceCount<1:
                        logging.warning( "Missing space after bookname in Bible reference '%s'" % referenceString )
                        haveWarnings = True
                    elif self.punctuationDict['spaceAllowedAfterBCS']=='N' or spaceCount>1:
                        logging.warning( "Extra space(s) after bookname in Bible reference '%s'" % referenceString )
                        haveWarnings = True
                    C += char
                elif char in allowedVerseSuffixes: # Could be like verse 5b
                    S += char
                elif C and char in self.punctuationDict['chapterVerseSeparator']:
                    status = 3 # Start getting the verse number
                else:
                    logging.error( "Unexpected '%s' character when getting chapter number in %s Bible reference '%s'" % ( char, BBB, referenceString ) )
                    haveErrors = True
                continue
            if status == 3: # Getting verse number
                if char == ' ' and not V:
                    logging.warning( "Extra space(s) after chapter in %s Bible reference '%s'" % ( BBB, referenceString ) )
                    haveWarnings = True
                elif char.isdigit():
                    V += char
                elif char in allowedVerseSuffixes: # Could be like verse 5b
                    S += char
                else:
                    logging.error( "Unexpected '%s' character when getting verse number in %s %s Bible reference '%s'" % ( char, BBB, C, referenceString ) )
                    haveErrors = True
                    if V: status = 4
                continue
        if status==3: # Got a C but still getting the V hopefully
            if V: status = 4
        if len(S) > 1:
            logging.error( "Unexpected long '%s' suffix in %s Bible reference '%s'" % ( S, BBB, referenceString ) )
            haveErrors = True
            S = S[0] # Just take the first one
        if BBB is not None:
            if status==2 and C and self.__BibleOrganizationalSystem.isSingleChapterBook( BBB ): # Have a single chapter book and what we were given is presumably the verse number
                    V = C
                    C = '1'
                    status = 4
            if status>=4 and not haveErrors:
                if self.__BibleOrganizationalSystem.isValidBCVRef( (BBB, C, V, S), referenceString, errorMessages=True ):
                    status = 9
        self.reference = (BBB, C, V, S,)
        #print( "Final status: %s -- got '%s'from '%s'\n" % (statusList[status],self.reference,referenceString) )
        return status==9 and not haveErrors, haveWarnings, BBB, C, V, S
# end of class BibleSingleReference


class BibleSingleReferences:
    """
    Class for creating and manipulating a list of multiple Bible reference objects (no ranges allowed).
        Use this class only if a Bible reference must be just a list of single Bible verses.

    Uses a state-machine (rather than regular expressions) because I think it can give better error and warning messages.
        Not fully tested for all exceptional cases.
    """

    def __init__( self, BBCObject, BOSObject ):
        """ Initialize the object with necessary sub-systems. """
        assert( BBCObject )
        assert( BOSObject )
        self.__BibleBooksCodes = BBCObject
        self.__BibleOrganizationalSystem = BOSObject
        self.punctuationDict = self.__BibleOrganizationalSystem.getPunctuationDict()
        self.referenceList = []
    # end of __init__

    def __str__( self ):
        """
        This method returns the string representation of a Bible object.
        
        @return: the name of a Bible object formatted as a string
        @rtype: string
        """
        result = "Bible Single References Object"
        if self.referenceList: result += ('\n' if result else '') + "  %s" % self.referenceList
        return result
    # end of __str__

    def parseReferenceString( self, referenceString ):
        """
        Returns a tuple with True/False result, haveWarnings, list of (BBB, C, V, S) tuples
        """

        def saveReference( BBB, C, V, S, refList ):
            """ Checks the reference info then saves it as a referenceTuple in the refList. """
            nonlocal haveErrors, haveWarnings
            if len(S) > 1:
                logging.error( "Unexpected long '%s' suffix in %s Bible reference '%s'" % ( S, BBB, referenceString ) )
                haveErrors = True
                S = S[0] # Just take the first one
            refTuple = ( BBB, C, V, S, )
            if refTuple in refList:
                logging.warning( "Reference %s is repeated in Bible reference '%s'" % ( refTuple, referenceString ) )
                haveWarnings = True
            if not self.__BibleOrganizationalSystem.isValidBCVRef( refTuple, referenceString, errorMessages=True ):
                haveErrors = True
            refList.append( refTuple )
        # end of saveReference

        #print( "Processing '%s'" % referenceString )
        assert( referenceString )
        haveWarnings, haveErrors = False, False
        strippedReferenceString = referenceString.strip()
        if strippedReferenceString != referenceString:
            logging.warning( "Reference string '%s' contains surrounding space(s)" % referenceString )
            haveWarnings = True
        #statusList = {0:"gettingBookname", 1:"gettingBCSeparator", 2:"gettingChapter", 3:"gettingVerse", 4:"gettingNextBorC", 5:"done", 9:"finished"}
        status, bookNameOrAbbreviation, BBB, C, V, S, spaceCount, refList = 0, '', None, '', '', '', 0, []
        for char in strippedReferenceString:
            #print( "Status: %s -- got '%s'" % (statusList[status],char) )
            if status == 0: # Getting bookname (with or without punctuation after book abbreviation)
                if char.isalnum():
                    if char.isdigit() and bookNameOrAbbreviation: # Could this be the chapter number?
                        BBB = self.__BibleOrganizationalSystem.getBBB( bookNameOrAbbreviation )
                        if BBB is None: # Don't seem to have a valid bookname yet
                            bookNameOrAbbreviation += char
                            continue
                        # else if seems we have a valid bookname -- let's assume this might be the chapter number
                        logging.error( "It seems that the bookname might be joined onto the chapter number in Bible reference '%s'" % (referenceString) )
                        status = 2 # Start getting the chapter number
                    else:
                        bookNameOrAbbreviation += char
                        continue
                elif char in self.punctuationDict['punctuationAfterBookAbbreviation']:
                    BBB = self.__BibleOrganizationalSystem.getBBB( bookNameOrAbbreviation )
                    status = 1 # Default to getting BCS
                    if BBB is None:
                        logging.error( "Invalid '%s' bookname in Bible reference '%s'" % ( bookNameOrAbbreviation, referenceString ) )
                        haveErrors = True
                    else: # we found an unambiguous bookname
                        shortBookName = self.__BibleOrganizationalSystem.getShortBookName( BBB )
                        if shortBookName == bookNameOrAbbreviation: # they entered the full bookname -- we didn't really expect this punctuation
                            if char in self.punctuationDict['bookChapterSeparator']: # ok, they are the same character
                                status = 2 # Just accept this as the BCS and go get the chapter number
                            else:
                                logging.warning( "Didn't expect '%s' punctuationAfterBookAbbreviation when the full book name was given in '%s'" % (self.punctuationDict['punctuationAfterBookAbbreviation'],referenceString) )
                                haveWarnings = True
                    continue
                elif char in self.punctuationDict['bookChapterSeparator']:
                    BBB = self.__BibleOrganizationalSystem.getBBB( bookNameOrAbbreviation )
                    if BBB is None:
                        logging.error( "Invalid '%s' bookname in Bible reference '%s'" % ( bookNameOrAbbreviation, referenceString ) )
                        haveErrors = True
                    else: # we found an unambiguous bookname
                        shortBookName = self.__BibleOrganizationalSystem.getShortBookName( BBB )
                        if shortBookName != bookNameOrAbbreviation: # they didn't enter the full bookname -- we really expect the punctuationAfterBookAbbreviation
                            logging.warning( "Missing '%s' punctuationAfterBookAbbreviation when the book name abbreviation was given in '%s'" % (self.punctuationDict['punctuationAfterBookAbbreviation'],referenceString) )
                            haveWarnings = True
                    spaceCount = 1 if char==' ' else 0
                    status = 2
                    continue
                else:
                    logging.error( "Unexpected '%s' character in Bible reference '%s' when getting book name" % ( char, referenceString ) )
                    haveErrors = True
                    continue
            if status == 1: # Getting book chapter separator
                if char in self.punctuationDict['bookChapterSeparator']:
                    BBB = self.__BibleOrganizationalSystem.getBBB( bookNameOrAbbreviation )
                    if BBB is None:
                        logging.error( "Invalid '%s' bookname in Bible reference '%s'" % ( bookNameOrAbbreviation, referenceString ) )
                        haveErrors = True
                    spaceCount = 1 if char==' ' else 0
                    status = 2
                    continue
                elif char.isdigit(): # Must have missed the BCS
                    logging.warning( "Missing '%s' book/chapter separator when the book name abbreviation was given in '%s'" % (self.punctuationDict['bookChapterSeparator'],referenceString) )
                    haveWarnings = True
                    status = 2 # Fall through below
                else:
                    logging.error( "Unexpected '%s' character in Bible reference '%s' when getting book/chapter separator" % ( char, referenceString ) )
                    haveErrors = True
                    continue
            if status == 2: # Getting chapter number (or could be the verse number of a one chapter book)
                if char==' ' and not C:
                    spaceCount += 1
                elif char.isdigit():
                    if self.punctuationDict['spaceAllowedAfterBCS']=='Y' and spaceCount<1:
                        logging.warning( "Missing space after bookname in Bible reference '%s'" % referenceString )
                        haveWarnings = True
                    elif self.punctuationDict['spaceAllowedAfterBCS']=='N' or spaceCount>1:
                        logging.warning( "Extra space(s) after bookname in Bible reference '%s'" % referenceString )
                        haveWarnings = True
                    C += char
                elif char in allowedVerseSuffixes: # Could be like verse 5b
                    S += char
                elif C and char in self.punctuationDict['chapterVerseSeparator']:
                    status = 3 # Start getting the verse number
                else:
                    logging.error( "Unexpected '%s' character when getting chapter number in %s Bible reference '%s'" % ( char, BBB, referenceString ) )
                    haveErrors = True
                continue
            if status == 3: # Getting verse number
                if char == ' ' and not V:
                    logging.warning( "Extra space(s) after chapter in %s Bible reference '%s'" % ( BBB, referenceString ) )
                    haveWarnings = True
                elif char.isdigit():
                    V += char
                elif char in allowedVerseSuffixes: # Could be like verse 5b
                    S += char
                elif V and char in self.punctuationDict['verseSeparator']:
                    saveReference( BBB, C, V, S, refList )
                    V, S = '', ''
                elif V and (char in self.punctuationDict['chapterSeparator'] or char in self.punctuationDict['bookSeparator']):
                    saveReference( BBB, C, V, S, refList )
                    V, S = '', ''
                    if self.punctuationDict['chapterSeparator'] == self.punctuationDict['bookSeparator']:
                        temp, spaceCount = '', 0
                        status = 4 # We don't know what to expect next
                    elif char in self.punctuationDict['chapterSeparator']:
                        C = ''
                        status = 2 # Get the next chapter number
                    elif char in self.punctuationDict['bookSeparator']:
                        bookNameOrAbbreviation, BBB, C = '', None, ''
                        status = 0 # Get the next book name abbreviation
                else:
                    logging.error( "Unexpected '%s' character when getting verse number in %s %s Bible reference '%s'" % ( char, BBB, C, referenceString ) )
                    haveErrors = True
                    if V:
                        saveReference( BBB, C, V, S, refList )
                        V, S = '', ''
                continue
            if status == 4: # Getting the next chapter number or book name (not sure which)
                if char == ' ' and not temp:
                    if spaceCount:
                        logging.warning( "Extra space(s) after chapter or book separator in %s Bible reference '%s'" % ( BBB, referenceString ) )
                        haveWarnings = True
                    spaceCount += 1
                elif char.isalnum():
                    temp += char
                elif char in self.punctuationDict['punctuationAfterBookAbbreviation']:
                    bookNameOrAbbreviation = temp
                    BBB = self.__BibleOrganizationalSystem.getBBB( bookNameOrAbbreviation )
                    C, status = '', 1 # Default to getting BCS
                    if BBB is None:
                        logging.error( "Invalid '%s' bookname in Bible reference '%s'" % ( bookNameOrAbbreviation, referenceString ) )
                        haveErrors = True
                    else: # we found an unambiguous bookname
                        shortBookName = self.__BibleOrganizationalSystem.getShortBookName( BBB )
                        if shortBookName == bookNameOrAbbreviation: # they entered the full bookname -- we didn't really expect this punctuation
                            if char in self.punctuationDict['bookChapterSeparator']: # ok, they are the same character
                                status = 2 # Just accept this as the BCS and go get the chapter number
                            else:
                                logging.warning( "Didn't expect '%s' punctuationAfterBookAbbreviation when the full book name was given in '%s'" % (self.punctuationDict['punctuationAfterBookAbbreviation'],referenceString) )
                                haveWarnings = True
                else:
                    #print( "Got '%s'" % temp )
                    if char in self.punctuationDict['chapterVerseSeparator'] and temp and temp.isdigit(): # Assume it's a follow on chapter number
                        C = temp
                        status = 3 # Now get the verse number
                    elif char in self.punctuationDict['bookChapterSeparator']:
                        bookNameOrAbbreviation = temp
                        BBB = self.__BibleOrganizationalSystem.getBBB( bookNameOrAbbreviation )
                        if BBB is None:
                            logging.error( "Invalid '%s' bookname in Bible reference '%s'" % ( bookNameOrAbbreviation, referenceString ) )
                            haveErrors = True
                        C, V, S = '', '', ''
                        spaceCount = 1 if char==' ' else 0
                        status = 2 # Start getting the chapter number
                    else:
                        logging.error( "Unexpected '%s' character in Bible reference '%s' when getting book name" % ( char, referenceString ) )
                        haveErrors = True
                continue
        if status==3: # Got a C but still getting the V hopefully
            if V: status = 4
        if BBB is not None:
            if status==2 and C and self.__BibleOrganizationalSystem.isSingleChapterBook( BBB ): # Have a single chapter book and what we were given is presumably the verse number
                    V = C
                    C = '1'
                    status = 4
            if status>=4 and not haveErrors:
                saveReference( BBB, C, V, S, refList )
                status = 9
        self.referenceList = refList
        #print( "Final status: %s -- got '%s'from '%s'\n" % (statusList[status],self.referenceList,referenceString) )
        return status==9 and not haveErrors, haveWarnings, self.referenceList
# end of class BibleSingleReferences


class BibleReferenceList:
    """
    Class for creating and manipulating a list of multiple Bible reference objects including optional ranges.
        Use this class unless a Bible reference must be just a single Bible verse.

    Uses a state-machine (rather than regular expressions) because I think it can give better error and warning messages.
        Not fully tested for all exceptional cases.
    """

    def __init__( self, BBCObject, BOSObject ):
        """ Initialize the object with necessary sub-systems. """
        assert( BBCObject )
        assert( BOSObject )
        self.__BibleBooksCodes = BBCObject
        self.__BibleOrganizationalSystem = BOSObject
        self.punctuationDict = self.__BibleOrganizationalSystem.getPunctuationDict()
        self.referenceList = []
    # end of __init__

    def __str__( self ):
        """
        This method returns- the string representation of a Bible Range References object.
        
        @return: the name of a Bible object formatted as a string
        @rtype: string
        """
        result = "Bible Range References object"
        if self.referenceList: result += ('\n' if result else '') + "  %s" % self.referenceList
        return result
    # end of __str__

    def makeReferenceString( self, ref ):
        """
        Makes a string out of a reference tuple
        """
        assert( ref )
        lenRef = len( ref )
        if lenRef == 2: (BBB, C), V, S = ref, '', ''
        elif lenRef == 3: (BBB, C, V), S = ref, ''
        elif lenRef == 4: BBB, C, V, S = ref
        else: logging.error( "Unrecognized %s parameter to makeReferenceString" % ref ); return None

        BnC = self.punctuationDict['booknameCase'] if isinstance(self.punctuationDict['booknameCase'],str) else self.punctuationDict['booknameCase'][0]
        BCS = self.punctuationDict['bookChapterSeparator'] if isinstance(self.punctuationDict['bookChapterSeparator'],str) else self.punctuationDict['bookChapterSeparator'][0]
        CVS = self.punctuationDict['chapterVerseSeparator'] if isinstance(self.punctuationDict['chapterVerseSeparator'],str) else self.punctuationDict['chapterVerseSeparator'][0]

        if BBB[0].isdigit(): # Have a book name like 1SA
            assert( "Should never happen I think" == BBB )
            BBBstr = BBB[0] + ( BBB[1:] if BnC=='U' else BBB[1:].lower() if BnC=='L' else BBB[1:].capitalize() )
        else:
            BBBstr = BBB if BnC=='U' else BBB.lower() if BnC=='L' else BBB.capitalize()
        if self.__BibleOrganizationalSystem.isSingleChapterBook( BBB ):
            assert( C == '1' )
            resultString = "%s%s%s%s" % ( BBBstr, BCS, ' ' if self.punctuationDict['spaceAllowedAfterBCS']=='Y' else '', V )
        else: # it's a book with multiple chapters
            resultString = "%s%s%s%s%s%s" % ( BBBstr, BCS, ' ' if self.punctuationDict['spaceAllowedAfterBCS']=='Y' else '', C, CVS, V )
        return resultString
    # end of makeReferenceString

    def XXXcheckReferenceRangeList( self, refList, referenceString="(unknown)", errorMessages=False ):
        """
        Check a reference range list

        Returns haveErrors, haveWarnings
        """
        assert( refList and isinstance(refList, list) )

        # Take a list that might include ranges, and convert it into a single list of individual verse numbers
        singleList = []
        haveErrors, haveWarnings = False, False
        for refOrRefs in refList:
            #print( "refOrRefs", refOrRefs )
            if len(refOrRefs) == 2: # We have two items, i.e., a verse range
                startRef, endRef = refOrRefs
                verseList = self.__BibleOrganizationalSystem.expandCVRange( startRef, endRef, referenceString, errorMessages )
                singleList.extend( verseList )
            else: # it must be a single reference
                if not self.__BibleOrganizationalSystem.isValidBCVRef( refOrRefs, referenceString, errorMessages ):
                    haveErrors = True
                singleList.append( refOrRefs )
        #print( "sL", singleList )
        singleSet = set( singleList )
        if len(singleSet) < len(singleList):
            for entry in singleSet:
                if singleList.count(entry) > 1:
                    #print( entry )
                    pass
                    #logging.warning( "Have duplicate or overlapping range at %s in Bible references '%s'" % ( self.makeReferenceString(entry), referenceString ) )
            haveWarnings = True
        return haveErrors, haveWarnings
    # end of checkReferenceRangeList

    def parseReferenceString( self, referenceString, errorMessages=False ):
        """
        Returns a tuple with True/False result, haveWarnings, list of (BBB, C, V, S) tuples.
            A range is expressed as a tuple containing a pair of (BBB, C, V, S) tuples.

        We could rewrite this using RegularExpressions, but would it be able to give such precise formatting error messages?
        """

        def saveReference( BBB, C, V, S, refList ):
            """ Checks the reference info then saves it as a referenceTuple in the refList. """
            nonlocal haveErrors, haveWarnings, totalVerseList
            if len(S) > 1:
                if errorMessages: logging.error( "Unexpected long '%s' suffix in %s Bible reference '%s'" % ( S, BBB, referenceString ) )
                haveErrors = True
                S = S[0] # Just take the first one
            refTuple = ( BBB, C, V, S, )
            if refTuple in refList:
                if errorMessages: logging.warning( "Reference %s is repeated in Bible reference '%s'" % ( refTuple, referenceString ) )
                haveWarnings = True
            if not self.__BibleOrganizationalSystem.isValidBCVRef( refTuple, referenceString, errorMessages ):
                haveErrors = True
            refList.append( refTuple )
            totalVerseList.append( refTuple )
        # end of saveReference

        def saveStartReference( BBB, C, V, S ):
            """ Checks the reference info then saves it as a referenceTuple. """
            nonlocal haveErrors, haveWarnings, startReferenceTuple
            if len(S) > 1:
                if errorMessages: logging.error( "Unexpected long '%s' suffix in %s Bible reference '%s'" % ( S, BBB, referenceString ) )
                haveErrors = True
                S = S[0] # Just take the first one
            startReferenceTuple = ( BBB, C, V, S, )
            if not self.__BibleOrganizationalSystem.isValidBCVRef( startReferenceTuple, referenceString, errorMessages ):
                haveErrors = True
        # end of saveStartReference

        def saveReferenceRange( startTuple, BBB, C, V, S, refList ):
            """ Checks the reference info then saves it as a referenceTuple in the refList. """
            nonlocal haveErrors, haveWarnings, totalVerseList
            if len(S) > 1:
                if errorMessages: logging.error( "Unexpected long '%s' suffix in %s Bible reference '%s'" % ( S, BBB, referenceString ) )
                haveErrors = True
                S = S[0] # Just take the first one
            finishTuple = ( BBB, C, V, S, )
            if not self.__BibleOrganizationalSystem.isValidBCVRef( finishTuple, referenceString, errorMessages=False ): # No error messages here because it will be caught at expandCVRange below
                haveErrors = True # Just set this flag
            rangeTuple = (startTuple, finishTuple,)
            verseList = self.__BibleOrganizationalSystem.expandCVRange( startTuple, finishTuple, referenceString, errorMessages )
            if verseList is not None: totalVerseList.extend( verseList )
            if rangeTuple in refList:
                if errorMessages: logging.warning( "Reference range %s is repeated in Bible reference '%s'" % ( rangeTuple, referenceString ) )
                haveWarnings = True
            refList.append( rangeTuple )
        # end of saveReferenceRange

        #print( "Processing '%s'" % referenceString )
        assert( referenceString )
        haveWarnings, haveErrors, totalVerseList = False, False, []
        strippedReferenceString = referenceString.strip()
        if strippedReferenceString != referenceString:
            if errorMessages: logging.warning( "Reference string '%s' contains surrounding space(s)" % referenceString )
            haveWarnings = True
        #statusList = {0:"gettingBookname", 1:"gettingBCSeparator", 2:"gettingChapter", 3:"gettingVerse", 4:"gettingNextBorC", 5:"gettingCorVRange", 6:"gettingCRange", 7:"gettingVRange", 9:"finished"}
        status, bookNameOrAbbreviation, BBB, C, V, S, spaceCount, startReferenceTuple, refList = 0, '', None, '', '', '', 0, (), []
        for char in strippedReferenceString:
            #print( "Status: %s -- got '%s'" % (statusList[status],char) )
            #print( "At %i got '%s'" % ( status,char ), haveErrors, haveWarnings, refList )
            if status == 0: # Getting bookname (with or without punctuation after book abbreviation)
                if char.isalnum():
                    if char.isdigit() and bookNameOrAbbreviation: # Could this be the chapter number?
                        BBB = self.__BibleOrganizationalSystem.getBBB( bookNameOrAbbreviation )
                        if BBB is None: # Don't seem to have a valid bookname yet
                            bookNameOrAbbreviation += char
                            continue
                        # else if seems we have a valid bookname -- let's assume this might be the chapter number
                        if errorMessages: logging.error( "It seems that the bookname might be joined onto the chapter number in Bible reference '%s'" % (referenceString) )
                        status = 2 # Start getting the chapter number immediately (no "continue" here)
                    else:
                        bookNameOrAbbreviation += char
                        continue
                elif bookNameOrAbbreviation and char == ' ': # Could be something like 1 Cor
                    BBB = self.__BibleOrganizationalSystem.getBBB( bookNameOrAbbreviation )
                    if BBB is None: # Don't seem to have a valid bookname yet
                        bookNameOrAbbreviation += char
                        continue
                if char in self.punctuationDict['punctuationAfterBookAbbreviation']:
                    BBB = self.__BibleOrganizationalSystem.getBBB( bookNameOrAbbreviation )
                    status = 1 # Default to getting BCS
                    if BBB is None:
                        if errorMessages: logging.error( "Invalid '%s' bookname in Bible reference '%s'" % ( bookNameOrAbbreviation, referenceString ) )
                        haveErrors = True
                    else: # we found an unambiguous bookname
                        shortBookName = self.__BibleOrganizationalSystem.getShortBookName( BBB )
                        if shortBookName == bookNameOrAbbreviation: # they entered the full bookname -- we didn't really expect this punctuation
                            if char in self.punctuationDict['bookChapterSeparator']: # ok, they are the same character
                                status = 2 # Just accept this as the BCS and go get the chapter number
                            else:
                                if errorMessages: logging.warning( "Didn't expect '%s' punctuationAfterBookAbbreviation when the full book name was given in '%s'" % (self.punctuationDict['punctuationAfterBookAbbreviation'],referenceString) )
                                haveWarnings = True
                    continue
                elif char in self.punctuationDict['bookChapterSeparator']:
                    BBB = self.__BibleOrganizationalSystem.getBBB( bookNameOrAbbreviation )
                    if BBB is None:
                        if errorMessages: logging.error( "Invalid '%s' bookname in Bible reference '%s'" % ( bookNameOrAbbreviation, referenceString ) )
                        haveErrors = True
                    else: # we found an unambiguous bookname
                        shortBookName = self.__BibleOrganizationalSystem.getShortBookName( BBB )
                        if shortBookName != bookNameOrAbbreviation: # they didn't enter the full bookname -- we really expect the punctuationAfterBookAbbreviation
                            if errorMessages: logging.warning( "Missing '%s' punctuationAfterBookAbbreviation when the book name abbreviation was given in '%s'" % (self.punctuationDict['punctuationAfterBookAbbreviation'],referenceString) )
                            haveWarnings = True
                    spaceCount = 1 if char==' ' else 0
                    status = 2
                    continue
                else:
                    if errorMessages: logging.error( "Unexpected '%s' character in Bible reference '%s' when getting book name" % ( char, referenceString ) )
                    haveErrors = True
                    continue
            if status == 1: # Getting book chapter separator
                if char in self.punctuationDict['bookChapterSeparator']:
                    BBB = self.__BibleOrganizationalSystem.getBBB( bookNameOrAbbreviation )
                    if BBB is None:
                        if errorMessages: logging.error( "Invalid '%s' bookname in Bible reference '%s'" % ( bookNameOrAbbreviation, referenceString ) )
                        haveErrors = True
                    spaceCount = 1 if char==' ' else 0
                    status = 2
                    continue
                elif char.isdigit(): # Must have missed the BCS
                    if errorMessages: logging.warning( "Missing '%s' book/chapter separator when the book name abbreviation was given in '%s'" % (self.punctuationDict['bookChapterSeparator'],referenceString) )
                    haveWarnings = True
                    status = 2 # Fall through below
                else:
                    if errorMessages: logging.error( "Unexpected '%s' character in Bible reference '%s' when getting book/chapter separator" % ( char, referenceString ) )
                    haveErrors = True
                    continue
            if status == 2: # Getting chapter number (or could be the verse number of a one chapter book)
                if char==' ' and not C:
                    spaceCount += 1
                elif char.isdigit():
                    if self.punctuationDict['spaceAllowedAfterBCS']=='Y' and spaceCount<1:
                        if errorMessages: logging.warning( "Missing space after bookname in Bible reference '%s'" % referenceString )
                        haveWarnings = True
                    elif self.punctuationDict['spaceAllowedAfterBCS']=='N' or spaceCount>1:
                        if errorMessages: logging.warning( "Extra space(s) after bookname in Bible reference '%s'" % referenceString )
                        haveWarnings = True
                    C += char
                elif char in allowedVerseSuffixes: # Could be like verse 5b
                    S += char
                elif C and char in self.punctuationDict['chapterVerseSeparator']:
                    status = 3 # Start getting the verse number
                elif C and self.__BibleOrganizationalSystem.isSingleChapterBook( BBB ):
                    V = C
                    C = '1'
                    if char in self.punctuationDict['verseSeparator']:
                        saveReference( BBB, C, V, S, refList )
                        status = 3 # Get the next verse number
                    elif char in self.punctuationDict['bookSeparator']:
                        saveReference( BBB, C, V, S, refList )
                        BBB, C = None, ''
                        status = 0
                    elif char in self.punctuationDict['verseBridgeCharacter']:
                        saveStartReference( BBB, C, V, S )
                        status = 7 # Getting verse range
                    else:
                        if errorMessages: logging.error( "Unexpected '%s' character when processing single chapter book %s in Bible reference '%s'" % ( char, BBB, referenceString ) )
                        haveErrors = True
                    V, S = '', ''
                elif C and char in self.punctuationDict['chapterBridgeCharacter']:
                    saveStartReference( BBB, C, V, S )
                    C, V, S = '', '', ''
                    status = 6 # Getting chapter range
                else:
                    if errorMessages: logging.error( "Unexpected '%s' character when getting chapter number in %s Bible reference '%s'" % ( char, BBB, referenceString ) )
                    haveErrors = True
                continue
            if status == 3: # Getting verse number
                if char == ' ' and not V:
                    if errorMessages: logging.warning( "Extra space(s) after chapter in %s Bible reference '%s'" % ( BBB, referenceString ) )
                    haveWarnings = True
                elif char.isdigit():
                    V += char
                elif char in allowedVerseSuffixes: # Could be like verse 5a
                    S += char
                elif V and char in self.punctuationDict['verseSeparator']:
                    saveReference( BBB, C, V, S, refList )
                    V, S = '', ''
                elif V and (char in self.punctuationDict['chapterSeparator'] or char in self.punctuationDict['bookSeparator']):
                    saveReference( BBB, C, V, S, refList )
                    V = ''
                    if self.punctuationDict['chapterSeparator'] == self.punctuationDict['bookSeparator']:
                        temp, spaceCount = '', 0
                        status = 4 # We don't know what to expect next
                    elif char in self.punctuationDict['chapterSeparator']:
                        C = ''
                        status = 2
                    elif char in self.punctuationDict['bookSeparator']:
                        bookNameOrAbbreviation, BBB, C = '', None, ''
                        status = 0
                elif char in self.punctuationDict['chapterBridgeCharacter']:
                    saveStartReference( BBB, C, V, S )
                    V, S = '', ''
                    if char not in self.punctuationDict['verseBridgeCharacter']: # Must be a chapter bridge
                        C = ''
                        status = 6
                    else: # We don't know what kind of bridge this is
                        X = ''
                        status = 5
                elif char in self.punctuationDict['verseBridgeCharacter']:
                    saveStartReference( BBB, C, V, S )
                    V, S = '', ''
                    status = 7
                else:
                    if errorMessages: logging.error( "Unexpected '%s' character when getting verse number in %s %s Bible reference '%s'" % ( char, BBB, C, referenceString ) )
                    haveErrors = True
                    if V:
                        saveReference( BBB, C, V, S, refList )
                        V, S = '', ''
                continue
            if status == 4: # Getting the next chapter number or book name (not sure which)
                if char == ' ' and not temp:
                    if spaceCount:
                        if errorMessages: logging.warning( "Extra space(s) after chapter or book separator in %s Bible reference '%s'" % ( BBB, referenceString ) )
                        haveWarnings = True
                    spaceCount += 1
                elif char.isalnum():
                    temp += char
                elif char in self.punctuationDict['punctuationAfterBookAbbreviation']:
                    bookNameOrAbbreviation = temp
                    BBB = self.__BibleOrganizationalSystem.getBBB( bookNameOrAbbreviation )
                    C, status = '', 1 # Default to getting BCS
                    if BBB is None:
                        if errorMessages: logging.error( "Invalid '%s' bookname in Bible reference '%s'" % ( bookNameOrAbbreviation, referenceString ) )
                        haveErrors = True
                    else: # we found an unambiguous bookname
                        shortBookName = self.__BibleOrganizationalSystem.getShortBookName( BBB )
                        if shortBookName == bookNameOrAbbreviation: # they entered the full bookname -- we didn't really expect this punctuation
                            if char in self.punctuationDict['bookChapterSeparator']: # ok, they are the same character
                                status = 2 # Just accept this as the BCS and go get the chapter number
                            else:
                                if errorMessages: logging.warning( "Didn't expect '%s' punctuationAfterBookAbbreviation when the full book name was given in '%s'" % (self.punctuationDict['punctuationAfterBookAbbreviation'],referenceString) )
                                haveWarnings = True
                else:
                    #print( "Got '%s'" % temp )
                    if char in self.punctuationDict['chapterVerseSeparator'] and temp and temp.isdigit(): # Assume it's a follow on chapter number
                        C = temp
                        status = 3 # Now get the verse number
                    elif char in self.punctuationDict['bookChapterSeparator']:
                        bookNameOrAbbreviation = temp
                        BBB = self.__BibleOrganizationalSystem.getBBB( bookNameOrAbbreviation )
                        if BBB is None:
                            if errorMessages: logging.error( "Invalid '%s' bookname in Bible reference '%s'" % ( bookNameOrAbbreviation, referenceString ) )
                            haveErrors = True
                        C, V, S = '', '', ''
                        spaceCount = 1 if char==' ' else 0
                        status = 2 # Start getting the chapter number
                    else:
                        if errorMessages: logging.error( "Unexpected '%s' character in Bible reference '%s' when getting book name" % ( char, referenceString ) )
                        haveErrors = True
                continue
            if status == 5: # Get either chapter or verse range
                if char == ' ' and not X:
                    if errorMessages: logging.warning( "Extra space(s) after range bridge in Bible reference '%s'" % referenceString )
                    haveWarnings = True
                elif char.isdigit():
                    X += char
                elif char in allowedVerseSuffixes: # Could be like verse 5a
                    S += char
                elif X and char in self.punctuationDict['chapterVerseSeparator']:
                    C = X
                    V, S = '', ''
                    status = 7
                elif X and char in self.punctuationDict['verseSeparator']:
                    V = X
                    saveReferenceRange( startReferenceTuple, BBB, C, V, S, refList )
                    V, S = '', ''
                    status = 3 # Go get a verse number
                elif X and (char in self.punctuationDict['chapterSeparator'] or char in self.punctuationDict['bookSeparator']):
                    V = X
                    saveReferenceRange( startReferenceTuple, BBB, C, V, S, refList )
                    V, S = '', ''
                    if self.punctuationDict['chapterSeparator'] == self.punctuationDict['bookSeparator']:
                        temp, spaceCount = '', 0
                        status = 4 # We don't know what to expect next
                    elif char in self.punctuationDict['chapterSeparator']:
                        C = ''
                        status = 1
                    elif char in self.punctuationDict['bookSeparator']:
                        bookNameOrAbbreviation, BBB, C = '', None, ''
                        status = 0
                    else: assert( "Should never happen" == 123 )
                else:
                    if errorMessages: logging.error( "Unexpected '%s' character when getting second chapter/verse number in Bible reference '%s'" % ( char, referenceString ) )
                    haveErrors = True
                continue
            if status == 6: # Get chapter range
                if char==' ' and not C:
                    if self.punctuationDict['spaceAllowedAfterBCS']=='N' or spaceCount>1:
                        if errorMessages: logging.warning( "Extra space(s) after bridge character in Bible reference '%s'" % referenceString )
                        haveWarnings = True
                    spaceCount += 1
                elif char.isdigit():
                    if self.punctuationDict['spaceAllowedAfterBCS']=='Y' and spaceCount<1:
                        if errorMessages: logging.warning( "Missing space after bridge character in Bible reference '%s'" % referenceString )
                        haveWarnings = True
                    C += char
                elif C and char in self.punctuationDict['chapterVerseSeparator']:
                    status = 7 # Start getting the verse number
                elif C and self.__BibleOrganizationalSystem.isSingleChapterBook(BBB) and char in self.punctuationDict['verseSeparator']:
                    V = C
                    C = '1'
                    saveReferenceRange( startReferenceTuple, BBB, C, V, S, refList )
                    V, S = '', ''
                    status = 7
                elif C and self.__BibleOrganizationalSystem.isSingleChapterBook(BBB) and char in self.punctuationDict['bookSeparator']:
                    V = C
                    C = '1'
                    saveReferenceRange( startReferenceTuple, BBB, C, V, S, refList )
                    BBB, C, V, S = None, '', '', ''
                    status = 0
                elif C and (char in self.punctuationDict['chapterSeparator'] or char in self.punctuationDict['bookSeparator']):
                    saveReferenceRange( startReferenceTuple, BBB, C, V, S, refList )
                    C, V, S = '', '', ''
                    if self.punctuationDict['chapterSeparator'] == self.punctuationDict['bookSeparator']:
                        temp, spaceCount = '', 0
                        status = 4 # We don't know what to expect next
                    elif char in self.punctuationDict['chapterSeparator']:
                        status = 1
                    elif char in self.punctuationDict['bookSeparator']:
                        bookNameOrAbbreviation, BBB = '', None
                        status = 0
                else:
                    if errorMessages: logging.error( "Unexpected '%s' character in Bible reference '%s' when getting second chapter number" % ( char, referenceString ) )
                    haveErrors = True
                continue
            if status == 7: # Get verse range
                if char == ' ' and not V:
                    if errorMessages: logging.warning( "Extra space(s) after chapter in range in %s Bible reference '%s'" % ( BBB, referenceString ) )
                    haveWarnings = True
                elif char.isdigit() or char in ('a','b','c','d','e'): # Could be like verse 5a
                    V += char
                elif V and char in self.punctuationDict['verseSeparator']:
                    saveReferenceRange( startReferenceTuple, BBB, C, V, S, refList )
                    V, S = '', ''
                elif V and (char in self.punctuationDict['chapterSeparator'] or char in self.punctuationDict['bookSeparator']):
                    saveReferenceRange( startReferenceTuple, BBB, C, V, S, refList )
                    V, S = '', ''
                    if self.punctuationDict['chapterSeparator'] == self.punctuationDict['bookSeparator']:
                        temp, spaceCount = '', 0
                        status = 4 # We don't know what to expect next
                    elif char in self.punctuationDict['chapterSeparator']:
                        C = ''
                        status = 1
                    elif char in self.punctuationDict['bookSeparator']:
                        bookNameOrAbbreviation, BBB, C = '', None, ''
                        status = 0
                else:
                    if errorMessages: logging.error( "Unexpected '%s' character when getting verse number for range in %s %s Bible reference '%s'" % ( char, BBB, C, referenceString ) )
                    haveErrors = True
                    if V:
                        saveReference( BBB, C, V, S )
                        V, S = '', ''
                continue
        if status==2 and C: # Getting chapter number
            if self.__BibleOrganizationalSystem.isSingleChapterBook( BBB ): # Have a single chapter book and what we were given is presumably the verse number
                V = C
                C = '1'
                status = 4
            else: # it must be specifying an entire chapter (like Gen. 3)
                saveReference( BBB, C, V, S, refList )
                status = 9
        elif status==3: # Got a C but still getting the V hopefully
            if V: status = 4
        elif status==4: # Must have ended with a separator character
            if errorMessages: logging.warning( "Bible reference '%s' ended with a separator character" % referenceString )
            haveWarnings = True
            status = 9;
        elif status==5 and X: # Getting C or V range
            V = X
            saveReferenceRange( startReferenceTuple, BBB, C, V, S, refList )
            status = 9
        elif status==6 and C: # Getting C range
            saveReferenceRange( startReferenceTuple, BBB, C, V, S, refList )
            status = 9
        elif status==7 and V: # Getting V range
            saveReferenceRange( startReferenceTuple, BBB, C, V, S, refList )
            status = 9
        if status==4 and not haveErrors:
            saveReference( BBB, C, V, S, refList )
            status = 9

        #if refList: self.checkReferenceRangeList( refList, referenceString, errorMessages=errorMessages )
        self.referenceList = refList
        #print( "Final status: %s -- got '%s'from '%s'\n" % (statusList[status],self.referenceList,referenceString) )

        #print( "here", len(totalVerseList), totalVerseList )
        singleVerseSet = set( totalVerseList )
        if len(singleVerseSet) < len(totalVerseList):
            for entry in singleVerseSet:
                if totalVerseList.count(entry) > 1:
                    #print( entry )
                    if errorMessages: logging.warning( "Have duplicate or overlapping range at %s in Bible references '%s'" % ( self.makeReferenceString(entry), referenceString ) )
            haveWarnings = True
        return status==9 and not haveErrors, haveWarnings, refList
    # end of parseReferenceString

    def getOSISRefList( self ):
        """ Converts a reference list to OSIS format.
                OSIS defines reference ranges
                    e.g., Gen.1.1-Gen.1.2 or Gen.1.1-Gen.2.3 (inclusive).

            We ignore the single lower-case letter verse suffixes. """
        assert( self.referenceList )

        result = ''
        lastBk, lastC, lastV = '', '', ''
        for refOrRefRange in self.referenceList:
            if result: result += self.punctuationDict['bookSeparator'] + ' ' # The separator between multiple references
            if len(refOrRefRange) == 2: # it must be a range (start and end tuples)
                (BBB1, C1, V1, S1), (BBB2, C2, V2, S2) = refOrRefRange
                Bk1 = self.__BibleBooksCodes.getOSISAbbreviation( BBB1 )
                Bk2 = self.__BibleBooksCodes.getOSISAbbreviation( BBB2 )
                if V1 and V2: result += "%s.%s.%s-%s.%s.%s" % (Bk1,C1,V1,Bk2,C2,V2)
                elif not V1 and not V2: result += "%s.%s-%s.%s" % (Bk1,C1,Bk2,C2)
                elif V2: result += "%s.%s.1-%s.%s.%s" % (Bk1,C1,Bk2,C2,V2)
                else: giveUphere
                lastBk, lastC, lastV = Bk2, C2, V2
            else: # It must be a single reference
                BBB, C, V, S = refOrRefRange
                Bk = self.__BibleBooksCodes.getOSISAbbreviation( BBB )
                if V: result += "%s.%s.%s" % (Bk,C,V)
                else: result += "%s.%s" % (Bk,C)
                lastBk, lastC, lastV = Bk, C, V
        #print( "OSIS result is '%s'" % result )
        return result
    # end of getOSISRefList

    def parseToOSIS( self, referenceString, errorMessages=False ):
        """ Just combines the two above routines.
                Parses a reference string and returns an OSIS reference string. """
        successFlag, haveWarnings, refList = self.parseReferenceString( referenceString, errorMessages )
        if successFlag: return self.getOSISRefList()
    # end of parseToOSIS
# end of class BibleReferenceList


def demo():
    """Demonstrate reading and processing some Bible name databases.
    """
    # Handle command line parameters
    from optparse import OptionParser
    parser = OptionParser( version="v%s" % ( versionString ) )
    #parser.add_option("-e", "--export", action="store_true", dest="export", default=False, help="export the XML file to .py and .h tables suitable for directly including into other programs")
    Globals.addStandardOptionsAndProcess( parser )

    if Globals.verbosityLevel > 1: print( "%s V%s" % ( progName, versionString ) )

    BBC = BibleBooksCodes().loadData()
    BOS = BibleOrganizationalSystem( "RSV" )
    printProcessingMessages = False
    wantErrorMessages = False

    if 0:
        print()
        BSR = BibleSingleReference( BBC, BOS )
        print( BSR ) # Just print a summary
        print( "\nSingle Reference (good)" )
        for ref in ("Mat 7:3","Mat.7:3","Mat. 7:3","Mt. 7:3","Mt.7:3","Jde 7","Jde. 7","Jde 1:7","Jde. 1:7","Job 8:4","Job. 8:4","Job8:4","Job  8:4","Lev. 8:4b"):
            if printProcessingMessages: print( "Processing '%s' reference string..." % ref )
            print( "  From '%s' BSR got %s" % (ref, BSR.parseReferenceString(ref,wantErrorMessages)) )
        print( "\nSingle Reference (bad)" )
        for ref in ("Mat 0:3","Mat.7:0","Mat. 77:3","Mt. 7:93","M 7:3","Mit 7:3","Mt. 7:3","Mit. 7:3","Mat. 7:3ab","Mat, 7:3","Mat. 7:3xyz5"):
            if printProcessingMessages: print( "Processing '%s' reference string..." % ref )
            print( "  From '%s' BSR got %s" % (ref, BSR.parseReferenceString(ref,wantErrorMessages)) )

    if 0:
        print()
        BSRs = BibleSingleReferences( BBC, BOS )
        print( BSRs ) # Just print a summary
        print( "\nSingle References (good)" )
        for ref in ("Mat 7:3","Mat.7:3","Mat. 7:3","Mt. 7:3","Mt.7:3","Jde 7","Jde. 7","Jde 1:7","Jde. 1:7","Job 8:4","Job. 8:4","Job8:4","Job  8:4","Lev. 8:4b"):
            if printProcessingMessages: print( "Processing '%s' reference string..." % ref )
            print( "  From '%s' BSRs got %s" % (ref, BSRs.parseReferenceString(ref,wantErrorMessages)) )
        for ref in ("Mat. 7:3,7","Mat. 7:3; 4:7","Mat. 7:3,7; 4:7","Mat. 7:3,7; 4:7,9,11","Mat. 7:3; Heb. 2:2; Rev. 1:1","Mat. 7:3,7; Heb 2:2,9; Rev. 1:1","Mat. 7:3,7; 8:17; Heb 2:2,9; 4:4,7; Rev. 1:1; 1:1","Mrk. 7:3a,7b,8"):
            if printProcessingMessages: print( "Processing '%s' reference string..." % ref )
            print( "  From '%s' BSRs got %s" % (ref, BSRs.parseReferenceString(ref,wantErrorMessages)) )
        print( "\nSingle References (bad)" )
        for ref in ("Mat 0:3","Mat.7:0","Mat. 77:3","Mt. 7:93","M 7:3","Mit 7:3","Mt. 7:3","Mit. 7:3","Mat. 7:3ab","Mat, 7:3","Mat. 7:3xyz5"):
            if printProcessingMessages: print( "Processing '%s' reference string..." % ref )
            print( "  From '%s' BSRs got %s" % (ref, BSRs.parseReferenceString(ref,wantErrorMessages)) )

    if 1:
        print()
        BRL = BibleReferenceList( BBC, BOS )
        print( BRL ) # Just print a summary
        print( BRL.makeReferenceString(("MAT", "7", "3")), BRL.makeReferenceString(("PHM", "1", "3")) )
        print( "\n\nSingle References for Ranges (good)" )
        for ref in ("Mat 7:3","Mat.7:3","Mat. 7:3","Mt. 7:3","Mt.7:3","Jde 7","Jde. 7","Jde 1:7","Jde. 1:7","Job 8:4","Job. 8:4","Job8:4","Job  8:4","Lev. 8:4b", \
                    "Mat. 7:3,7","Mat. 7:3; 4:7","Mat. 7:3,7; 4:7","Mat. 7:3,7; 4:7,9,11","Mat. 7:3; Heb. 2:2; Rev. 1:1","Mat. 7:3,7; Heb 2:2,9; Rev. 1:1","Mat. 7:3,7; 8:17; Heb 2:2,9; 4:4,7; Rev. 1:1; 1:1","Mrk. 7:3a,7b,8"):
            if printProcessingMessages: print( "Processing '%s' reference string..." % ref )
            print( "  From '%s' BRL got %s" % (ref, BRL.parseReferenceString(ref,wantErrorMessages)) )
        print( "\nSingle References for Ranges (bad)" )
        for ref in ("Mat 0:3","Mat.7:0","Mat. 77:3","Mt. 7:93","M 7:3","Mit 7:3","Mt. 7:3","Mit. 7:3","Mat. 7:3ab","Mat, 7:3","Mat. 7:3xyz5"):
            if printProcessingMessages: print( "Processing '%s' reference string..." % ref )
            print( "  From '%s' BSRs got %s" % (ref, BRL.parseReferenceString(ref,wantErrorMessages)) )
        print( "\n\nSingle Ranges (good)" )
        for ref in ("Mat 7:3-7","Mat.7:3-11","Mat. 7:13-8:2","Mt. 7:3,5-9","Mt.7:3-4,6-9","Jde 7-8","Jde. 1-3","Jde 1:7-8","Jud. 1:1-3,5,7-9","EXO.4:14,27c-30;  5:1,4,20; 6:13,20,23,25-27a; 7:1,2,6b-10a,10,12,19,20; 8:1,2,4,8,12,13,21;"):
            if printProcessingMessages: print( "Processing '%s' reference string..." % ref )
            print( "  From '%s' BRL got %s" % (ref, BRL.parseReferenceString(ref,wantErrorMessages)) )
            print( "OSIS result is '%s'" % BRL.getOSISRefList() )
        print( "\nSingle Ranges (bad)" )
        for ref in ("EXO.4:14-12; NUM.3:12-1:5; JOS.4:5-5","Mt. 7:7;"):
            if printProcessingMessages: print( "Processing '%s' reference string..." % ref )
            print( "  From '%s' BRL got %s" % (ref, BRL.parseReferenceString(ref,wantErrorMessages)) )
        print( "\n\nNow some chapter Ranges (good)" )
        for ref in ("Dan. 5","Gen. 1-11","Act.4-7; Mat.5-7"):
            if printProcessingMessages: print( "Processing '%s' reference string..." % ref )
            print( "  From '%s' BRL got %s" % (ref, BRL.parseReferenceString(ref,wantErrorMessages)) )
            #print( "OSIS result is '%s'" % BRL.getOSISRefList() )
        print( "\nNow some chapter Ranges (bad)" )
        for ref in ("Tit. 1:2; 1:2-7","Jer. 95","Exo. 23-99","1 Cor.9-7; 1Tim.5-7:2"):
            if printProcessingMessages: print( "Processing '%s' reference string..." % ref )
            print( "  From '%s' BRL got %s" % (ref, BRL.parseReferenceString(ref,wantErrorMessages)) )
        for ref in ("Jhn. 3:16", "Rev. 2:1-3" ):
            if printProcessingMessages: print( "Processing '%s' reference string..." % ref )
            print( "  From '%s' BRL got OSIS '%s'" % (ref, BRL.parseToOSIS(ref,wantErrorMessages)) )

if __name__ == '__main__':
    demo()
# end of BibleReferences.py
