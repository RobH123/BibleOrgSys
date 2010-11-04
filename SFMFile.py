#!/usr/bin/python3
##
# SFMFile.py
#
# SFM (Standard Format Marker) data file reader
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
Module for reading UTF-8 SFM (Standard Format Marker) file.

There are three kinds of SFM encoded files which can be loaded:
    1/ A "flat" file, read line by line into a list.
            This could be any kind of SFM data.
    2/ A "record based" file (e.g., a dictionary), read record by record into a list
    3/ A header segment, then a "record based" structure read into the same list,
            for example an interlinearized text.

  In each case, the SFM and it's field are read into a tuple and saved (in order) in the list.

  Gives a fatal error (IOError) if file doesn't exist.
"""


import logging


class SFMLines:
    """
    Class holding a list of (non-blank) SFM lines.
    Each line is a tuple consisting of (SFMMarker, SFMValue).
    """

    def __init__(self):
        self.lines = []

    def __str__(self):
        """
        This method returns the string representation of a SFM lines object.
        
        @return: the name of a SFM field object formatted as a string
        @rtype: string
        """
        result = ""
        for line in self.lines:
            if result: result += '\n'
            result += str( line )
        return result

    def read( self, sfm_filename, ignoreSFMs=None, encoding='utf-8' ):
        """Read a simple SFM (Standard Format Marker) file into a list of tuples.

        @param sfm_filename: The filename
        @type sfm_filename: string
        @param key: The SFM record marker (not including the backslash)
        @type encoding: string
        @rtype: list
        @return: list of lists containing the records
        """

        # Check/handle parameters
        if ignoreSFMs is None: ignoreSFMs = ()

        result = []
        lastLine = ''
        lineCount = 0
        with open( sfm_filename, encoding=encoding ) as myFile: # Automatically closes the file when done
            try:
                for line in myFile:
                    if lineCount==0 and encoding.lower()=='utf-8' and line[0]==chr(65279): #U+FEFF
                        print( "      Detected UTF-16 Byte Order Marker" )
                        line = line[1:] # Remove the UTF-8 Byte Order Marker
                    if line[-1]=='\n': line=line[:-1] # Removing trailing newline character
                    if not line: continue # Just discard blank lines
                    lastLine = line
                    lineCount += 1
                    #print ( 'SFM file line is "' + line + '"' )
                    #if line[0:2]=='\\_': continue # Just discard Toolbox header lines
                    if line[0]=='#': continue # Just discard comment lines

                    if line[0]!='\\':
                        if len(result)==0:
                            print( "SFMFiles.py: XXZXResult is", result, len(line) )
                            for x in range(0, min(6,len(line))):
                                print( x, "'" + str(ord(line[x])) + "'" )
                            raise IOError('Oops: Line break on last line ??? not handled here "' + line + '"')
                        else: # Append this continuation line
                            if marker not in ignoreSFMs:
                                oldmarker, oldtext = result.pop()
                                #print ("Popped",oldmarker,oldtext)
                                #print ("Adding", line, "to", oldmarker, oldtext)
                                result.append( (oldmarker, oldtext+' '+line) )
                            continue
                    if ' ' in line:
                        si = line.index(' ')
                        marker = line[1:si] #Marker is from after backslash and before the space
                        text = line[si+1:] # All the rest is the text field
                    else: # line contains no spaces
                        marker = line[1:] # The marker is the entire line (after skipping the backslash)
                        text = ''
                    if marker not in ignoreSFMs:
                        result.append( (marker, text) )
            except:
                logging.critical( "Invalid line in " + sfm_filename + " -- line ignored at " + str(lineCount) )
                if lineCount: print( 'Previous line was: ', lastLine )
                print( line )
                #raise

            self.lines = result
    # end of SFMLines.read
# end of class SFMLines


class SFMRecords:
    """
    Class holding a list of SFM records.
    Each record is a list of SFM lines. (The record always starts with the same SFMMarker, except perhaps the first record.)
    Each line is a tuple consisting of (SFMMarker, SFMValue).
    """

    def __init__(self):
        self.records = []

    def __str__(self):
        """
        This method returns the string representation of a SFM lines object.
        
        @return: the name of a SFM field object formatted as a string
        @rtype: string
        """
        result = ""
        for record in self.records:
            if result: result += '\n' # Blank line between records
            for line in record:
                if result: result += '\n'
                result += str( line )
        return result


    def read( self, sfm_filename, key=None, ignoreSFMs=None, ignoreEntries=None, changePairs=None, encoding='utf-8' ):
        """Read a simple SFM (Standard Format Marker) file into a list of lists of tuples.

        @param sfm_filename: The filename
        @type sfm_filename: string
        @param key: The SFM record marker (not including the backslash)
        @type encoding: string
        @rtype: list
        @return: list of lists containing the records
        """

        def changeMarker( currentMarker, changePairs ):
            """Change the SFM marker if required"""
            if changePairs:
                for findMarker, replaceMarker in changePairs:
                    if findMarker==currentMarker: return replaceMarker
            return currentMarker

        # Check/handle parameters
        if ignoreSFMs is None: ignoreSFMs = ()
        #print( "ignoreSFMs =", ignoreSFMs )
        if ignoreEntries is None: ignoreEntries = ()
        #print( "ignoreEntries =", ignoreEntries )
        if key:
            if '\\' in key: raise ValueError('SFM marker must not contain backslash')
            if ' ' in key: raise ValueError('SFM marker must not contain spaces')

        result = []
        record = []
        lastLine = ''
        lineCount = 0
        with open( sfm_filename, encoding=encoding ) as myFile: # Automatically closes the file when done
            try:
                for line in myFile:
                    lineCount += 1
                    if lineCount==1 and encoding.lower()=='utf-8' and line and line[0]==chr(65279): #U+FEFF
                        print( "      Detected UTF-16 Byte Order Marker" )
                        line = line[1:] # Remove the UTF-8 Byte Order Marker
                    if line[-1]=='\n': line = line[:-1] # Removing trailing newline character
                    if not line: continue # Just discard blank lines
                    lastLine = line
                    #print ( 'SFM file line is "' + line + '"' )
                    #if line[0:2]=='\\_': continue # Just discard Toolbox header lines
                    if line[0]=='#': continue # Just discard comment lines
                    if line[0]!='\\':
                        if len(record)==0:
                            print( 'SFMFiles.py: SFM file line is "' + line + '"' )
                            print( "First character of line is '" + line[0] + "' (" + str(ord(line[0])) + ")" )
                            print( "XXXRecord is", record)
                            raise IOError('Oops: Line break on last line of record not handled here "' + line + '"')
                        else: # Append this continuation line
                            oldmarker, oldtext = record.pop()
                            record.append( (oldmarker, oldtext+' '+line) )
                            continue
                    if ' ' in line: # Break into SFM marker (before space) and text (after space)
                        si = line.index(' ')
                        marker = changeMarker( line[1:si], changePairs ) #Marker is from after backslash and before the space
                        text = line[si+1:] # All the rest (if any) is the text field
                    else: # line contains no spaces
                        marker = changeMarker( line[1:], changePairs ) # The marker is the entire line (after skipping the backslash)
                        text = ''
                        if marker==key: print ("Warning: Have a blank key field after", record)
                    if not key and marker not in ignoreSFMs:
                        print ('    Assuming', marker, 'to be the SFM key for', sfm_filename)
                        key = marker
                    if marker==key: # Save the previous record
                        if record and record[0][1] not in ignoreEntries: # Looks at the text associated with the first (record key) marker
                            strippedRecord = []
                            for savedMarker,savedText in record:
                                if savedMarker not in ignoreSFMs:
                                    strippedRecord.append( (savedMarker, savedText) )
                            if strippedRecord:
                                result.append( strippedRecord )
                        record = []
                    # Save the current marker and text
                    record.append( (marker, text) )
            except:
                logging.critical( "Invalid line in " + sfm_filename + " -- line ignored at " + str(lineCount) )
                if lineCount: print( 'Previous line was: ', lastLine )
                else: print( 'Possible encoding error -- expected', encoding )
                #raise

            # Write the final record
            if record and record[0][1] not in ignoreEntries: # Looks at the text associated with the first (record key) marker
                strippedRecord = []
                for savedMarker,savedText in record:
                    if savedMarker not in ignoreSFMs:
                        strippedRecord.append( (savedMarker, savedText) )
                if strippedRecord:
                    result.append( strippedRecord ) # Append the last record

            self.records = result
    # end of SFMRecords.read
# end of class SFMRecords


def demo():
    """Demonstrate reading and processing some UTF-8 SFM databases.
    """

    import os
    folder = '/mnt/Data/SFM2Web/SFM2Web-Hg-Repo/SampleData/Lexicon'
    filename = os.path.join(folder, 'Matigsalug Dictionary A.sfm')

    linesDB = SFMLines()
    linesDB.read( filename, ignoreSFMs=('mn','aMU','aMW','cu','cp'))
    print (len(linesDB.lines), 'lines read from file', filename)
    for i, r in enumerate(linesDB.lines):
        print ( i, r)
        if i>9: break
    print ( '...\n',len(linesDB.lines)-1, linesDB.lines[len(linesDB.lines)-1], '\n') # Display the last record

    recordsDB = SFMRecords()
    recordsDB.read( filename, 'og', ignoreSFMs=('mn','aMU','aMW','cu','cp'))
    print (len(recordsDB.records), 'records read from file', filename)
    for i, r in enumerate(recordsDB.records):
        print ( i, r)
        if i>3: break
    print ('...\n',len(recordsDB.records)-1, recordsDB.records[len(recordsDB.records)-1]) # Display the last record

if __name__ == '__main__':
    demo()
# end of SFMFile.py
