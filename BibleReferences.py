#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# BibleReferences.py
#
# Module for handling Bible references including ranges
#
# Copyright (C) 2010 Robert Hunt
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
"""


import os, logging
import BibleBookNames, USFMBibleBookCodes, BibleChaptersVerses


builtinSystems = {
# For BooknameCase
#   U = must be UPPER, L = lower, M = Mixed, E = either allowed
# For SpaceAllowedAfterBCS:
#   Y = yes, N = no, E = either (optional)
    'EnglishSystem': {
        'BooknameCase': ( 'M', 'E' ), # Mixed case preferred
        'BookChapterSeparator': ( '.', ' ' ), # period preferred
        'SpaceAllowedAfterBCS': 'E', # after non-blank BookChapterSeparator
        'ChapterBridge': ( '–', '-' ), # en-dash preferred
        'ChapterVerseSeparator': ':',
        'VerseSeparator': ',',
        'VerseBridge': ( '–', '-' ), # en-dash preferred
        'ChapterSeparator': ';',
        'BookSeparator': ';',
        },
    'EnglishSystemWithHyphen': {
        'BooknameCase': ( 'M', 'E' ), # Mixed case preferred
        'BookChapterSeparator': '.',
        'SpaceAllowedAfterBCS': 'Y', # after non-blank BookChapterSeparator
        'ChapterBridge': '-', # hyphen only
        'ChapterVerseSeparator': ':',
        'VerseSeparator': ',',
        'VerseBridge': '-', # hyphen only
        'ChapterSeparator': ';',
        'BookSeparator': ';',
        },
    'EnglishSystemWithEnDash': {
        'BooknameCase': ( 'M', 'E' ), # Mixed case preferred
        'BookChapterSeparator': '.',
        'SpaceAllowedAfterBCS': 'Y', # after non-blank BookChapterSeparator
        'ChapterBridge': '–', # en-dash
        'ChapterVerseSeparator': ':',
        'VerseSeparator': ',',
        'VerseBridge': '–', # en-dash
        'ChapterSeparator': ';',
        'BookSeparator': ';',
        },
    'GermanSystem': {
        'BooknameCase': ( 'M', 'E' ), # Mixed case preferred
        'BookChapterSeparator': ' ',
        'SpaceAllowedAfterBCS': 'E', # after non-blank BookChapterSeparator
        'ChapterBridge': ( '-', '–' ), # en-dash
        'ChapterVerseSeparator': ',',
        'VerseSeparator': ' ',
        'VerseBridge': ( '-', '–' ), # en-dash
        'ChapterSeparator': ';',
        'BookSeparator': ';',
        },
    'FrenchSystem': {
        'BooknameCase': ( 'M', 'E' ), # Mixed case preferred
        'BookChapterSeparator': ' ',
        'SpaceAllowedAfterBCS': 'E', # after non-blank BookChapterSeparator
        'ChapterBridge': ( '-', '–' ), # en-dash
        'ChapterVerseSeparator': '.',
        'VerseSeparator': ',',
        'VerseBridge': ( '-', '–' ), # en-dash
        'ChapterSeparator': ';',
        'BookSeparator': ';',
        },
    }


class BibleSingleReference:
    """
    Class for creating and manipulating single Bible reference objects (no range allowed).
    """

    def __init__( self, systemName, BBNObject, BCVObject ):
        assert( systemName )
        assert( BBNObject )
        assert( BCVObject )
        self.BibleBookNames = BBNObject
        self.BibleChaptersVerses = BCVObject
        self.load( systemName )
    # end of __init__

    def __str__( self ):
        """
        This method returns the string representation of a Bible object.
        
        @return: the name of a Bible object formatted as a string
        @rtype: string
        """
        result = ""
        if self.systemName: result += ('\n' if result else '') + self.systemName
        #if self.versionName and self.versionName!=self.name: result += ('\n' if result else '') + self.versionName
        return result
    # end of __str__

    def load( self, systemName ):
        self.systemName = systemName
        if systemName in builtinSystems:
            self.characters = builtinSystems[systemName]
        else:
            self.systemName = None
            self.characters = None
            logging.error( "Sorry, this program doesn't handle the '%s' language system for Bible references yet." % systemName )
    # end of load

    def parseWithErrorMsgs( self, referenceString ):
        """
        Returns a tuple with True/False result, haveWarnings, BBB, C, V
        """
        assert( self.characters )
        assert( referenceString )
        haveWarnings, haveErrors = False, False
        strippedReferenceString = referenceString.strip()
        if strippedReferenceString != referenceString:
            logging.warning( "Reference string '%s' contains surrounding space(s)" % referenceString )
            haveWarnings = True
        status = 0  # 0:getting bookname, 1:getting chapter, 2:getting verse, 3:done both
        bookName, BBB, C, V = '', '', '', ''
        for char in strippedReferenceString:
            if status == 0: # Getting bookname
                if char.isalnum():
                    bookName += char
                elif char in self.characters['BookChapterSeparator']:
                    BBB = self.BibleBookNames.getBBB( bookName )
                    if BBB is None:
                        logging.error( "Invalid '%s' bookname in Bible reference '%s'" % ( bookName, referenceString ) )
                        haveErrors = True
                    spaceCount = 1 if char==' ' else 0
                    status = 1
                else:
                    logging.error( "Unexpected '%s' character in Bible reference '%s' when getting book name" % ( char, referenceString ) )
                    haveErrors = True
            elif status == 1: # Getting chapter number (or could be the verse number of a one chapter book)
                if char==' ' and not C:
                    if self.characters['SpaceAllowedAfterBCS']=='N' or spaceCount>1:
                        logging.warning( "Extra space(s) after bookname in Bible reference '%s'" % referenceString )
                        haveWarnings = True
                    spaceCount += 1
                elif char.isdigit() or char in ('a','b','c','d','e'): # Could be like verse 5a
                    if self.characters['SpaceAllowedAfterBCS']=='Y' and spaceCount<1:
                        logging.warning( "Missing space after bookname in Bible reference '%s'" % referenceString )
                        haveWarnings = True
                    C += char
                elif C and char in self.characters['ChapterVerseSeparator']:
                    status = 2
                else:
                    logging.error( "Unexpected '%s' character when getting chapter number in %s Bible reference '%s'" % ( char, BBB, referenceString ) )
                    haveErrors = True
            elif status == 2: # Getting verse number
                if char == ' ' and not V:
                    logging.warning( "Extra space(s) after chapter in %s Bible reference '%s'" % ( BBB, referenceString ) )
                    haveWarnings = True
                elif char.isdigit() or char in ('a','b','c','d','e'): # Could be like verse 5a
                    V += char
                else:
                    logging.error( "Unexpected '%s' character when getting verse number in %s %s Bible reference '%s'" % ( char, BBB, C, referenceString ) )
                    haveErrors = True
                    if V: status = 3
        if status==2: # Got a C but still getting the V hopefully
            if V: status = 3
        if status==1 and C and BBB in USFMBibleBookCodes.OneChapterBookListUC: # Have a single chapter book and what we were given is presumably the verse number
                V = C
                C = '1'
                status = 4
        if status>=3 and not haveErrors:
            if self.BibleChaptersVerses.CVValidWithErrorMsgs( BBB, C, V, referenceString ):
                status = 9
        return status==9 and not haveErrors, haveWarnings, BBB, C, V
# end of class BibleSingleReference


class BibleSingleReferences:
    """
    Class for creating and manipulating a list of multiple Bible reference objects (no ranges allowed).
    """

    def __init__( self, systemName, BBNObject, BCVObject ):
        assert( systemName )
        assert( BBNObject )
        assert( BCVObject )
        self.BibleBookNames = BBNObject
        self.BibleChaptersVerses = BCVObject
        self.load( systemName )
    # end of __init__

    def __str__( self ):
        """
        This method returns the string representation of a Bible object.
        
        @return: the name of a Bible object formatted as a string
        @rtype: string
        """
        result = ""
        if self.systemName: result += ('\n' if result else '') + self.systemName
        #if self.versionName and self.versionName!=self.name: result += ('\n' if result else '') + self.versionName
        return result
    # end of __str__

    def load( self, systemName ):
        self.systemName = systemName
        if systemName in builtinSystems:
            self.characters = builtinSystems[systemName]
        else:
            self.systemName = None
            self.characters = None
            logging.error( "Sorry, this program doesn't handle the '%s' language system for Bible references yet." % systemName )
    # end of load

    def parseWithErrorMsgs( self, referenceString ):
        """
        Returns a tuple with True/False result, haveWarnings, list of (BBB, C, V) tuples
        """
        #print( "Processing '%s'" % referenceString )
        assert( self.characters )
        assert( referenceString )
        haveWarnings, haveErrors = False, False
        strippedReferenceString = referenceString.strip()
        if strippedReferenceString != referenceString:
            logging.warning( "Reference string '%s' contains surrounding space(s)" % referenceString )
            haveWarnings = True
        status = 0  # 0:getting bookname, 1:getting chapter, 2:getting verse, 3:done both, 4:expecting either another chapter number or a book name
        bookName, BBB, C, V, refList = '', '', '', '', []
        for char in strippedReferenceString:
            if status == 0: # Getting bookname
                if char.isalnum():
                    bookName += char
                elif char in self.characters['BookChapterSeparator']:
                    BBB = self.BibleBookNames.getBBB( bookName )
                    if BBB is None:
                        logging.error( "Invalid '%s' bookname in Bible reference '%s'" % ( bookName, referenceString ) )
                        haveErrors = True
                    else:
                        C, V = '', ''
                    spaceCount = 1 if char==' ' else 0
                    status = 1
                else:
                    logging.error( "Unexpected '%s' character in Bible reference '%s' when getting book name" % ( char, referenceString ) )
                    haveErrors = True
            elif status == 1: # Getting chapter number (or could be the verse number of a one chapter book)
                if char==' ' and not C:
                    if self.characters['SpaceAllowedAfterBCS']=='N' or spaceCount>1:
                        logging.warning( "Extra space(s) after bookname in Bible reference '%s'" % referenceString )
                        haveWarnings = True
                    spaceCount += 1
                elif char.isdigit() or char in ('a','b','c','d','e'): # Could be like verse 5a
                    if self.characters['SpaceAllowedAfterBCS']=='Y' and spaceCount<1:
                        logging.warning( "Missing space after bookname in Bible reference '%s'" % referenceString )
                        haveWarnings = True
                    C += char
                elif C and char in self.characters['ChapterVerseSeparator']:
                    status = 2
                elif C and BBB in USFMBibleBookCodes.OneChapterBookListUC and char in self.characters['VerseSeparator']:
                    V = C
                    C = '1'
                    refList.append( (BBB, C, V) )
                    V = ''
                    status = 2
                elif C and BBB in USFMBibleBookCodes.OneChapterBookListUC and char in self.characters['BookSeparator']:
                    V = C
                    C = '1'
                    refList.append( (BBB, C, V) )
                    BBB, C, V = '', '', ''
                    status = 0
                else:
                    logging.error( "Unexpected '%s' character when getting chapter number in %s Bible reference '%s'" % ( char, BBB, referenceString ) )
                    haveErrors = True
            elif status == 2: # Getting verse number
                if char == ' ' and not V:
                    logging.warning( "Extra space(s) after chapter in %s Bible reference '%s'" % ( BBB, referenceString ) )
                    haveWarnings = True
                elif char.isdigit() or char in ('a','b','c','d','e'): # Could be like verse 5a
                    V += char
                elif V and char in self.characters['VerseSeparator']:
                    refList.append( (BBB, C, V) )
                    V = ''
                elif V and (char in self.characters['ChapterSeparator'] or char in self.characters['BookSeparator']):
                    refList.append( (BBB, C, V) )
                    V = ''
                    if self.characters['ChapterSeparator'] == self.characters['BookSeparator']:
                        temp, spaceCount = '', 0
                        status = 4 # We don't know what to expect next
                    elif char in self.characters['ChapterSeparator']:
                        C = ''
                        status = 1
                    elif char in self.characters['BookSeparator']:
                        bookName, BBB, C = '', '', ''
                        status = 0
                else:
                    logging.error( "Unexpected '%s' character when getting verse number in %s %s Bible reference '%s'" % ( char, BBB, C, referenceString ) )
                    haveErrors = True
                    if V:
                        refList.append( (BBB, C, V) )
                        V = ''
            elif status == 4: # Getting the next chapter number or book name (not sure which)
                if char == ' ' and not temp:
                    if spaceCount:
                        logging.warning( "Extra space(s) after chapter or book separator in %s Bible reference '%s'" % ( BBB, referenceString ) )
                        haveWarnings = True
                    spaceCount += 1
                elif char.isalnum():
                    temp += char
                else:
                    #print( "Got '%s'" % temp )
                    if char in self.characters['ChapterVerseSeparator'] and temp and temp.isdigit(): # Assume it's a follow on chapter number
                        C = temp
                        status = 2
                    elif char in self.characters['BookChapterSeparator']:
                        bookName = temp
                        BBB = self.BibleBookNames.getBBB( bookName )
                        if BBB is None:
                            logging.error( "Invalid '%s' bookname in Bible reference '%s'" % ( bookName, referenceString ) )
                            haveErrors = True
                        C, V = '', ''
                        spaceCount = 1 if char==' ' else 0
                        status = 1
                    else:
                        logging.error( "Unexpected '%s' character in Bible reference '%s' when getting book name" % ( char, referenceString ) )
                        haveErrors = True
        if status==2: # Got a C but still getting the V hopefully
            if V:
                status = 3
        if status==1 and C and BBB in USFMBibleBookCodes.OneChapterBookListUC: # Have a single chapter book and what we were given is presumably the verse number
                V = C
                C = '1'
                status = 8
        if status>=3 and not haveErrors:
            refList.append( (BBB, C, V) )
            status = 9
        for ref in refList:
            #print( ref )
            BBB, C, V = ref
            if not self.BibleChaptersVerses.CVValidWithErrorMsgs( BBB, C, V, referenceString ):
                haveErrors = True
        return status==9 and not haveErrors, haveWarnings, refList
# end of class BibleSingleReferences


class BibleRangeReferences:
    """
    Class for creating and manipulating a list of multiple Bible reference objects including optional ranges.
    """

    def __init__( self, systemName, BBNObject, BCVObject ):
        assert( systemName )
        assert( BBNObject )
        assert( BCVObject )
        self.BibleBookNames = BBNObject
        self.BibleChaptersVerses = BCVObject
        self.load( systemName )
    # end of __init__

    def __str__( self ):
        """
        This method returns the string representation of a Bible object.
        
        @return: the name of a Bible object formatted as a string
        @rtype: string
        """
        result = ""
        if self.systemName: result += ('\n' if result else '') + self.systemName
        #if self.versionName and self.versionName!=self.name: result += ('\n' if result else '') + self.versionName
        return result
    # end of __str__

    def load( self, systemName ):
        self.systemName = systemName
        if systemName in builtinSystems:
            self.characters = builtinSystems[systemName]
        else:
            self.systemName = None
            self.characters = None
            logging.error( "Sorry, this program doesn't handle the '%s' language system for Bible references yet." % systemName )
    # end of load

    def makeReferenceString( self, ref ):
        """
        Makes a string out of a reference tuple
        """
        assert( ref and len(ref)==3 )
        BBB, C, V = ref
        BnC = self.characters['BooknameCase'] if isinstance(self.characters['BooknameCase'],str) else self.characters['BooknameCase'][0]
        BCS = self.characters['BookChapterSeparator'] if isinstance(self.characters['BookChapterSeparator'],str) else self.characters['BookChapterSeparator'][0]
        CVS = self.characters['ChapterVerseSeparator'] if isinstance(self.characters['ChapterVerseSeparator'],str) else self.characters['ChapterVerseSeparator'][0]
        if BBB[0].isdigit(): # Have a book name like 1SA
            BBBstr = BBB[0] + ( BBB[1:] if BnC=='U' else BBB[1:].lower() if BnC=='L' else BBB[1:].capitalize() )
        else:
            BBBstr = BBB if BnC=='U' else BBB.lower() if BnC=='L' else BBB.capitalize()
        if BBB in USFMBibleBookCodes.OneChapterBookListUC:
            assert( C == '1' )
            resultString = "%s%s%s%s" % ( BBBstr, BCS, ' ' if self.characters['SpaceAllowedAfterBCS']=='Y' else '', V )
        else: # it's a book with multiple chapters
            resultString = "%s%s%s%s%s%s" % ( BBBstr, BCS, ' ' if self.characters['SpaceAllowedAfterBCS']=='Y' else '', C, CVS, V )
        return resultString
    # end of makeReferenceString

    def checkWithErrorMsgs( self, refList, referenceString="(unknown)" ):
        """
        Check a reference range list

        Returns haveErrors, haveWarnings
        """
        assert( refList )

        # Take a list that might include ranges, and convert it into a single list
        singleList = []
        haveErrors, haveWarnings = False, False
        for refOrRefs in refList:
            #print( refOrRefs )
            if isinstance( refOrRefs, list ): # We have a list of two items, i.e., a verse range
                assert( len(refOrRefs) == 2 )
                startRef, endRef = refOrRefs
                verseList, haveErrors, haveWarnings = self.BibleChaptersVerses.expandCVRangeWithErrorMsgs( startRef, endRef, referenceString )
                singleList.extend( verseList )
            else: # it must be a single reference
                BBB, C, V = refOrRefs
                if not self.BibleChaptersVerses.CVValidWithErrorMsgs( BBB, C, V, referenceString ):
                    haveErrors = True
                singleList.append( refOrRefs )
        singleSet = set( singleList )
        if len(singleSet) < len(singleList):
            for entry in singleSet:
                if singleList.count(entry) > 1:
                    #print( entry )
                    pass
                    #logging.warning( "Have duplicate or overlapping range at %s in Bible references '%s'" % ( self.makeReferenceString(entry), referenceString ) )
            haveWarnings = True
        return haveErrors, haveWarnings
    # end of checkWithErrorMsgs

    def parseWithErrorMsgs( self, referenceString ):
        """
        Returns a tuple with True/False result, haveWarnings, list of (BBB, C, V) tuples
        """
        #print( "Processing '%s'" % referenceString )
        assert( self.characters )
        assert( referenceString )
        haveWarnings, haveErrors = False, False
        strippedReferenceString = referenceString.strip()
        if strippedReferenceString != referenceString:
            logging.warning( "Reference string '%s' contains surrounding space(s)" % referenceString )
            haveWarnings = True
        status = 0  # 0:getting bookname, 1:getting chapter, 2:getting verse, 3:done both, 4:expecting either another chapter number or a book name
                    #   5: getting chapter or verse range, 6: getting chapter range, 7: getting verse range
        bookName, BBB, C, V, refList = '', '', '', '', []
        for char in strippedReferenceString:
            #print( "At %i got '%s'" % ( status,char ), haveErrors, haveWarnings, refList )
            if status == 0: # Getting bookname
                if char.isalnum():
                    bookName += char
                elif char in self.characters['BookChapterSeparator']:
                    BBB = self.BibleBookNames.getBBB( bookName )
                    if BBB is None:
                        logging.error( "Invalid '%s' bookname in Bible reference '%s'" % ( bookName, referenceString ) )
                        haveErrors = True
                    else:
                        C, V = '', ''
                    spaceCount = 1 if char==' ' else 0
                    status = 1
                else:
                    logging.error( "Unexpected '%s' character in Bible reference '%s' when getting book name" % ( char, referenceString ) )
                    haveErrors = True
            elif status == 1: # Getting chapter number (most probably -- but could be a verse number for a single chapter book)
                if char==' ' and not C:
                    if self.characters['SpaceAllowedAfterBCS']=='N' or spaceCount>1:
                        logging.warning( "Extra space(s) after bookname in Bible reference '%s'" % referenceString )
                        haveWarnings = True
                    spaceCount += 1
                elif char.isdigit() or char in ('a','b','c','d','e'): # Could be like verse 5a
                    if self.characters['SpaceAllowedAfterBCS']=='Y' and spaceCount<1:
                        logging.warning( "Missing space after bookname in Bible reference '%s'" % referenceString )
                        haveWarnings = True
                    C += char
                elif C and char in self.characters['ChapterVerseSeparator']:
                    status = 2
                elif C and BBB in USFMBibleBookCodes.OneChapterBookListUC:
                    V = C
                    C = '1'
                    if char in self.characters['VerseSeparator']:
                        refList.append( (BBB, C, V) )
                        status = 2
                    elif char in self.characters['BookSeparator']:
                        refList.append( (BBB, C, V) )
                        BBB, C, V = '', '', ''
                        status = 0
                    elif char in self.characters['VerseBridge']:
                        rangeStart = BBB, C, V
                        status = 7 # Getting verse range
                    else:
                        logging.error( "Unexpected '%s' character when processing single chapter book %s in Bible reference '%s'" % ( char, BBB, referenceString ) )
                        haveErrors = True
                    V = ''
                else:
                    logging.error( "Unexpected '%s' character in Bible reference '%s' when getting chapter number" % ( char, referenceString ) )
                    haveErrors = True
            elif status == 2: # Getting verse number
                if char == ' ' and not V:
                    logging.warning( "Extra space(s) after chapter in %s Bible reference '%s'" % ( BBB, referenceString ) )
                    haveWarnings = True
                elif char.isdigit() or char in ('a','b','c','d','e'): # Could be like verse 5a
                    V += char
                elif V and char in self.characters['VerseSeparator']:
                    refList.append( (BBB, C, V) )
                    V = ''
                elif V and (char in self.characters['ChapterSeparator'] or char in self.characters['BookSeparator']):
                    refList.append( (BBB, C, V) )
                    V = ''
                    if self.characters['ChapterSeparator'] == self.characters['BookSeparator']:
                        temp, spaceCount = '', 0
                        status = 4 # We don't know what to expect next
                    elif char in self.characters['ChapterSeparator']:
                        C = ''
                        status = 1
                    elif char in self.characters['BookSeparator']:
                        bookName, BBB, C = '', '', ''
                        status = 0
                elif char in self.characters['ChapterBridge']:
                    rangeStart = BBB, C, V
                    V = ''
                    if char not in self.characters['VerseBridge']: # Must be a chapter bridge
                        C = ''
                        status = 6
                    else: # We don't know what kind of bridge this is
                        X = ''
                        status = 5
                elif char in self.characters['VerseBridge']:
                    rangeStart = BBB, C, V
                    V = ''
                    status = 7
                else:
                    logging.error( "Unexpected '%s' character when getting verse number in %s %s Bible reference '%s'" % ( char, BBB, C, referenceString ) )
                    haveErrors = True
                    if V:
                        refList.append( (BBB, C, V) )
                        V = ''
            elif status == 4: # Getting the next chapter number or book name (not sure which)
                if char == ' ' and not temp:
                    if spaceCount:
                        logging.warning( "Extra space(s) after chapter or book separator in %s Bible reference '%s'" % ( BBB, referenceString ) )
                        haveWarnings = True
                    spaceCount += 1
                elif char.isalnum():
                    temp += char
                else:
                    #print( "Got '%s'" % temp )
                    if char in self.characters['ChapterVerseSeparator'] and temp and temp.isdigit(): # Assume it's a follow on chapter number
                        C = temp
                        status = 2
                    elif char in self.characters['BookChapterSeparator']:
                        bookName = temp
                        BBB = self.BibleBookNames.getBBB( bookName )
                        if BBB is None:
                            logging.error( "Invalid '%s' bookname in Bible reference '%s'" % ( bookName, referenceString ) )
                            haveErrors = True
                        C, V = '', ''
                        spaceCount = 1 if char==' ' else 0
                        status = 1
                    else:
                        logging.error( "Unexpected '%s' character when getting book name in Bible reference '%s'" % ( char, referenceString ) )
                        haveErrors = True
            elif status == 5: # Get either chapter or verse range
                if char == ' ' and not X:
                    logging.warning( "Extra space(s) after range bridge in Bible reference '%s'" % referenceString )
                    haveWarnings = True
                elif char.isdigit() or char in ('a','b','c','d','e'): # Could be like verse 5a
                    X += char
                elif X and char in self.characters['ChapterVerseSeparator']:
                    C = X
                    V = ''
                    status = 7
                elif X and char in self.characters['VerseSeparator']:
                    V = X
                    refList.append( [rangeStart, (BBB, C, V)] )
                    V = ''
                    status = 2
                elif X and (char in self.characters['ChapterSeparator'] or char in self.characters['BookSeparator']):
                    V = X
                    refList.append( [rangeStart, (BBB, C, V)] )
                    V = ''
                    if self.characters['ChapterSeparator'] == self.characters['BookSeparator']:
                        temp, spaceCount = '', 0
                        status = 4 # We don't know what to expect next
                    elif char in self.characters['ChapterSeparator']:
                        C = ''
                        status = 1
                    elif char in self.characters['BookSeparator']:
                        bookName, BBB, C = '', '', ''
                        status = 0
                    else: assert( "Should never happen" == 123 )
                else:
                    logging.error( "Unexpected '%s' character when getting second chapter/verse number in Bible reference '%s'" % ( char, referenceString ) )
                    haveErrors = True
            elif status == 6: # Get chapter range
                if char==' ' and not C:
                    if self.characters['SpaceAllowedAfterBCS']=='N' or spaceCount>1:
                        logging.warning( "Extra space(s) after bridge character in Bible reference '%s'" % referenceString )
                        haveWarnings = True
                    spaceCount += 1
                elif char.isdigit():
                    if self.characters['SpaceAllowedAfterBCS']=='Y' and spaceCount<1:
                        logging.warning( "Missing space after bridge character in Bible reference '%s'" % referenceString )
                        haveWarnings = True
                    C += char
                elif C and char in self.characters['ChapterVerseSeparator']:
                    status = 2
                elif C and BBB in USFMBibleBookCodes.OneChapterBookListUC and char in self.characters['VerseSeparator']:
                    V = C
                    C = '1'
                    refList.append( [rangeStart, (BBB, C, V)] )
                    V = ''
                    status = 7
                elif C and BBB in USFMBibleBookCodes.OneChapterBookListUC and char in self.characters['BookSeparator']:
                    V = C
                    C = '1'
                    refList.append( [rangeStart, (BBB, C, V)] )
                    BBB, C, V = '', '', ''
                    status = 0
                else:
                    logging.error( "Unexpected '%s' character in Bible reference '%s' when getting second chapter number" % ( char, referenceString ) )
                    haveErrors = True
            elif status == 7: # Get verse range
                if char == ' ' and not V:
                    logging.warning( "Extra space(s) after chapter in range in %s Bible reference '%s'" % ( BBB, referenceString ) )
                    haveWarnings = True
                elif char.isdigit() or char in ('a','b','c','d','e'): # Could be like verse 5a
                    V += char
                elif V and char in self.characters['VerseSeparator']:
                    refList.append( [rangeStart, (BBB, C, V)] )
                    V = ''
                elif V and (char in self.characters['ChapterSeparator'] or char in self.characters['BookSeparator']):
                    refList.append( [rangeStart, (BBB, C, V)] )
                    V = ''
                    if self.characters['ChapterSeparator'] == self.characters['BookSeparator']:
                        temp, spaceCount = '', 0
                        status = 4 # We don't know what to expect next
                    elif char in self.characters['ChapterSeparator']:
                        C = ''
                        status = 1
                    elif char in self.characters['BookSeparator']:
                        bookName, BBB, C = '', '', ''
                        status = 0
                else:
                    logging.error( "Unexpected '%s' character when getting verse number for range in %s %s Bible reference '%s'" % ( char, BBB, C, referenceString ) )
                    haveErrors = True
                    if V:
                        refList.append( (BBB, C, V) )
                        V = ''
        if status==1 and C and BBB in USFMBibleBookCodes.OneChapterBookListUC: # Have a single chapter book and what we were given is presumably the verse number
                V = C
                C = '1'
                status = 9
        elif status==2: # Got a C but still getting the V hopefully
            if V:
                status = 3
        elif status==4: # Must have ended with a seperator character
            logging.warning( "Bible reference '%s' ended with a separator character" % referenceString )
            haveWarnings = True
            status = 9;
        elif status==5 and X:
            V = X
            refList.append( [rangeStart, (BBB, C, V)] )
            status = 9
        elif status==7 and V:
            refList.append( [rangeStart, (BBB, C, V)] )
            status = 9
        if status==3 and not haveErrors:
            refList.append( (BBB, C, V) )
            status = 9

        #print( "Final status is %i" % status )
        self.checkWithErrorMsgs( refList, referenceString )
        #if haveErrors: print( refList ); halt
        return status==9 and not haveErrors, haveWarnings, refList
# end of class BibleRangeReferences


def demo():
    """Demonstrate reading and processing some Bible name databases.
    """
    BBN = BibleBookNames.BibleBookNames( "English" )
    BCV = BibleChaptersVerses.BibleChaptersVerses( "EnglishProtestantSystem" )

    BSR = BibleSingleReference( "EnglishSystem", BBN, BCV )
    #print( BSR )
    print( "\nSingle Reference (good)" )
    print( BSR.parseWithErrorMsgs( "Mat 7:3" ), BSR.parseWithErrorMsgs( "Mat.7:3" ), BSR.parseWithErrorMsgs( "Mat. 7:3" ), BSR.parseWithErrorMsgs( "Mt. 7:3" ), BSR.parseWithErrorMsgs( "Mt.7:3" ) )
    print( BSR.parseWithErrorMsgs( "Jud 7" ), BSR.parseWithErrorMsgs( "Jud. 7" ), BSR.parseWithErrorMsgs( "Jud 1:7" ), BSR.parseWithErrorMsgs( "Jud. 1:7" ) )
    print( "\nSingle Reference (bad)" )
    print( BSR.parseWithErrorMsgs( "Mat 0:3" ), BSR.parseWithErrorMsgs( "Mat.7:0" ), BSR.parseWithErrorMsgs( "Mat. 77:3" ), BSR.parseWithErrorMsgs( "Mt. 7:93" ) )
    print( BSR.parseWithErrorMsgs( "M 7:3" ), BSR.parseWithErrorMsgs( "Mit 7:3" ), BSR.parseWithErrorMsgs( "Mt. 7:3" ), BSR.parseWithErrorMsgs( "Mit. 7:3" ) )
    print( BSR.parseWithErrorMsgs( "Mat, 7:3" ) )
    print( BSR.parseWithErrorMsgs( "Mat. 7:3xyz5" ) )

    BSRs = BibleSingleReferences( "EnglishSystem", BBN, BCV )
    #print( BSRs )
    print( "\n\nSingle References (good)" )
    print( BSRs.parseWithErrorMsgs( "Mat 7:3" ), BSRs.parseWithErrorMsgs( "Mat.7:3" ), BSRs.parseWithErrorMsgs( "Mat. 7:3" ), BSRs.parseWithErrorMsgs( "Mt. 7:3" ), BSRs.parseWithErrorMsgs( "Mt.7:3" ) )
    print( BSRs.parseWithErrorMsgs( "Jud 7" ), BSRs.parseWithErrorMsgs( "Jud. 7" ), BSRs.parseWithErrorMsgs( "Jud 1:7" ), BSRs.parseWithErrorMsgs( "Jud. 1:7" ) )
    print( BSRs.parseWithErrorMsgs( "Mat. 7:3,7" ), BSRs.parseWithErrorMsgs( "Mat. 7:3; 4:7" ), BSRs.parseWithErrorMsgs( "Mat. 7:3,7; 4:7" ), BSRs.parseWithErrorMsgs( "Mat. 7:3,7; 4:7,9,11" ) )
    print( BSRs.parseWithErrorMsgs( "Mat. 7:3; Heb. 2:2; Rev. 1:1" ), BSRs.parseWithErrorMsgs( "Mat. 7:3,7; Heb 2:2,9; Rev. 1:1" ), BSRs.parseWithErrorMsgs( "Mat. 7:3,7; 8:17; Heb 2:2,9; 4:4,7; Rev. 1:1; 1:1" ) )
    print( "\nSingle References (bad)" )
    print( BSRs.parseWithErrorMsgs( "Mat 0:3" ), BSRs.parseWithErrorMsgs( "Mat.7:0" ), BSRs.parseWithErrorMsgs( "Mat. 77:3" ), BSRs.parseWithErrorMsgs( "Mt. 7:93" ) )
    print( BSRs.parseWithErrorMsgs( "M 7:3" ), BSRs.parseWithErrorMsgs( "Mit 7:3" ), BSRs.parseWithErrorMsgs( "Mt. 7:3" ), BSRs.parseWithErrorMsgs( "Mit. 7:3" ) )
    print( BSRs.parseWithErrorMsgs( "Mat, 7:3" ) )
    print( BSRs.parseWithErrorMsgs( "Mat. 7:3xyz5" ) )

    BRRs = BibleRangeReferences( "EnglishSystem", BBN, BCV )
    #print( BRRs )
    print( BRRs.makeReferenceString(("MAT", "7", "3")), BRRs.makeReferenceString(("PHM", "1", "3")) )
    #print( "\n\nSingle References for Ranges (good)" )
    #print( BRRs.parseWithErrorMsgs( "Mat 7:3" ), BRRs.parseWithErrorMsgs( "Mat.7:3" ), BRRs.parseWithErrorMsgs( "Mat. 7:3" ), BRRs.parseWithErrorMsgs( "Mt. 7:3" ), BRRs.parseWithErrorMsgs( "Mt.7:3" ) )
    #print( BRRs.parseWithErrorMsgs( "Jud 7" ), BRRs.parseWithErrorMsgs( "Jud. 7" ), BRRs.parseWithErrorMsgs( "Jud 1:7" ), BRRs.parseWithErrorMsgs( "Jud. 1:7" ) )
    #print( BRRs.parseWithErrorMsgs( "Mat. 7:3,7" ), BRRs.parseWithErrorMsgs( "Mat. 7:3; 4:7" ), BRRs.parseWithErrorMsgs( "Mat. 7:3,7; 4:7" ), BRRs.parseWithErrorMsgs( "Mat. 7:3,7; 4:7,9,11" ) )
    #print( BRRs.parseWithErrorMsgs( "Mat. 7:3; Heb. 2:2; Rev. 1:1" ), BRRs.parseWithErrorMsgs( "Mat. 7:3,7; Heb 2:2,9; Rev. 1:1" ), BRRs.parseWithErrorMsgs( "Mat. 7:3,7; 8:17; Heb 2:2,9; 4:4,7; Rev. 1:1; 1:1" ) )
    #print( "\nSingle References for Ranges (bad)" )
    #print( BRRs.parseWithErrorMsgs( "Mat 0:3" ), BRRs.parseWithErrorMsgs( "Mat.7:0" ), BRRs.parseWithErrorMsgs( "Mat. 77:3" ), BRRs.parseWithErrorMsgs( "Mt. 7:93" ) )
    #print( BRRs.parseWithErrorMsgs( "M 7:3" ), BRRs.parseWithErrorMsgs( "Mit 7:3" ), BRRs.parseWithErrorMsgs( "Mt. 7:3" ), BRRs.parseWithErrorMsgs( "Mit. 7:3" ) )
    #print( BRRs.parseWithErrorMsgs( "Mat, 7:3" ) )
    #print( BRRs.parseWithErrorMsgs( "Mat. 7:3xyz5" ) )
    print( "\n\nSingle Ranges (good)" )
    print( BRRs.parseWithErrorMsgs( "Mat 7:3-7" ), BRRs.parseWithErrorMsgs( "Mat.7:3-11" ), BRRs.parseWithErrorMsgs( "Mat. 7:13-8:2" ), BRRs.parseWithErrorMsgs( "Mt. 7:3,5-9" ), BRRs.parseWithErrorMsgs( "Mt.7:3-4,6-9" ) )
    print( BRRs.parseWithErrorMsgs( "Jud 7-8" ), BRRs.parseWithErrorMsgs( "Jud. 1-3" ), BRRs.parseWithErrorMsgs( "Jud 1:7-8" ), BRRs.parseWithErrorMsgs( "Jud. 1:1-3,5,7-9" ) )
    print( BRRs.parseWithErrorMsgs( "EXO.4:14,27-30;  5:1,4,20; 6:13,20,23,25-27; 7:1,2,6-10,10,12,19,20; 8:1,2,4,8,12,13,21;" ) )
    print( "\n\nSingle Ranges (bad)" )
    print( BRRs.parseWithErrorMsgs( "EXO.4:14-12; NUM.3:12-1:5; JOS.4:5-5" ) )
    #print( BRRs.parseWithErrorMsgs( "Mat. 7:3,7" ), BRRs.parseWithErrorMsgs( "Mat. 7:3; 4:7" ), BRRs.parseWithErrorMsgs( "Mat. 7:3,7; 4:7" ), BRRs.parseWithErrorMsgs( "Mat. 7:3,7; 4:7,9,11" ) )
    #print( BRRs.parseWithErrorMsgs( "Mat. 7:3; Heb. 2:2; Rev. 1:1" ), BRRs.parseWithErrorMsgs( "Mat. 7:3,7; Heb 2:2,9; Rev. 1:1" ), BRRs.parseWithErrorMsgs( "Mat. 7:3,7; 8:17; Heb 2:2,9; 4:4,7; Rev. 1:1; 1:1" ) )

if __name__ == '__main__':
    demo()
# end of BibleReferences.py
