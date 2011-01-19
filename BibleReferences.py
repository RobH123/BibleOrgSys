#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# BibleReferences.py
#
# Module for handling Bible references including ranges
#   Last modified: 2011-01-19 (also update versionString below)
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
    S is the single lowercase letter suffix (see allowedVerseSuffixes from the punctuation system)

OSIS defines reference ranges
    e.g., Gen.1.1-Gen.1.2 or Gen.1.1-Gen.2.3 (inclusive)

Our ranges are slightly different (also inclusive)
    e.g., Gen_1:1-Gen_1:2 but Gen_1:1-Gen_2:3
    i.e., using a hyphen for a verse span but xxx for a span that crosses chapters.

OXES is different again.
"""

progName = "Bible References handler"
versionString = "0.21"


import os, logging
from gettext import gettext as _

import Globals
from BibleBooksCodes import BibleBooksCodes
from BibleOrganizationalSystems import BibleOrganizationalSystem


# This is a hack because it's language dependant :(
ignoredSuffixes = (' (LXX)',) # A hack to cope with these suffixes in cross-references and footnotes :(


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
        if self.reference: result += ('\n' if result else '') + "  {}".format( str(self.reference) )
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
            logging.warning( _("Reference string '{}' contains surrounding space(s)").format( referenceString ) )
            haveWarnings = True
        #statusList = {0:"gettingBookname", 1:"gettingBCSeparator", 2:"gettingChapter", 3:"gettingVerse", 4:"gotCV", 5:"done", 9:"finished"}
        status, bookNameOrAbbreviation, BBB, C, V, S, spaceCount = 0, '', None, '', '', '', 0
        for nn, char in enumerate(strippedReferenceString):
            #print( "Status: {} -- got '{}'".format(statusList[status],char) )
            if status == 0: # Getting bookname (with or without punctuation after book abbreviation)
                if char.isalnum():
                    if char.isdigit() and bookNameOrAbbreviation: # Could this be the chapter number?
                        BBB = self.__BibleOrganizationalSystem.getBBB( bookNameOrAbbreviation )
                        if BBB is None: # Don't seem to have a valid bookname yet
                            bookNameOrAbbreviation += char
                            continue
                        # else if seems we have a valid bookname -- let's assume this might be the chapter number
                        logging.error( _("It seems that the bookname might be joined onto the chapter number in Bible reference '{}'").format(referenceString) )
                        status = 2 # Start getting the chapter number
                    else:
                        bookNameOrAbbreviation += char
                        continue
                elif 'punctuationAfterBookAbbreviation' in self.punctuationDict and char in self.punctuationDict['punctuationAfterBookAbbreviation']:
                    BBB = self.__BibleOrganizationalSystem.getBBB( bookNameOrAbbreviation )
                    status = 1 # Default to getting BCS
                    if BBB is None:
                        logging.error( _("Invalid '{}' bookname in Bible reference '{}'").format( bookNameOrAbbreviation, referenceString ) )
                        haveErrors = True
                    else: # we found an unambiguous bookname
                        shortBookName = self.__BibleOrganizationalSystem.getShortBookName( BBB )
                        if shortBookName == bookNameOrAbbreviation: # they entered the full bookname -- we didn't really expect this punctuation
                            if char in self.punctuationDict['bookChapterSeparator']: # ok, they are the same character
                                status = 2 # Just accept this as the BCS and go get the chapter number
                            else:
                                logging.warning( _("Didn't expect '{}' punctuationAfterBookAbbreviation when the full book name was given in '{}'").format(self.punctuationDict['punctuationAfterBookAbbreviation'],referenceString) )
                                haveWarnings = True
                    continue
                elif char in self.punctuationDict['bookChapterSeparator']:
                    BBB = self.__BibleOrganizationalSystem.getBBB( bookNameOrAbbreviation )
                    if BBB is None:
                        logging.error( _("Invalid '{}' bookname in Bible reference '{}'").format( bookNameOrAbbreviation, referenceString ) )
                        haveErrors = True
                    else: # we found an unambiguous bookname
                        shortBookName = self.__BibleOrganizationalSystem.getShortBookName( BBB )
                        if shortBookName != bookNameOrAbbreviation: # they didn't enter the full bookname -- we really expect the punctuationAfterBookAbbreviation
                            if 'punctuationAfterBookAbbreviation' in self.punctuationDict and self.punctuationDict['punctuationAfterBookAbbreviation']:
                                logging.warning( _("Missing '{}' punctuationAfterBookAbbreviation when the book name abbreviation was given in '{}'").format(self.punctuationDict['punctuationAfterBookAbbreviation'],referenceString) )
                                haveWarnings = True
                    spaceCount = 1 if char==' ' else 0
                    status = 2
                    continue
                else:
                    logging.error( _("Unexpected '{}' character in Bible reference '{}' when getting book name").format( char, referenceString ) )
                    haveErrors = True
                    continue
            if status == 1: # Getting book chapter separator
                if char in self.punctuationDict['bookChapterSeparator']:
                    BBB = self.__BibleOrganizationalSystem.getBBB( bookNameOrAbbreviation )
                    if BBB is None:
                        logging.error( _("Invalid '{}' bookname in Bible reference '{}'").format( bookNameOrAbbreviation, referenceString ) )
                        haveErrors = True
                    spaceCount = 1 if char==' ' else 0
                    status = 2
                    continue
                elif char.isdigit(): # Must have missed the BCS
                    logging.warning( _("Missing '{}' book/chapter separator when the book name abbreviation was given in '{}'").format(self.punctuationDict['bookChapterSeparator'],referenceString) )
                    haveWarnings = True
                    status = 2 # Fall through below
                else:
                    logging.error( _("Unexpected '{}' character in Bible reference '{}' when getting book/chapter separator").format( char, referenceString ) )
                    haveErrors = True
                    continue
            if status == 2: # Getting chapter number (or could be the verse number of a one chapter book)
                if char==' ' and not C:
                    spaceCount += 1
                elif char.isdigit():
                    if self.punctuationDict['spaceAllowedAfterBCS']=='Y' and spaceCount<1:
                        logging.warning( _("Missing space after bookname in Bible reference '{}'").format( referenceString ) )
                        haveWarnings = True
                    elif self.punctuationDict['spaceAllowedAfterBCS']=='N' or spaceCount>1:
                        logging.warning( _("Extra space(s) after bookname in Bible reference '{}'").format( referenceString ) )
                        haveWarnings = True
                    C += char
                elif char in self.punctuationDict['allowedVerseSuffixes']: # Could be like verse 5b
                    S += char
                elif C and char in self.punctuationDict['chapterVerseSeparator']:
                    status = 3 # Start getting the verse number
                else:
                    logging.error( _("Unexpected '{}' character when getting chapter number in {} Bible reference '{}'").format( char, BBB, referenceString ) )
                    haveErrors = True
                continue
            if status == 3: # Getting verse number
                if char == ' ' and not V:
                    logging.warning( _("Extra space(s) after chapter in {} Bible reference '{}'").format( BBB, referenceString ) )
                    haveWarnings = True
                elif char.isdigit():
                    V += char
                elif char in self.punctuationDict['allowedVerseSuffixes']: # Could be like verse 5b
                    S += char
                else:
                    logging.error( _("Unexpected '{}' character when getting verse number in {} {} Bible reference '{}'").format( char, BBB, C, referenceString ) )
                    haveErrors = True
                    if V: status = 4
                continue
        if status==3: # Got a C but still getting the V hopefully
            if V: status = 4
        if len(S) > 1:
            logging.error( _("Unexpected long '{}' suffix in {} Bible reference '{}'").format( S, BBB, referenceString ) )
            haveErrors = True
            S = S[0] # Just take the first one
        if BBB is not None:
            if status==2 and C and self.__BibleOrganizationalSystem.isSingleChapterBook( BBB ): # Have a single chapter book and what we were given is presumably the verse number
                    V = C
                    C = '1'
                    status = 4
            if status>=4 and not haveErrors:
                if self.__BibleOrganizationalSystem.isValidBCVRef( (BBB, C, V, S), referenceString, wantErrorMessages=True ):
                    status = 9
        self.reference = (BBB, C, V, S,)
        #print( "Final status: {} -- got '{}'from '{}'\n".format(statusList[status],self.reference,referenceString) )
        return status==9 and not haveErrors, haveWarnings, BBB, C, V, S
    # end of parseReferenceString
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
        if self.referenceList: result += ('\n' if result else '') + "  {}".format( self.referenceList )
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
                logging.error( _("Unexpected long '{}' suffix in {} Bible reference '{}'").format( S, BBB, referenceString ) )
                haveErrors = True
                S = S[0] # Just take the first one
            refTuple = ( BBB, C, V, S, )
            if refTuple in refList:
                logging.warning( _("Reference {} is repeated in Bible reference '{}'").format( refTuple, referenceString ) )
                haveWarnings = True
            if not self.__BibleOrganizationalSystem.isValidBCVRef( refTuple, referenceString, wantErrorMessages=True ):
                haveErrors = True
            refList.append( refTuple )
        # end of saveReference

        #print( "Processing '{}'".format( referenceString ) )
        assert( referenceString )
        haveWarnings, haveErrors = False, False
        strippedReferenceString = referenceString.strip()
        if strippedReferenceString != referenceString:
            logging.warning( _("Reference string '{}' contains surrounding space(s)").format( referenceString ) )
            haveWarnings = True
        #statusList = {0:"gettingBookname", 1:"gettingBCSeparator", 2:"gettingChapter", 3:"gettingVerse", 4:"gettingNextBorC", 5:"done", 9:"finished"}
        status, bookNameOrAbbreviation, BBB, C, V, S, spaceCount, refList = 0, '', None, '', '', '', 0, []
        for nn, char in enumerate(strippedReferenceString):
            #print( "Status: {} -- got '{}'".format(statusList[status],char) )
            if status == 0: # Getting bookname (with or without punctuation after book abbreviation)
                if char.isalnum():
                    if char.isdigit() and bookNameOrAbbreviation: # Could this be the chapter number?
                        BBB = self.__BibleOrganizationalSystem.getBBB( bookNameOrAbbreviation )
                        if BBB is None: # Don't seem to have a valid bookname yet
                            bookNameOrAbbreviation += char
                            continue
                        # else if seems we have a valid bookname -- let's assume this might be the chapter number
                        logging.error( _("It seems that the bookname might be joined onto the chapter number in Bible reference '{}'").format(referenceString) )
                        status = 2 # Start getting the chapter number
                    else:
                        bookNameOrAbbreviation += char
                        continue
                elif 'punctuationAfterBookAbbreviation' in self.punctuationDict and char in self.punctuationDict['punctuationAfterBookAbbreviation']:
                    BBB = self.__BibleOrganizationalSystem.getBBB( bookNameOrAbbreviation )
                    status = 1 # Default to getting BCS
                    if BBB is None:
                        logging.error( _("Invalid '{}' bookname in Bible reference '{}'").format( bookNameOrAbbreviation, referenceString ) )
                        haveErrors = True
                    else: # we found an unambiguous bookname
                        shortBookName = self.__BibleOrganizationalSystem.getShortBookName( BBB )
                        if shortBookName == bookNameOrAbbreviation: # they entered the full bookname -- we didn't really expect this punctuation
                            if char in self.punctuationDict['bookChapterSeparator']: # ok, they are the same character
                                status = 2 # Just accept this as the BCS and go get the chapter number
                            else:
                                logging.warning( _("Didn't expect '{}' punctuationAfterBookAbbreviation when the full book name was given in '{}'").format(self.punctuationDict['punctuationAfterBookAbbreviation'],referenceString) )
                                haveWarnings = True
                    continue
                elif char in self.punctuationDict['bookChapterSeparator']:
                    BBB = self.__BibleOrganizationalSystem.getBBB( bookNameOrAbbreviation )
                    if BBB is None:
                        logging.error( _("Invalid '{}' bookname in Bible reference '{}'").format( bookNameOrAbbreviation, referenceString ) )
                        haveErrors = True
                    else: # we found an unambiguous bookname
                        shortBookName = self.__BibleOrganizationalSystem.getShortBookName( BBB )
                        if shortBookName != bookNameOrAbbreviation: # they didn't enter the full bookname -- we really expect the punctuationAfterBookAbbreviation
                            if 'punctuationAfterBookAbbreviation' in self.punctuationDict and self.punctuationDict['punctuationAfterBookAbbreviation']:
                                logging.warning( _("Missing '{}' punctuationAfterBookAbbreviation when the book name abbreviation was given in '{}'").format(self.punctuationDict['punctuationAfterBookAbbreviation'],referenceString) )
                                haveWarnings = True
                    spaceCount = 1 if char==' ' else 0
                    status = 2
                    continue
                else:
                    logging.error( _("Unexpected '{}' character in Bible reference '{}' when getting book name").format( char, referenceString ) )
                    haveErrors = True
                    continue
            if status == 1: # Getting book chapter separator
                if char in self.punctuationDict['bookChapterSeparator']:
                    BBB = self.__BibleOrganizationalSystem.getBBB( bookNameOrAbbreviation )
                    if BBB is None:
                        logging.error( _("Invalid '{}' bookname in Bible reference '{}'").format( bookNameOrAbbreviation, referenceString ) )
                        haveErrors = True
                    spaceCount = 1 if char==' ' else 0
                    status = 2
                    continue
                elif char.isdigit(): # Must have missed the BCS
                    logging.warning( _("Missing '{}' book/chapter separator when the book name abbreviation was given in '{}'").format(self.punctuationDict['bookChapterSeparator'],referenceString) )
                    haveWarnings = True
                    status = 2 # Fall through below
                else:
                    logging.error( _("Unexpected '{}' character in Bible reference '{}' when getting book/chapter separator").format( char, referenceString ) )
                    haveErrors = True
                    continue
            if status == 2: # Getting chapter number (or could be the verse number of a one chapter book)
                if char==' ' and not C:
                    spaceCount += 1
                elif char.isdigit():
                    if self.punctuationDict['spaceAllowedAfterBCS']=='Y' and spaceCount<1:
                        logging.warning( _("Missing space after bookname in Bible reference '{}'").format( referenceString ) )
                        haveWarnings = True
                    elif self.punctuationDict['spaceAllowedAfterBCS']=='N' or spaceCount>1:
                        logging.warning( _("Extra space(s) after bookname in Bible reference '{}'").format( referenceString ) )
                        haveWarnings = True
                    C += char
                elif char in self.punctuationDict['allowedVerseSuffixes']: # Could be like verse 5b
                    S += char
                elif C and char in self.punctuationDict['chapterVerseSeparator']:
                    status = 3 # Start getting the verse number
                else:
                    logging.error( _("Unexpected '{}' character when getting chapter number in {} Bible reference '{}'").format( char, BBB, referenceString ) )
                    haveErrors = True
                continue
            if status == 3: # Getting verse number
                if char == ' ' and not V:
                    logging.warning( _("Extra space(s) after chapter in {} Bible reference '{}'").format( BBB, referenceString ) )
                    haveWarnings = True
                elif char.isdigit():
                    V += char
                elif char in self.punctuationDict['allowedVerseSuffixes']: # Could be like verse 5b
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
                    logging.error( _("Unexpected '{}' character when getting verse number in {} {} Bible reference '{}'").format( char, BBB, C, referenceString ) )
                    haveErrors = True
                    if V:
                        saveReference( BBB, C, V, S, refList )
                        V, S = '', ''
                continue
            if status == 4: # Getting the next chapter number or book name (not sure which)
                if char == ' ' and not temp:
                    if spaceCount:
                        logging.warning( _("Extra space(s) after chapter or book separator in {} Bible reference '{}'").format( BBB, referenceString ) )
                        haveWarnings = True
                    spaceCount += 1
                elif char.isalnum():
                    temp += char
                elif 'punctuationAfterBookAbbreviation' in self.punctuationDict and char in self.punctuationDict['punctuationAfterBookAbbreviation']:
                    bookNameOrAbbreviation = temp
                    BBB = self.__BibleOrganizationalSystem.getBBB( bookNameOrAbbreviation )
                    C, status = '', 1 # Default to getting BCS
                    if BBB is None:
                        logging.error( _("Invalid '{}' bookname in Bible reference '{}'").format( bookNameOrAbbreviation, referenceString ) )
                        haveErrors = True
                    else: # we found an unambiguous bookname
                        shortBookName = self.__BibleOrganizationalSystem.getShortBookName( BBB )
                        if shortBookName == bookNameOrAbbreviation: # they entered the full bookname -- we didn't really expect this punctuation
                            if char in self.punctuationDict['bookChapterSeparator']: # ok, they are the same character
                                status = 2 # Just accept this as the BCS and go get the chapter number
                            else:
                                logging.warning( _("Didn't expect '{}' punctuationAfterBookAbbreviation when the full book name was given in '{}'").format(self.punctuationDict['punctuationAfterBookAbbreviation'],referenceString) )
                                haveWarnings = True
                else:
                    #print( "Got '{}'".format( temp ) )
                    if char in self.punctuationDict['chapterVerseSeparator'] and temp and temp.isdigit(): # Assume it's a follow on chapter number
                        C = temp
                        status = 3 # Now get the verse number
                    elif char in self.punctuationDict['bookChapterSeparator']:
                        bookNameOrAbbreviation = temp
                        BBB = self.__BibleOrganizationalSystem.getBBB( bookNameOrAbbreviation )
                        if BBB is None:
                            logging.error( _("Invalid '{}' bookname in Bible reference '{}'").format( bookNameOrAbbreviation, referenceString ) )
                            haveErrors = True
                        C, V, S = '', '', ''
                        spaceCount = 1 if char==' ' else 0
                        status = 2 # Start getting the chapter number
                    else:
                        logging.error( _("Unexpected '{}' character in Bible reference '{}' when getting book name").format( char, referenceString ) )
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
        #print( "Final status: {} -- got '{}'from '{}'\n".format(statusList[status],self.referenceList,referenceString) )
        return status==9 and not haveErrors, haveWarnings, self.referenceList
    # end of parseReferenceString
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
        if self.referenceList: result += ('\n' if result else '') + "  {}".format( self.referenceList )
        return result
    # end of __str__

    def makeReferenceString( self, refTuple ):
        """
        Makes a string out of a reference tuple
        """
        assert( refTuple )
        lenRef = len( refTuple )
        if lenRef == 2: (BBB, C), V, S = refTuple, '', ''
        elif lenRef == 3: (BBB, C, V), S = refTuple, ''
        elif lenRef == 4: BBB, C, V, S = refTuple
        else: logging.error( _("Unrecognized {} parameter to makeReferenceString").format( refTuple ) ); return None

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
            resultString = "{}{}{}{}".format( BBBstr, BCS, ' ' if self.punctuationDict['spaceAllowedAfterBCS']=='Y' else '', V )
        else: # it's a book with multiple chapters
            resultString = "{}{}{}{}{}{}".format( BBBstr, BCS, ' ' if self.punctuationDict['spaceAllowedAfterBCS']=='Y' else '', C, CVS, V )
        return resultString
    # end of makeReferenceString

    def parseReferenceString( self, referenceString, wantErrorMessages=False ):
        """
        Returns a tuple with True/False result, haveWarnings, list of (BBB, C, V, S) tuples.
            A range is expressed as a tuple containing a pair of (BBB, C, V, S) tuples.

        All parsed references are checked for validity against the versification system.

        We could rewrite this using RegularExpressions, but would it be able to give such precise formatting error messages?
        """

        def saveReference( BBB, C, V, S, refList ):
            """ Checks the reference info then saves it as a referenceTuple in the refList. """
            nonlocal haveErrors, haveWarnings, totalVerseList
            if len(S) > 1:
                if wantErrorMessages: logging.error( _("Unexpected long '{}' suffix in {} Bible reference '{}'").format( S, BBB, referenceString ) )
                haveErrors = True
                S = S[0] # Just take the first one
            refTuple = ( BBB, C, V, S, )
            if refTuple in refList:
                if wantErrorMessages: logging.warning( _("Reference {} is repeated in Bible reference '{}'").format( refTuple, referenceString ) )
                haveWarnings = True
            if not self.__BibleOrganizationalSystem.isValidBCVRef( refTuple, referenceString, wantErrorMessages ):
                haveErrors = True
            refList.append( refTuple )
            totalVerseList.append( refTuple )
        # end of saveReference

        def saveStartReference( BBB, C, V, S ):
            """ Checks the reference info then saves it as a referenceTuple. """
            nonlocal haveErrors, haveWarnings, startReferenceTuple
            if len(S) > 1:
                if wantErrorMessages: logging.error( _("Unexpected long '{}' suffix in {} Bible reference '{}'").format( S, BBB, referenceString ) )
                haveErrors = True
                S = S[0] # Just take the first one
            startReferenceTuple = ( BBB, C, V, S, )
            if not self.__BibleOrganizationalSystem.isValidBCVRef( startReferenceTuple, referenceString, wantErrorMessages ):
                haveErrors = True
        # end of saveStartReference

        def saveReferenceRange( startTuple, BBB, C, V, S, refList ):
            """ Checks the reference info then saves it as a referenceTuple in the refList. """
            nonlocal haveErrors, haveWarnings, totalVerseList
            if len(S) > 1:
                if wantErrorMessages: logging.error( _("Unexpected long '{}' suffix in {} Bible reference '{}'").format( S, BBB, referenceString ) )
                haveErrors = True
                S = S[0] # Just take the first one
            finishTuple = ( BBB, C, V, S, )
            if not self.__BibleOrganizationalSystem.isValidBCVRef( finishTuple, referenceString, wantErrorMessages=False ): # No error messages here because it will be caught at expandCVRange below
                haveErrors = True # Just set this flag
            rangeTuple = (startTuple, finishTuple,)
            verseList = self.__BibleOrganizationalSystem.expandCVRange( startTuple, finishTuple, referenceString, self.__BibleOrganizationalSystem, wantErrorMessages=wantErrorMessages )
            if verseList is not None: totalVerseList.extend( verseList )
            if rangeTuple in refList:
                if wantErrorMessages: logging.warning( _("Reference range {} is repeated in Bible reference '{}'").format( rangeTuple, referenceString ) )
                haveWarnings = True
            refList.append( rangeTuple )
        # end of saveReferenceRange

        #print( "Processing '{}'".format( referenceString ) )
        assert( referenceString )
        haveWarnings, haveErrors, totalVerseList = False, False, []
        strippedReferenceString = referenceString.strip()
        if strippedReferenceString != referenceString:
            if wantErrorMessages: logging.warning( _("Reference string '{}' contains surrounding space(s)").format( referenceString ) )
            haveWarnings = True
        adjustedReferenceString = strippedReferenceString
        for value in ignoredSuffixes:
            adjustedReferenceString = adjustedReferenceString.replace( value, '' )
        #statusList = {0:"gettingBookname", 1:"gettingBCSeparator", 2:"gettingChapter", 3:"gettingVerse", 4:"gettingNextBorC", 5:"gettingBorCorVRange", 6:"gettingBRange", 7:"gettingCRange", 8:"gettingVRange", 9:"finished"}
        status, bookNameOrAbbreviation, BBB, C, V, S, spaceCount, startReferenceTuple, self.referenceList = 0, '', None, '', '', '', 0, (), []
        for nn, char in enumerate(adjustedReferenceString):
            nnn = referenceString.find( char, nn ) # Best guess of where this char might be in the original reference string (which we will display to users in error messages)
            if nnn!=nn:
                assert( adjustedReferenceString != referenceString )
                print( nn, nnn, "'"+referenceString+"'", "'"+adjustedReferenceString+"'" )
            #if referenceString.startswith('Num 22'):
            #    print( "Status: {}:{} -- got '{}'".format(status, statusList[status],char), haveErrors, haveWarnings, self.referenceList )
            if status == 0: # Getting bookname (with or without punctuation after book abbreviation)
                if char.isalnum():
                    if char.isdigit() and bookNameOrAbbreviation: # Could this be the chapter number?
                        BBB = self.__BibleOrganizationalSystem.getBBB( bookNameOrAbbreviation )
                        if BBB is None: # Don't seem to have a valid bookname yet
                            bookNameOrAbbreviation += char
                            continue
                        # else if seems we have a valid bookname -- let's assume this might be the chapter number
                        if wantErrorMessages: logging.error( _("It seems that the bookname might be joined onto the chapter number at position {} in Bible reference '{}'").format(nnn, referenceString) )
                        status = 2 # Start getting the chapter number immediately (no "continue" here)
                    else:
                        bookNameOrAbbreviation += char
                        continue
                elif bookNameOrAbbreviation and char == ' ': # Could be something like 1 Cor
                    BBB = self.__BibleOrganizationalSystem.getBBB( bookNameOrAbbreviation )
                    if BBB is None: # Don't seem to have a valid bookname yet
                        bookNameOrAbbreviation += char
                        continue
                if 'punctuationAfterBookAbbreviation' in self.punctuationDict and char in self.punctuationDict['punctuationAfterBookAbbreviation']:
                    BBB = self.__BibleOrganizationalSystem.getBBB( bookNameOrAbbreviation )
                    status = 1 # Default to getting BCS
                    if BBB is None:
                        if wantErrorMessages: logging.error( _("Invalid '{}' bookname at position {} in Bible reference '{}'").format( bookNameOrAbbreviation, nnn, referenceString ) )
                        haveErrors = True
                    else: # we found an unambiguous bookname
                        shortBookName = self.__BibleOrganizationalSystem.getShortBookName( BBB )
                        if shortBookName == bookNameOrAbbreviation: # they entered the full bookname -- we didn't really expect this punctuation
                            if char in self.punctuationDict['bookChapterSeparator']: # ok, they are the same character
                                status = 2 # Just accept this as the BCS and go get the chapter number
                            else:
                                if wantErrorMessages: logging.warning( _("Didn't expect '{}' punctuationAfterBookAbbreviation when the full book name was given at position {} in '{}'").format(self.punctuationDict['punctuationAfterBookAbbreviation'],nnn,referenceString) )
                                haveWarnings = True
                    continue
                elif char in self.punctuationDict['bookChapterSeparator']:
                    BBB = self.__BibleOrganizationalSystem.getBBB( bookNameOrAbbreviation )
                    if BBB is None:
                        if wantErrorMessages: logging.error( _("Invalid '{}' bookname in Bible reference '{}'").format( bookNameOrAbbreviation, referenceString ) )
                        haveErrors = True
                    else: # we found an unambiguous bookname
                        shortBookName = self.__BibleOrganizationalSystem.getShortBookName( BBB )
                        if shortBookName != bookNameOrAbbreviation: # they didn't enter the full bookname -- we really expect the punctuationAfterBookAbbreviation
                            if 'punctuationAfterBookAbbreviation' in self.punctuationDict and self.punctuationDict['punctuationAfterBookAbbreviation']:
                                if wantErrorMessages: logging.warning( _("Missing '{}' punctuationAfterBookAbbreviation when the book name abbreviation was given at position {} in '{}'").format(self.punctuationDict['punctuationAfterBookAbbreviation'],nnn,referenceString) )
                                haveWarnings = True
                    spaceCount = 1 if char==' ' else 0
                    status = 2
                    continue
                else:
                    if wantErrorMessages: logging.error( _("Unexpected '{}' character  when getting book name at position {} in Bible reference '{}'").format( char, nnn, referenceString ) )
                    haveErrors = True
                    continue
            if status == 1: # Getting book chapter separator
                if char in self.punctuationDict['bookChapterSeparator']:
                    BBB = self.__BibleOrganizationalSystem.getBBB( bookNameOrAbbreviation )
                    if BBB is None:
                        if wantErrorMessages: logging.error( _("Invalid '{}' bookname at position {} in Bible reference '{}'").format( bookNameOrAbbreviation, nnn, referenceString ) )
                        haveErrors = True
                    spaceCount = 1 if char==' ' else 0
                    status = 2
                    continue
                elif char.isdigit(): # Must have missed the BCS
                    if wantErrorMessages: logging.warning( _("Missing '{}' book/chapter separator when the book name abbreviation was given at position {} in '{}'").format(self.punctuationDict['bookChapterSeparator'],nnn,referenceString) )
                    haveWarnings = True
                    status = 2 # Fall through below
                else:
                    if wantErrorMessages: logging.error( _("Unexpected '{}' character when getting book/chapter separator at position {} in Bible reference '{}'").format( char, nnn, referenceString ) )
                    haveErrors = True
                    continue
            if status == 2: # Getting chapter number (or could be the verse number of a one chapter book)
                if char==' ' and not C:
                    spaceCount += 1
                elif char.isdigit():
                    if self.punctuationDict['spaceAllowedAfterBCS']=='Y' and spaceCount<1:
                        if wantErrorMessages: logging.warning( _("Missing space after bookname at position {} in Bible reference '{}'").format( nnn, referenceString ) )
                        haveWarnings = True
                    elif self.punctuationDict['spaceAllowedAfterBCS']=='N' or spaceCount>1:
                        if wantErrorMessages: logging.warning( _("Extra space(s) after bookname at position {} in Bible reference '{}'").format( nnn, referenceString ) )
                        haveWarnings = True
                    C += char
                elif char in self.punctuationDict['allowedVerseSuffixes']: # Could be like verse 5b
                    S += char
                elif C and char in self.punctuationDict['chapterVerseSeparator']:
                    status = 3 # Start getting the verse number
                elif C and self.__BibleOrganizationalSystem.isSingleChapterBook( BBB ):
                    V = C
                    C = '1'
                    if char in self.punctuationDict['verseSeparator']:
                        saveReference( BBB, C, V, S, self.referenceList )
                        status = 3 # Get the next verse number
                    elif char in self.punctuationDict['bookSeparator']:
                        saveReference( BBB, C, V, S, self.referenceList )
                        BBB, C = None, ''
                        status = 0
                    elif char in self.punctuationDict['verseBridgeCharacter']:
                        saveStartReference( BBB, C, V, S )
                        status = 8 # Getting verse range
                    else:
                        if wantErrorMessages: logging.error( _("Unexpected '{}' character when processing single chapter book {} at position {} in Bible reference '{}'").format( char, BBB, nnn, referenceString ) )
                        haveErrors = True
                    V, S = '', ''
                elif C and char in self.punctuationDict['chapterBridgeCharacter']:
                    saveStartReference( BBB, C, V, S )
                    status, C, V, S = 7, '', '', '' # Getting chapter range
                else:
                    if wantErrorMessages: logging.error( _("Unexpected '{}' character when getting chapter number at position {} in {} Bible reference '{}'").format( char, BBB, nnn, referenceString ) )
                    haveErrors = True
                continue
            if status == 3: # Getting verse number
                if char == ' ' and not V:
                    if wantErrorMessages: logging.warning( _("Extra space(s) after chapter at position {} in {} Bible reference '{}'").format( nnn, BBB, referenceString ) )
                    haveWarnings = True
                elif char.isdigit():
                    V += char
                elif char in self.punctuationDict['allowedVerseSuffixes']: # Could be like verse 5a
                    S += char
                elif V and char in self.punctuationDict['verseSeparator']:
                    saveReference( BBB, C, V, S, self.referenceList )
                    V, S = '', ''
                elif V and (char in self.punctuationDict['chapterSeparator'] or char in self.punctuationDict['bookSeparator']):
                    saveReference( BBB, C, V, S, self.referenceList )
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
                elif char in self.punctuationDict['bookBridgeCharacter']:
                    saveStartReference( BBB, C, V, S )
                    V, S = '', ''
                    if char not in self.punctuationDict['chapterBridgeCharacter'] and char not in self.punctuationDict['verseBridgeCharacter']: # Must be a chapter bridge
                        status, BBB, C = 6, None, ''
                    else: # We don't know what kind of bridge this is
                        status, X = 5, ''
                elif char in self.punctuationDict['chapterBridgeCharacter']:
                    saveStartReference( BBB, C, V, S )
                    V, S = '', ''
                    if char not in self.punctuationDict['verseBridgeCharacter']: # Must be a chapter bridge
                        status, C = 7, ''
                    else: # We don't know what kind of bridge this is
                        status, X = 5, ''
                elif char in self.punctuationDict['verseBridgeCharacter']:
                    saveStartReference( BBB, C, V, S )
                    status, V, S = 8, '', ''
                else:
                    if wantErrorMessages: logging.error( _("Unexpected '{}' character when getting verse number at position {} in {} {} Bible reference '{}'").format( char, nnn, BBB, C, referenceString ) )
                    haveErrors = True
                    if V:
                        saveReference( BBB, C, V, S, self.referenceList )
                        V, S = '', ''
                continue
            if status == 4: # Getting the next chapter number or book name (not sure which)
                if char == ' ' and not temp:
                    if spaceCount:
                        if wantErrorMessages: logging.warning( _("Extra space(s) after chapter or book separator at position {} in {} Bible reference '{}'").format( nnn, BBB, referenceString ) )
                        haveWarnings = True
                    spaceCount += 1
                elif char.isalnum():
                    temp += char
                elif 'punctuationAfterBookAbbreviation' in self.punctuationDict and char in self.punctuationDict['punctuationAfterBookAbbreviation']:
                    bookNameOrAbbreviation = temp
                    BBB = self.__BibleOrganizationalSystem.getBBB( bookNameOrAbbreviation )
                    status, C = 1, '' # Default to getting BCS
                    if BBB is None:
                        if wantErrorMessages: logging.error( _("Invalid '{}' bookname in Bible reference '{}'").format( bookNameOrAbbreviation, referenceString ) )
                        haveErrors = True
                    else: # we found an unambiguous bookname
                        shortBookName = self.__BibleOrganizationalSystem.getShortBookName( BBB )
                        if shortBookName == bookNameOrAbbreviation: # they entered the full bookname -- we didn't really expect this punctuation
                            if char in self.punctuationDict['bookChapterSeparator']: # ok, they are the same character
                                status = 2 # Just accept this as the BCS and go get the chapter number
                            else:
                                if wantErrorMessages: logging.warning( _("Didn't expect '{}' punctuationAfterBookAbbreviation when the full book name was given at position {} in '{}'").format(self.punctuationDict['punctuationAfterBookAbbreviation'],nnn,referenceString) )
                                haveWarnings = True
                else:
                    #print( "Char is '{}', Temp is '{}'".format(char,temp) )
                    if char in self.punctuationDict['chapterVerseSeparator'] and temp and temp.isdigit(): # Assume it's a follow on chapter number
                        C = temp
                        status = 3 # Now get the verse number
                    elif char in self.punctuationDict['bookChapterSeparator']: # but this is often a space which also occurs in things like 1 Thess
                        BBB = self.__BibleOrganizationalSystem.getBBB( temp )
                        if BBB is not None: # Must have found a bookname
                            bookNameOrAbbreviation = temp
                            C, V, S = '', '', ''
                            spaceCount = 1 if char==' ' else 0
                            status = 2 # Start getting the chapter number
                        else: # Not a valid bookname
                            if char != ' ':
                                if wantErrorMessages: logging.error( _("Invalid '{}' bookname at position {} in Bible reference '{}'").format( bookNameOrAbbreviation, nnn, referenceString ) )
                                haveErrors = True
                    else:
                        if wantErrorMessages: logging.error( _("Unexpected '{}' character when getting book name at position {} in Bible reference '{}'").format( char, nnn, referenceString ) )
                        haveErrors = True
                continue
            if status == 5: # Get either book or chapter or verse range
                if char == ' ' and not X:
                    if wantErrorMessages: logging.warning( _("Extra space(s) after range bridge at position {} in Bible reference '{}'").format( nnn, referenceString ) )
                    haveWarnings = True
                elif char.isalnum():
                    X += char
                elif X and char in self.punctuationDict['punctuationAfterBookAbbreviation']:
                    BBB = self.__BibleOrganizationalSystem.getBBB( X )
                    if BBB is not None: # Must have found a bookname
                        bookNameOrAbbreviation = X
                        shortBookName = self.__BibleOrganizationalSystem.getShortBookName( BBB )
                        if shortBookName == bookNameOrAbbreviation: # they entered the full bookname -- we didn't really expect this punctuation
                            if char in self.punctuationDict['bookChapterSeparator']: # ok, they are the same character
                                pass
                            else:
                                if wantErrorMessages: logging.warning( _("Didn't expect '{}' punctuationAfterBookAbbreviation when the full book name was given at position {} in '{}'").format(self.punctuationDict['punctuationAfterBookAbbreviation'],nnn,referenceString) )
                                haveWarnings = True
                        C, V, S = '', '', ''
                        spaceCount = 1 if char==' ' else 0
                        status = 7 # Start getting the chapter range
                    else: # Not a valid bookname
                        if char != ' ':
                            if wantErrorMessages: logging.error( _("Invalid '{}' bookname in Bible reference '{}'").format( X, referenceString ) )
                            haveErrors = True
                elif X and char in self.punctuationDict['bookChapterSeparator']: # but this is often a space which also occurs in things like 1 Thess
                    BBB = self.__BibleOrganizationalSystem.getBBB( X )
                    if BBB is not None: # Must have found a bookname
                        bookNameOrAbbreviation = X
                        shortBookName = self.__BibleOrganizationalSystem.getShortBookName( BBB )
                        if shortBookName != bookNameOrAbbreviation and self.punctuationDict['punctuationAfterBookAbbreviation']: # they didn't enter the full bookname -- we expect some punctuation
                            if wantErrorMessages: logging.warning( _("Expected '{}' punctuationAfterBookAbbreviation when the abbreviated book name was given at position {} in '{}'").format(self.punctuationDict['punctuationAfterBookAbbreviation'],nnn,referenceString) )
                            haveWarnings = True
                        C, V, S = '', '', ''
                        spaceCount = 1 if char==' ' else 0
                        status = 7 # Start getting the chapter range
                    else: # Not a valid bookname
                        if char != ' ':
                            if wantErrorMessages: logging.error( _("Invalid '{}' bookname in Bible reference '{}'").format( X, referenceString ) )
                            haveErrors = True
                elif X and char in self.punctuationDict['chapterVerseSeparator']: # This must have been a chapter range
                    C = X
                    status, V, S = 8, '', ''
                elif X and char in self.punctuationDict['verseSeparator']: # This must have been a verse range
                    V = X
                    saveReferenceRange( startReferenceTuple, BBB, C, V, S, self.referenceList )
                    status, V, S = 3, '', '' # Go get a verse number
                elif X and (char in self.punctuationDict['chapterSeparator'] or char in self.punctuationDict['bookSeparator']): # This must have been a verse range
                    V = X
                    saveReferenceRange( startReferenceTuple, BBB, C, V, S, self.referenceList )
                    V, S = '', ''
                    if self.punctuationDict['chapterSeparator'] == self.punctuationDict['bookSeparator']:
                        temp, spaceCount = '', 0
                        status = 4 # We don't know what to expect next
                    elif char in self.punctuationDict['chapterSeparator']:
                        status,C = 1, ''
                    elif char in self.punctuationDict['bookSeparator']:
                        bookNameOrAbbreviation, BBB, C = '', None, ''
                        status = 0
                    else: assert( "Should never happen" == 123 )
                else:
                    if wantErrorMessages: logging.error( _("Unexpected '{}' character when getting second chapter/verse number at position {} in Bible reference '{}'").format( char, nnn, referenceString ) )
                    haveErrors = True
                continue
            if status == 7: # Get chapter range
                if char==' ' and not C:
                    if self.punctuationDict['spaceAllowedAfterBCS']=='N' or spaceCount>1:
                        if wantErrorMessages: logging.warning( _("Extra space(s) after bridge character at position {} in Bible reference '{}'").format( nnn, referenceString ) )
                        haveWarnings = True
                    spaceCount += 1
                elif char.isdigit():
                    if self.punctuationDict['spaceAllowedAfterBCS']=='Y' and spaceCount<1:
                        if wantErrorMessages: logging.warning( _("Missing space after bridge character at position {} in Bible reference '{}'").format( nnn, referenceString ) )
                        haveWarnings = True
                    C += char
                elif C and char in self.punctuationDict['chapterVerseSeparator']:
                    status = 8 # Start getting the verse number
                elif C and self.__BibleOrganizationalSystem.isSingleChapterBook(BBB) and char in self.punctuationDict['verseSeparator']:
                    V = C
                    C = '1'
                    saveReferenceRange( startReferenceTuple, BBB, C, V, S, self.referenceList )
                    status, V, S = 8, '', ''
                elif C and self.__BibleOrganizationalSystem.isSingleChapterBook(BBB) and char in self.punctuationDict['bookSeparator']:
                    V = C
                    C = '1'
                    saveReferenceRange( startReferenceTuple, BBB, C, V, S, self.referenceList )
                    status, BBB, C, V, S = 0, None, '', '', ''
                elif C and (char in self.punctuationDict['chapterSeparator'] or char in self.punctuationDict['bookSeparator']):
                    saveReferenceRange( startReferenceTuple, BBB, C, V, S, self.referenceList )
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
                    if wantErrorMessages: logging.error( _("Unexpected '{}' character when getting second chapter number at position {} in Bible reference '{}'").format( char, nnn, referenceString ) )
                    haveErrors = True
                continue
            if status == 8: # Get verse range
                if char == ' ' and not V:
                    if wantErrorMessages: logging.warning( _("Extra space(s) after chapter in range at position {} in {} Bible reference '{}'").format( nnn, BBB, referenceString ) )
                    haveWarnings = True
                elif char.isdigit():
                    V += char
                elif char in self.punctuationDict['allowedVerseSuffixes']: # Could be like verse 5a
                    S += char
                elif V and char in self.punctuationDict['verseSeparator']:
                    saveReferenceRange( startReferenceTuple, BBB, C, V, S, self.referenceList )
                    status, V, S = 3, '', '' # Go get a verse number
                elif V and (char in self.punctuationDict['chapterSeparator'] or char in self.punctuationDict['bookSeparator']):
                    saveReferenceRange( startReferenceTuple, BBB, C, V, S, self.referenceList )
                    V, S = '', ''
                    if self.punctuationDict['chapterSeparator'] == self.punctuationDict['bookSeparator']:
                        temp, spaceCount = '', 0
                        status = 4 # We don't know what to expect next
                    elif char in self.punctuationDict['chapterSeparator']:
                        status, C = 1, ''
                    elif char in self.punctuationDict['bookSeparator']:
                        bookNameOrAbbreviation, BBB, C = '', None, ''
                        status = 0
                else:
                    if wantErrorMessages: logging.error( _("Unexpected '{}' character when getting verse number for range at position {} in {} {} Bible reference '{}'").format( char, nnn, BBB, C, referenceString ) )
                    haveErrors = True
                    if V:
                        saveReference( BBB, C, V, S, self.referenceList )
                        V, S = '', ''
                continue
        if status==2 and C: # Getting chapter number
            if self.__BibleOrganizationalSystem.isSingleChapterBook( BBB ): # Have a single chapter book and what we were given is presumably the verse number
                V = C
                C = '1'
                status = 4
            else: # it must be specifying an entire chapter (like Gen. 3)
                saveReference( BBB, C, V, S, self.referenceList )
                status = 9
        elif status==3: # Got a C but still getting the V hopefully
            if V: status = 4
        elif status==4: # Must have ended with a separator character
            if wantErrorMessages: logging.warning( _("Bible reference '{}' ended with a separator character").format( referenceString ) )
            haveWarnings = True
            status = 9;
        elif status==5 and X: # Getting C or V range
            V = X
            saveReferenceRange( startReferenceTuple, BBB, C, V, S, self.referenceList )
            status = 9
        #elif status==6 and C: # Getting book range
        #    saveReferenceRange( startReferenceTuple, BBB, C, V, S, self.referenceList )
        #    status = 9
        elif status==7 and C: # Getting C range
            saveReferenceRange( startReferenceTuple, BBB, C, V, S, self.referenceList )
            status = 9
        elif status==8 and V: # Getting V range
            saveReferenceRange( startReferenceTuple, BBB, C, V, S, self.referenceList )
            status = 9
        if status==4 and not haveErrors:
            saveReference( BBB, C, V, S, self.referenceList )
            status = 9

        #print( "Final status: {} -- got '{}'from '{}'\n".format(statusList[status],self.referenceList,referenceString) )
        #print( "here", len(totalVerseList), totalVerseList )

        singleVerseSet = set( totalVerseList )
        if len(singleVerseSet) < len(totalVerseList):
            #print( "Final status: {} -- got '{}'from '{}'\n".format(statusList[status],self.referenceList,referenceString) )
            print( "totalVerseList is {}, singleVerseSet is {}".format(totalVerseList, singleVerseSet) )
            for entry in singleVerseSet:
                if totalVerseList.count(entry) > 1:
                    print( entry )
                    if wantErrorMessages: logging.warning( _("Have duplicate or overlapping range at {} in Bible references '{}'").format( self.makeReferenceString(entry), referenceString ) )
            haveWarnings = True
        return status==9 and not haveErrors, haveWarnings, self.referenceList
    # end of parseReferenceString

    def getReferenceList( self, expanded=False, wantErrorMessages=False ):
        """ Returns the internal list of Bible references.

            If expanded, fills out any ranges according to the specified versification system. """
        if expanded:
            expandedList = []
            for refTuple in self.referenceList:
                if len(refTuple) == 2: # it's a range
                    startRefTuple, endRefTuple = refTuple
                    expandedRange = self.__BibleOrganizationalSystem.expandCVRange( startRefTuple, endRefTuple, bookOrderSystem=self.__BibleOrganizationalSystem, wantErrorMessages=wantErrorMessages )
                    if expandedRange is not None: expandedList.extend( expandedRange )
                else: expandedList.append( refTuple )
            return expandedList
        else:
            return self.referenceList
    # end of getReferenceList

    def getOSISRefList( self ):
        """ Converts our internal reference list to OSIS format.
                OSIS defines reference ranges
                    e.g., Gen.1.1-Gen.1.2 or Gen.1.1-Gen.2.3 (inclusive).

            We simply ignore the single lower-case letter verse suffixes. """
        assert( self.referenceList )

        result = ''
        lastBk, lastC, lastV = '', '', ''
        for refOrRefRange in self.referenceList:
            if result: result += self.punctuationDict['bookSeparator'] + ' ' # The separator between multiple references
            if len(refOrRefRange) == 2: # it must be a range (start and end tuples)
                (BBB1, C1, V1, S1), (BBB2, C2, V2, S2) = refOrRefRange
                Bk1 = self.__BibleBooksCodes.getOSISAbbreviation( BBB1 )
                Bk2 = self.__BibleBooksCodes.getOSISAbbreviation( BBB2 )
                if V1 and V2: result += "{}.{}.{}-{}.{}.{}".format(Bk1,C1,V1,Bk2,C2,V2)
                elif not V1 and not V2: result += "{}.{}-{}.{}".format(Bk1,C1,Bk2,C2)
                elif V2: result += "{}.{}.1-{}.{}.{}".format(Bk1,C1,Bk2,C2,V2)
                else: giveUphere
                lastBk, lastC, lastV = Bk2, C2, V2
            else: # It must be a single reference
                BBB, C, V, S = refOrRefRange
                Bk = self.__BibleBooksCodes.getOSISAbbreviation( BBB )
                if V: result += "{}.{}.{}".format(Bk,C,V)
                else: result += "{}.{}".format(Bk,C)
                lastBk, lastC, lastV = Bk, C, V
        return result
    # end of getOSISRefList

    def parseToOSIS( self, referenceString, wantErrorMessages=False ):
        """ Just combines the two above routines.
                Parses a vernacular reference string and returns an OSIS reference string
                    or None if a valid reference cannot be parsed. """
        successFlag, haveWarnings, refList = self.parseReferenceString( referenceString, wantErrorMessages )
        if successFlag: return self.getOSISRefList()
        #if wantErrorMessages: logging.error( "You should already have an error above for '{}'".format( referenceString ) ) # temp
    # end of parseToOSIS

    def containsReferenceTuple( self, refTuple, wantErrorMessages=False ):
        """ Returns True/False if the internal reference list contains the given reference tuple. """
        assert( refTuple and len(refTuple)==4 )
        if wantErrorMessages and not self.__BibleOrganizationalSystem.isValidBCVRef( refTuple, "{} {}:{}{}"%(refTuple[0],refTuple[1],refTuple[2],refTuple[3]), wantErrorMessages ):
            haveErrors = True

        # See if we can find this reference in our internal list
        for refTuple in self.referenceList:
            if len(refTuple) == 2: # it's a range
                startRefTuple, endRefTuple = refTuple
                expandedList = self.__BibleOrganizationalSystem.expandCVRange( startRefTuple, endRefTuple, bookOrderSystem=self.__BibleOrganizationalSystem, wantErrorMessages=wantErrorMessages )
                if refTuple in expandedList: return True
            elif refTuple == refTuple: return True
        return False
    # end of containsReferenceTuple

    def containsReference( self, BBB, C, V, S=None, wantErrorMessages=False ):
        """ Returns True/False if the internal reference list contains the given reference. """
        assert( BBB and len(BBB)==3 )
        assert( C and C.isdigit() )
        assert( V ) # May contain a list or range here

        # First find out what we were given
        if V.isdigit(): # it's simple
            myTuple = (BBB, C, V, S)
            if wantErrorMessages and not self.__BibleOrganizationalSystem.isValidBCVRef( myTuple, "{} {}:{}{}"%(BBB,C,V,S), wantErrorMessages ):
                haveErrors = True
            myList = [ myTuple, ]
        else: # Must have a list or range
            status, myList = 0, []
            myV = ''
            for char in V+self.punctuationDict['verseSeparator'][0]: # Adds something like a comma at the end to force collecting the final verse digit(s)
                if status == 0: # Getting a verse number
                    if char.isdigit(): myV += char
                    elif myV and char in self.punctuationDict['verseSeparator']: # Just got a verse number
                        myTuple = (BBB, C, myV, S)
                        if wantErrorMessages and not self.__BibleOrganizationalSystem.isValidBCVRef( myTuple, "{} {}:{}{}"%(BBB,C,myV,S), wantErrorMessages ):
                            haveErrors = True
                        myList.append( myTuple )
                        myV = ''
                    elif myV and char in self.punctuationDict['verseBridgeCharacter']: # Just got the start verse of a range
                        startTuple = (BBB, C, myV, S)
                        if wantErrorMessages and not self.__BibleOrganizationalSystem.isValidBCVRef( startTuple, "{} {}:{}{}"%(BBB,C,myV,S), wantErrorMessages ):
                            haveErrors = True
                        status, myV = 1, ''
                    elif wantErrorMessages: logging.error( _("Invalid '{}' verse list/range given with {} {}:{}{}").format( V, BBB, C, V, S ) )
                elif status == 1: # Getting the end of a verse range
                    assert( startTuple )            
                    if char.isdigit(): myV += char
                    elif myV and char in self.punctuationDict['verseSeparator']: # Just got the end of the range
                        endTuple = (BBB, C, myV, S)
                        if wantErrorMessages and not self.__BibleOrganizationalSystem.isValidBCVRef( endTuple, "{} {}:{}{}"%(BBB,C,myV,S), wantErrorMessages ):
                            haveErrors = True
                        verseList = self.__BibleOrganizationalSystem.expandCVRange( startTuple, endTuple, bookOrderSystem=self.__BibleOrganizationalSystem, wantErrorMessages=wantErrorMessages )
                        if verseList is not None: myList.extend( verseList )
                        status, myV = 0, ''
            if wantErrorMessages and (status>0 or myV): logging.error( _("Invalid '{}' verse list/range given with {} {}:{}{}").format( V, BBB, C, V, S ) )
            #print( "myList", myList )

        # Now see if we can find any of these references in our internal list
        for myRefTuple in myList:
            for refTuple in self.referenceList:
                if len(refTuple) == 2: # it's a range
                    startRefTuple, endRefTuple = refTuple
                    expandedList = self.__BibleOrganizationalSystem.expandCVRange( startRefTuple, endRefTuple, bookOrderSystem=self.__BibleOrganizationalSystem, wantErrorMessages=wantErrorMessages )
                    if myRefTuple in expandedList: return True
                    elif S is None:
                        for refTuple in expandedList:
                            if myRefTuple[0]==refTuple[0] and myRefTuple[1]==refTuple[1] and myRefTuple[2]==refTuple[2]: return True # Just compare BBB,C,V (not S)
                elif myRefTuple == refTuple: return True
                elif S is None and myRefTuple[0]==refTuple[0] and myRefTuple[1]==refTuple[1] and myRefTuple[2]==refTuple[2]: return True # Just compare BBB,C,V (not S)
        return False
    # end of containsReference
# end of class BibleReferenceList


def demo():
    """Demonstrate reading and processing some Bible name databases.
    """
    # Handle command line parameters
    from optparse import OptionParser
    parser = OptionParser( version="v{}".format( versionString ) )
    #parser.add_option("-e", "--export", action="store_true", dest="export", default=False, help="export the XML file to .py and .h tables suitable for directly including into other programs")
    Globals.addStandardOptionsAndProcess( parser )

    if Globals.verbosityLevel > 1: print( "{} V{}".format( progName, versionString ) )

    BBC = BibleBooksCodes().loadData()
    BOS = BibleOrganizationalSystem( "RSV" )
    printProcessingMessages = True
    wantErrorMessages = True

    if 0:
        print()
        BSR = BibleSingleReference( BBC, BOS )
        print( BSR ) # Just print a summary
        print( "\nSingle Reference (good)" )
        for ref in ("Mat 7:3","Mat.7:3","Mat. 7:3","Mt. 7:3","Mt.7:3","Jde 7","Jde. 7","Jde 1:7","Jde. 1:7","Job 8:4","Job. 8:4","Job8:4","Job  8:4","Lev. 8:4b"):
            if printProcessingMessages: print( "Processing '{}' reference string...".format( ref ) )
            print( "  From '{}' BSR got {}".format(ref, BSR.parseReferenceString(ref,wantErrorMessages)) )
        print( "\nSingle Reference (bad)" )
        for ref in ("Mat 0:3","Mat.7:0","Mat. 77:3","Mt. 7:93","M 7:3","Mit 7:3","Mt. 7:3","Mit. 7:3","Mat. 7:3ab","Mat, 7:3","Mat. 7:3xyz5"):
            if printProcessingMessages: print( "Processing '{}' reference string...".format( ref ) )
            print( "  From '{}' BSR got {}".format(ref, BSR.parseReferenceString(ref,wantErrorMessages)) )

    if 0:
        print()
        BSRs = BibleSingleReferences( BBC, BOS )
        print( BSRs ) # Just print a summary
        print( "\nSingle References (good)" )
        for ref in ("Mat 7:3","Mat.7:3","Mat. 7:3","Mt. 7:3","Mt.7:3","Jde 7","Jde. 7","Jde 1:7","Jde. 1:7","Job 8:4","Job. 8:4","Job8:4","Job  8:4","Lev. 8:4b"):
            if printProcessingMessages: print( "Processing '{}' reference string...".format( ref ) )
            print( "  From '{}' BSRs got {}".format(ref, BSRs.parseReferenceString(ref,wantErrorMessages)) )
        for ref in ("Mat. 7:3,7","Mat. 7:3; 4:7","Mat. 7:3,7; 4:7","Mat. 7:3,7; 4:7,9,11","Mat. 7:3; Heb. 2:2; Rev. 1:1","Mat. 7:3,7; Heb 2:2,9; Rev. 1:1","Mat. 7:3,7; 8:17; Heb 2:2,9; 4:4,7; Rev. 1:1; 1:1","Mrk. 7:3a,7b,8"):
            if printProcessingMessages: print( "Processing '{}' reference string...".format( ref ) )
            print( "  From '{}' BSRs got {}".format(ref, BSRs.parseReferenceString(ref,wantErrorMessages)) )
        print( "\nSingle References (bad)" )
        for ref in ("Mat 0:3","Mat.7:0","Mat. 77:3","Mt. 7:93","M 7:3","Mit 7:3","Mt. 7:3","Mit. 7:3","Mat. 7:3ab","Mat, 7:3","Mat. 7:3xyz5"):
            if printProcessingMessages: print( "Processing '{}' reference string...".format( ref ) )
            print( "  From '{}' BSRs got {}".format(ref, BSRs.parseReferenceString(ref,wantErrorMessages)) )

    if 1:
        print()
        BRL = BibleReferenceList( BBC, BOS )
        print( BRL ) # Just print a summary
        print( BRL.makeReferenceString(("MAT",'7','3')), BRL.makeReferenceString(("PHM",'1','3')), BRL.makeReferenceString(("CO1",'2','1','a')), BRL.makeReferenceString(("CO2",'7')) )
        if 0:
            print( "\n\nSingle References for Ranges (good)" )
            for ref in ("Mat 7:3","Mat.7:3","Mat. 7:3","Mt. 7:3","Mt.7:3","Jde 7","Jde. 7","Jde 1:7","Jde. 1:7","Job 8:4","Job. 8:4","Job8:4","Job  8:4","Lev. 8:4b", \
                        "Mat. 7:3,7","Mat. 7:3; 4:7","Mat. 7:3,7; 4:7","Mat. 7:3,7; 4:7,9,11","Mat. 7:3; Heb. 2:2; Rev. 1:1","Mat. 7:3,7; Heb 2:2,9; Rev. 1:1","Mat. 7:3,7; 8:17; Heb 2:2,9; 4:4,7; Rev. 1:1; 1:1","Mrk. 7:3a,7b,8"):
                if printProcessingMessages: print( "Processing '{}' reference string...".format( ref ) )
                print( "  From '{}' BRL got {}".format(ref, BRL.parseReferenceString(ref,wantErrorMessages)) )
            print( "\nSingle References for Ranges (bad)" )
            for ref in ("Mat 0:3","Mat.7:0","Mat. 77:3","Mt. 7:93","M 7:3","Mit 7:3","Mt. 7:3","Mit. 7:3","Mat. 7:3ab","Mat, 7:3","Mat. 7:3xyz5"):
                if printProcessingMessages: print( "Processing '{}' reference string...".format( ref ) )
                print( "  From '{}' BSRs got {}".format(ref, BRL.parseReferenceString(ref,wantErrorMessages)) )
            print( "\n\nSingle Ranges (good)" )
            for ref in ("Mat 7:3-7","Mat.7:3-11","Mat. 7:13-8:2","Mt. 7:3,5-9","Mt.7:3-4,6-9","Jde 7-8","Jde. 1-3","Jde 1:7-8","Jud. 1:1-3,5,7-9","EXO.4:14,27c-30;  5:1,4,20; 6:13,20,23,25-27a; 7:1,2,6b-10a,10,12,19,20; 8:1,2,4,8,12,13,21;"):
                if printProcessingMessages: print( "Processing '{}' reference string...".format( ref ) )
                print( "  From '{}' BRL got {}".format(ref, BRL.parseReferenceString(ref,wantErrorMessages)) )
                print( "OSIS result is '{}'".format( BRL.getOSISRefList() ) )
            print( "\nSingle Ranges (bad)" )
            for ref in ("EXO.4:14-12; NUM.3:12-1:5; JOS.4:5-5","Mt. 7:7;"):
                if printProcessingMessages: print( "Processing '{}' reference string...".format( ref ) )
                print( "  From '{}' BRL got {}".format(ref, BRL.parseReferenceString(ref,wantErrorMessages)) )
            print( "\n\nNow some chapter Ranges (good)" )
            for ref in ("Dan. 5","Gen. 1-11","Act.4-7; Mat.5-7"):
                if printProcessingMessages: print( "Processing '{}' reference string...".format( ref ) )
                print( "  From '{}' BRL got {}".format(ref, BRL.parseReferenceString(ref,wantErrorMessages)) )
                #print( "OSIS result is '{}'".format( BRL.getOSISRefList() ) )
            print( "\nNow some chapter Ranges (bad)" )
            for ref in ("Tit. 1:2; 1:2-7","Jer. 95","Exo. 23-99","1 Cor.9-7; 1Tim.5-7:2"):
                if printProcessingMessages: print( "Processing '{}' reference string...".format( ref ) )
                print( "  From '{}' BRL got {}".format(ref, BRL.parseReferenceString(ref,wantErrorMessages)) )
            for ref in ("Jhn. 3:16", "Rev. 2:1-3" ):
                if printProcessingMessages: print( "Processing '{}' reference string...".format( ref ) )
                print( "  From '{}' BRL got OSIS '{}'".format(ref, BRL.parseToOSIS(ref,wantErrorMessages)) )
        if 0:
            for ref in ("Mat. 27:15a-Mrk. 2:4b", "1Sml. 16:1-1Kngs. 2:11", "Eze. 27:12-13,22", ):
                if printProcessingMessages: print( "\nProcessing '{}' reference string...".format( ref ) )
                print( "  From '{}' BRL got OSIS '{}'".format(ref, BRL.parseToOSIS(ref,wantErrorMessages)) )
                l1, l2 = BRL.getReferenceList(), BRL.getReferenceList( expanded=True )
                print( "List is: ", l1 )
                if l2!=l1: print( "Expanded:", l2 )
        if 1:
            for ref in ( \
                    #"Mt 3:2; 4:17;  9:35; 10:7; 11:12,13; 12:28; 13:11, 19, 44, 45, 47, 52; 18:23; 19:12; 20:1; 22:2; 24:14, 25:1, 14, 31; Mk 1:15; 4:11; 9:1; 10:15; 11:10; 15:43; Lk 1:32, 33; 3:1,2; 4:43; 8:1, 10; 9:1,2, 11, 27, 60, 62; 10:9, 11; 16:16; 17:19, 20, 22; 18:17, 29; 19:11, 15; 21:31; 22:18, 28-29; 23:43, 50-52; Jn 18:36; Ac 1:2,3,30; 7:18; 8:12; 13:22; 19:8; 20:25; 28:23, 31; Rm 15:12; Col 4:10,11; 2 Ti 4:1; Rev 11:17; 12:10", \
                    "Mt. 3:2; 4:17; 9:35; 10:7; 11:12,13; 12:28; 13:11,19,44,45,47,52; 18:23; 19:12; 20:1; 22:2; 24:14; 25:1,14,31; Mk. 1:15; 4:11; 9:1; 10:15; 11:10; 15:43; Lk. 1:32,33; 3:1,2; 4:43; 8:1,10; 9:1,2,11,27,60,62; 10:9,11; 16:16; 17:19,20,22; 18:17,29; 19:11,15; 21:31; 22:18,28-29; 23:43,50-52; Jn 18:36; Ac. 1:2,3,30; 7:18; 8:12; 13:22; 19:8; 20:25; 28:23,31; Rm. 15:12; Col. 4:10,11; 2 Ti. 4:1; Rev. 11:17; 12:10", \
                    #"Mt 5:3, 10, 19, 20; 11:11; 13:24, 31, 33 41; 18:1, 3, 4; 19:14, 23, 24; 21:31, 43; 23:13; Mk 4:30; 10:14, 23, 24, 25; 12:34; Lk 6:20; 7:28; 12:32; 13:18,20, 18:16, 24,25; 19:14, 27; John 3:3, 3:5; Ac 1:6; 7:10; Ac 1 Co 6:9, 10; 15:24-25, 50; Gal 5:21; Eph 5:5; Col 1:12", \
                    "Mt. 5:3,10,19,20; 11:11; 13:24,31,33,41; 18:1,3,4; 19:14,23,24; 21:31,43; 23:13; Mk. 4:30; 10:14,23,24,25; 12:34; Lk 6:20; 7:28; 12:32; 13:18,20; 18:16,24,25; 19:14,27; John 3:3; 3:5; Ac. 1:6; 7:10; 1 Co. 6:9,10; 15:24-25,50; Gal. 5:21; Eph. 5:5; Col. 1:12", \
                    #"Mt 7:21; 8:11; 11:12,13; 13:43; 16:19; 24:7; 25:34; 26:29; Mk 6:23; 9:47; 10:37; 13:8; 14:25; Lk 13:21, 24-25; 13:28, 29; 14:15; 17:21; 21:10; 22:16, 30; Ac 1:6; 7:10; 14:22; 15:16,50; Col 1:12; 1 Th 2:11,12; 2 Th 1:5; 4:18; Heb 12:28; Jas 2:5; 2 Pe 1:11; Rev 3:7; 16:10", \
                    "Mt. 7:21; 8:11; 11:12,13; 13:43; 16:19; 24:7; 25:34; 26:29; Mk. 6:23; 9:47; 10:37; 13:8; 14:25; Lk 13:21,24-25; 13:28,29; 14:15; 17:21; 21:10; 22:16,30; Ac 1:6; 7:10; 14:22; 15:16,50; Col. 1:12; 1 Th. 2:11,12; 2 Th. 1:5; 4:18; Heb. 12:28; Jas. 2:5; 2 Pe. 1:11; Rev. 3:7; 16:10", ):
                if printProcessingMessages: print( "\nProcessing '{}' reference string...".format( ref ) )
                print( "From '{}'\n  BRL got OSIS '{}'".format(ref, BRL.parseToOSIS(ref,wantErrorMessages)) )
                l1, l2 = BRL.getReferenceList(), BRL.getReferenceList( expanded=True )
                print( "List is: ", l1 )
                #if l2!=l1: print( "Expanded:", l2 )

if __name__ == '__main__':
    demo()
# end of BibleReferences.py
