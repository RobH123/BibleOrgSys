#!/usr/bin/python3
#
# USFMFilenames.py
#
# Module handling the USFM Bible filenames
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
Module for creating and manipulating BibleBookName objects.
"""


import os
import SFMFile, USFMBibleBookCodes


class USFMFilenames:
    """
    Class for creating and manipulating Bible book name objects.
    """

    def __init__( self, folder ):
        self.folder = folder
        files = os.listdir( self.folder )
        if not files: raise IOError("No files in given folder: " + self.folder)
        for foundFilename in files:
            if not foundFilename.endswith('~'):
                foundFileBit, foundExtBit = os.path.splitext( foundFilename )
                #print( foundFileBit, foundExtBit )
                containsDigits = False
                for char in foundFilename:
                    if char.isdigit():
                        containsDigits = True
                        break
                if len(foundFileBit)==8 and containsDigits and foundExtBit and foundExtBit[0]=='.':
                    for digits,bookCode in USFMBibleBookCodes.AllBooks:
                        matched = False
                        if digits in foundFileBit and (bookCode in foundFileBit or bookCode.upper() in foundFileBit):
                            digitsIndex = foundFileBit.index( digits )
                            bookCodeIndex = foundFileBit.index(bookCode) if bookCode in foundFileBit else foundFileBit.index(bookCode.upper())
                            bookCode = foundFileBit[bookCodeIndex:bookCodeIndex+3]
                            #print( digitsIndex, bookCodeIndex, bookCode )
                            if digitsIndex==3 and bookCodeIndex==5:
                                self.languageIndex = 0
                                self.languageCode = foundFileBit[self.languageIndex:self.languageIndex+3]
                                self.digitsIndex = digitsIndex
                                self.bookCodeIndex = bookCodeIndex
                                self.pattern = "lllddbbb"
                            else: raise ValueError( "Unrecognized USFM filename template at "+foundFileBit )
                            if self.languageCode.isupper(): self.pattern = self.pattern.replace( 'lll', 'LLL' )
                            if bookCode.isupper(): self.pattern = self.pattern.replace( 'bbb', 'BBB' )
                            self.fileExtension = foundExtBit[1:]
                            matched = True
                            break
                if matched: break
        if not matched:
            raise ValueError( "Unable to find valid USFM files in " + folder )
        #print( self.pattern, self.extension )
        

    def __str__( self ):
        """
        This method returns the string representation of a Bible object.
        
        @return: the name of a Bible object formatted as a string
        @rtype: string
        """
        result = ""
        if self.pattern: result += ('\n' if result else '') + self.pattern
        if self.fileExtension: result += ('\n' if result else '') + self.fileExtension
        return result


    def possibleFiles( self ):
        """Return a list of valid USFM filenames"""
        filelist = []
        for digits,bookCode in USFMBibleBookCodes.AllBooks:
            filename = "--------" # Eight characters
            filename = filename[:self.digitsIndex] + digits + filename[self.digitsIndex+len(digits):]
            filename = filename[:self.bookCodeIndex] + bookCode.upper() if 'BBB' in self.pattern else bookCode + filename[self.bookCodeIndex+len(bookCode):]
            filename = filename[:self.languageIndex] + self.languageCode + filename[self.languageIndex+len(self.languageCode):]
            filename += '.' + self.fileExtension
            #print( filename )
            filelist.append( filename )
        return filelist


    def actualFiles( self ):
        """Return a list of tuples of UPPER CASE book codes with actual (present) USFM filenames"""
        filelist = []
        for possibleFilename in self.possibleFiles():
            possibleFilepath = os.path.join( self.folder, possibleFilename )
            #print( '  Looking for: ' + possibleFilename )
            if os.access( possibleFilepath, os.R_OK ):
                bookCode = possibleFilename[self.bookCodeIndex:self.bookCodeIndex+3].upper()
                filelist.append( ( bookCode, possibleFilename, ) )
        return filelist
# end of class USFMFiles


def demo():
    """Demonstrate reading and processing some Bible databases.
    """
    test = USFMFilenames( '/mnt/Data/Matigsalug/Scripture/MBTV' )
    print( test )
    print( test.possibleFiles() )
    print( test.actualFiles() )

if __name__ == '__main__':
    demo()
