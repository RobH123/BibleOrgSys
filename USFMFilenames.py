#!/usr/bin/python3
#
# USFMFilenames.py
#
# Module handling USFM Bible filenames
#   Last modified: 2011-01-17 (also update versionString below)
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
Module for creating and manipulating USFM filenames.
"""

progName = "USFM Bible filenames handler"
versionString = "0.54"


import os

from singleton import singleton
import Globals
from BibleBooksCodes import BibleBooksCodes


#@singleton # Can only ever have one instance
class USFMFilenames:
    """
    Class for creating and manipulating USFM Filenames.
    """

    def __init__( self, folder ):
        """
        Create the object.
        """
        # Get the data tables that we need for proper checking
        self.BibleBooksCodes = BibleBooksCodes().loadData()

        self.folder = folder
        files = os.listdir( self.folder )
        if not files: raise IOError("No files in given folder: " + self.folder)
        for foundFilename in files:
            if not foundFilename.endswith('~'):
                foundFileBit, foundExtBit = os.path.splitext( foundFilename )
                foundLength = len( foundFileBit )
                #print( foundFileBit, foundExtBit )
                containsDigits = False
                for char in foundFilename:
                    if char.isdigit():
                        containsDigits = True
                        break
                matched = False
                if foundLength>=8 and containsDigits and foundExtBit and foundExtBit[0]=='.':
                    for paratextBookCode,paratextDigits,bookReferenceCode in self.BibleBooksCodes.getAllParatextBooksCodeNumberTriples():
                        if paratextDigits in foundFileBit and (paratextBookCode in foundFileBit or paratextBookCode.upper() in foundFileBit):
                            digitsIndex = foundFileBit.index( paratextDigits )
                            paratextBookCodeIndex = foundFileBit.index(paratextBookCode) if paratextBookCode in foundFileBit else foundFileBit.index(paratextBookCode.upper())
                            paratextBookCode = foundFileBit[paratextBookCodeIndex:paratextBookCodeIndex+3]
                            #print( digitsIndex, paratextBookCodeIndex, paratextBookCode )
                            if digitsIndex==0 and paratextBookCodeIndex==2:
                                self.languageIndex = 5
                                self.languageCode = foundFileBit[self.languageIndex:self.languageIndex+foundLength-5]
                                self.digitsIndex = digitsIndex
                                self.paratextBookCodeIndex = paratextBookCodeIndex
                                self.pattern = "ddbbb" + 'n'*(foundLength-5)
                            elif foundLength==8 and digitsIndex==3 and paratextBookCodeIndex==5:
                                self.languageIndex = 0
                                self.languageCode = foundFileBit[self.languageIndex:self.languageIndex+foundLength-5]
                                self.digitsIndex = digitsIndex
                                self.paratextBookCodeIndex = paratextBookCodeIndex
                                self.pattern = "nnnddbbb"
                            else: raise ValueError( "Unrecognized USFM filename template at "+foundFileBit )
                            if self.languageCode.isupper(): self.pattern = self.pattern.replace( 'n', 'N' )
                            if paratextBookCode.isupper(): self.pattern = self.pattern.replace( 'bbb', 'BBB' )
                            self.fileExtension = foundExtBit[1:]
                            matched = True
                            break
                if matched: break
        if not matched:
            raise ValueError( "Unable to recognize valid USFM files in " + folder )
        #print( self.pattern, self.fileExtension )
        

    def __str__( self ):
        """
        This method returns the string representation of an object.
        
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
        for paratextBookCode,paratextDigits,bookReferenceCode in self.BibleBooksCodes.getAllParatextBooksCodeNumberTriples():
            filename = "--------" # Eight characters
            filename = filename[:self.digitsIndex] + paratextDigits + filename[self.digitsIndex+len(paratextDigits):]
            filename = filename[:self.paratextBookCodeIndex] + paratextBookCode.upper() if 'BBB' in self.pattern else paratextBookCode + filename[self.paratextBookCodeIndex+len(paratextBookCode):]
            filename = filename[:self.languageIndex] + self.languageCode + filename[self.languageIndex+len(self.languageCode):]
            filename += '.' + self.fileExtension
            #print( filename )
            filelist.append( (bookReferenceCode,filename,) )
        return filelist


    def actualFiles( self ):
        """Return a list of tuples of UPPER CASE book codes with actual (present) USFM filenames"""
        filelist = []
        for bookReferenceCode,possibleFilename in self.possibleFiles():
            possibleFilepath = os.path.join( self.folder, possibleFilename )
            #print( '  Looking for: ' + possibleFilename )
            if os.access( possibleFilepath, os.R_OK ):
                #paratextBookCode = possibleFilename[self.paratextBookCodeIndex:self.paratextBookCodeIndex+3].upper()
                filelist.append( (bookReferenceCode, possibleFilename,) )
        return filelist
# end of class USFMFiles


def demo():
    """Demonstrate reading and processing some Bible databases.
    """
    # Handle command line parameters
    from optparse import OptionParser
    parser = OptionParser( version="v{}".format( versionString ) )
    #parser.add_option("-e", "--export", action="store_true", dest="export", default=False, help="export the XML file to .py and .h tables suitable for directly including into other programs")
    Globals.addStandardOptionsAndProcess( parser )

    if Globals.verbosityLevel > 0: print( "{} V{}".format( progName, versionString ) )

    test = USFMFilenames( '/mnt/Data/Matigsalug/Scripture/MBTV' )
    print( test )
    print( test.possibleFiles() )
    print( test.actualFiles() )
    print( 2 )
    test = USFMFilenames( '/mnt/Vista/Program Files/Paratext 6/GNTUK' )
    print( test )
    print( test.possibleFiles() )
    print( test.actualFiles() )

if __name__ == '__main__':
    demo()
# end of USFMFilenames.py
