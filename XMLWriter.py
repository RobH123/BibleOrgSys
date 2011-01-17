#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# XMLWriter.py
#
# Module handling pretty writing of XML (and xHTML) files
#   Last modified: 2011-01-17 by RJH (also update versionString below)
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
Module handling creation of simple XML (and xHTML) files.

Why write yet another module to do this?
    Better control of field checking and warning/error messages
    Better control of file layout and indentation
    It only took half a day anyway.

TODO: Add buffering
TODO: Add writeAutoDTD

"""

progName = "XML Writer"
versionString = "0.23"


import os, logging
from collections import OrderedDict

import Globals


class XMLWriter:
    """
    A class to handle data for Bible book order systems.
    """

    def __init__( self ):
        """
        Constructor.
        """
        self.outputFilePath = None # The folder and filename
        self.outputFile = None # The actual file object

        self.spaceBeforeSelfcloseTag = False
        self._humanReadable = 'All' # Else 'None' or 'Header' or the special 'NLSpace' mode
        self._indentPerLevel = 2 # Number of spaces to indent for each level
        self._limitColumns = True # Add new lines when going over the column width limit
        self._maxColumns = 200 # Very roughly indicates the desired column width to aim for (but it can vary considerable either way because we only break in certain positions)

        self._status = "Idle" # Not sure that we really even need this
        self._sectionName = "None" # Else 'Header' or 'Main' (allows finer use of humanReadable control)
        self._buffer = ''
        self._openStack = [] # Here we keep track of what XML markers need to be closed
        self._currentColumn = 0
        self.linesWritten = 0
    # end of __init__

    def __str__( self ):
        """
        This method returns the string representation of a Bible book order system.
        
        @return: the name of a Bible object formatted as a string
        @rtype: string
        """
        result = "_XMLWriter object"
        result += ('\n' if result else '') + "  Status: {}".format(self._status)
        return result
    # end of __str__

    def setOutputFilePath( self, filename, folder=None ):
        """ Set the output filepath. """
        assert( self._status == 'Idle' )
        self.outputFilePath = os.path.join ( folder, filename ) if folder is not None else filename
        return self
    # end of setOutputFilePath

    def setHumanReadable( self, value='All', indentSize=2 ):
        """ Set the human readable flag. """
        assert( value=='All' or value=='Header' or value=='None' or value=='NLSpace' )
        self._humanReadable = value
        self._indentPerLevel = indentSize
        if value=='NLSpace':
            self._limitColumns = False
    # end of setHumanReadableFlag

    def setSectionName( self, sectionName ):
        """ Tells the writer the current section that we are writing.
            This can affect formatting depending on the _humanReadable flag. """
        assert( sectionName=='None' or sectionName=='Header' or sectionName=='Main' )
        self._sectionName = sectionName
    # end of setSection

    def _write( self, string ):
        """ Writes a string to the file.
            NOTE: This doesn't update self._currentColumn (because we don't know what we're writing here). """
        assert( self.outputFile is not None )
        self.outputFile.write( string )
    # end of _write

    def getFilePosition( self ):
        """ Returns the current position through the file (in bytes from the beginning of the file). """
        assert( self.outputFile is not None )
        return self.outputFile.tell()
    # end of getFilePosition

    def _SP( self ):
        """Returns an indent with space characters if required (else an empty string)."""
        if self._humanReadable == "None": return ''
        if self._humanReadable=="All" or self._humanReadable=="NLSpace": return ' '*len(self._openStack)*self._indentPerLevel
        # Else, we'll assume that it's set to "Header"
        if self._sectionName == 'Main': return ''
        return ' '*len(self._openStack)*self._indentPerLevel # for header
    # end of _SP

    def _NL( self ):
        """Returns a newline character if required (else an empty string)."""
        if self._humanReadable == "None": result = ''
        elif self._humanReadable == "All":  result = '\n'
        elif self._humanReadable == "NLSpace":  result = ' '
        # Else, we'll assume that it's set to "Header"
        elif self._sectionName == 'Main': result = '' # (not header)
        else: result= '\n' # for header

        # Overrride if we've gone past the max column width
        if self._limitColumns and self._currentColumn >= self._maxColumns: result = '\n'

        if result == '\n': self._currentColumn = 0
        return result
    # end of _NL

    def start( self, noAutoXML=False ):
        """ Opens the file and writes a header record to it. """
        assert( self._status == 'Idle' )
        if Globals.verbosityLevel>1: print( "Writing {}...".format(self.outputFilePath) )
        self.outputFile = open( self.outputFilePath, 'wt' )
        self._status = 'Open'
        self._currentColumn = 0
        if not noAutoXML:
            chars = self._SP() + '<?xml version="1.0" encoding="UTF-8"?>'
            self._currentColumn += len(chars)
            self._write( chars + self._NL() )
        self._sectionName = 'None'
    # end of start

    def _autoWrite( self, string ):
        """ Writes a string to the file with appropriate indenting and newlines. """
        assert( self.outputFile is not None )
        chars = self._SP() + string
        length = len( chars )
        self._currentColumn += length
        final = self._NL()
        if final != '\n': length += len( final )
        self._write( chars + final )
        self._currentColumn += length
        return length
    # end of _write

    def writeNewLine( self, count=1 ):
        """ Writes a (1 or more) new line sequence to the output. """
        self._write( '\n' )
        self._currentColumn = 0
    # end of writeNewLine

    def checkTag( self, tagString ):
        """ Returns a checked string containing the tag name. """
        #print( "tagString: '{}'", tagString )
        assert( tagString ) # It can't be blank
        assert( '<' not in tagString and '>' not in tagString and '"' not in tagString )
        return tagString
    # end of checkTag

    def checkText( self, textString ):
        """ Returns a checked string containing the tag name. """
        assert( textString ) # It can't be blank
        assert( '<' not in textString and '>' not in textString and '"' not in textString )
        return textString
    # end of checkText

    def checkAttribName( self, nameString ):
        """ Returns a checked string containing the attribute name. """
        assert( nameString ) # It can't be blank
        assert( '<' not in nameString and '>' not in nameString and '"' not in nameString )
        return nameString
    # end of checkAttribName

    def checkAttribValue( self, valueString ):
        """ Returns a checked string containing the attribute value. """
        if isinstance( valueString, int ): valueString = str( valueString ) # Do an automatic conversion if they pass us and integer
        assert( valueString ) # It can't be blank (can it?)
        assert( '<' not in valueString and '>' not in valueString and '"' not in valueString )
        return valueString
    # end of checkAttribValue

    def getAttributes( self, attribInfo ):
        """ Returns a string containing the validated attributes. """
        result = ''
        if isinstance( attribInfo, tuple ): # Assume it's a single pair
            assert( len(attribInfo) == 2 )
            if result: result += ' '
            result += '{}="{}"'.format( self.checkAttribName(attribInfo[0]), self.checkAttribValue(attribInfo[1]) )
        elif isinstance( attribInfo, list ):
            for attrib,value in attribInfo:
                if result: result += ' '
                result += '{}="{}"'.format( self.checkAttribName(attrib), self.checkAttribValue(value) )
        else: # It's not a tuple or a list so we assume it's a dictionary or ordered dictionary
            for attrib,value in attribInfo.items():
                if result: result += ' '
                result += '{}="{}"'.format( self.checkAttribName(attrib), self.checkAttribValue(value) )
        return result
    # end if getAttributes

    def writeLineComment( self, text, noTextCheck=False ):
        """ Writes an XML comment field. """
        return self._autoWrite( '<!-- {} -->'.format(text if noTextCheck else self.checkText(text)) )
    # end of writeLineComment

    def writeLineText( self, text, noTextCheck=False ):
        """ Writes raw text onto a line. """
        return self._autoWrite( text if noTextCheck else self.checkText(text) )
    # end of writeLineText

    def writeLineOpen( self, openTag, attribInfo=None ):
        """ Writes an opening tag on a line. """
        if attribInfo is None:
            self._autoWrite( '<{}>'.format(self.checkTag(openTag)) )
        else: # have one or more attributes
            self._autoWrite( '<{} {}>'.format( self.checkTag(openTag), self.getAttributes(attribInfo) ) )
        self._openStack.append( openTag )
    # end of writeLineOpen

    def writeLineOpenText( self, openTag, text, attribInfo=None, noTextCheck=False ):
        """ Writes an opening tag on a line. """
        #print( "text: '{}'".format(text )
        if noTextCheck == False: text = self.checkText( text )
        if attribInfo is None:
            self._autoWrite( '<{}>{}'.format( self.checkTag(openTag), text ) )
        else: # have one or more attributes
            self._autoWrite( '<{} {}>{}'.format( self.checkTag(openTag), self.getAttributes(attribInfo), text ) )
        self._openStack.append( openTag )
    # end of writeLineOpenText

    def writeLineClose( self, closeTag ):
        """ Writes an opening tag on a line. """
        expectedTag = self._openStack.pop()
        if expectedTag != closeTag: logging.error( "Closed '{}' tag but should have closed '{}'".format( closeTag, expectedTag ) )
        self._autoWrite( '</{}>'.format(self.checkTag(closeTag)) )
    # end of writeLineOpen

    def writeLineOpenClose( self, tag, text, attribInfo=None, noTextCheck=False ):
        """ Writes an opening and closing tag on the same line. """
        checkedTag = self.checkTag(tag)
        checkedText = text if noTextCheck else self.checkText(text)
        if attribInfo is None:
            return self._autoWrite( '<{}>{}</{}>'.format( checkedTag, checkedText, checkedTag ) )
        #else: # have one or more attributes
        return self._autoWrite( '<{} {}>{}</{}>'.format( checkedTag, self.getAttributes(attribInfo), checkedText, checkedTag ) )
    # end of writeLineOpenClose

    def writeLineOpenSelfclose( self, tag, attribInfo=None ):
        """ Writes a self-closing tag with optional attributes. """
        checkedTag = self.checkTag(tag)
        if attribInfo is None:
            return self._autoWrite( '<{}{}/>'.format( checkedTag, ' ' if self.spaceBeforeSelfcloseTag else '' ) )
        #else: # have one or more attributes
        return self._autoWrite( '<{} {}{}/>'.format( checkedTag, self.getAttributes(attribInfo), ' ' if self.spaceBeforeSelfcloseTag else '' ) )
    # end of writeLineOpenSelfclose

    def writeBuffer( self ):
        """ Writes the buffer to the file. """
        assert( self.outputFile is not None )
        if self._buffer:
            self._write( buffer )
            self._buffer = ''
    # end of writeBuffer

    def close( self ):
        """ Finish everything up and close the file. """
        assert( self.outputFile is not None )
        if self._openStack: logging.error( "Have unclosed tags: {}".format(self._openStack) )
        if self._buffer: self.writeBuffer()
        if self._status != "Buffered": pass
        self.outputFile.close()
        self._status = "Closed"
    # end of close

    def autoClose( self ):
        """ Close all open tags and finish everything up and close the file. """
        assert( self.outputFile is not None )
        assert( self._status == 'Open' )
        if Globals.debugFlag: print( "autoClose stack: {}", self._openStack )
        for index in range( len(self._openStack)-1, -1, -1 ): # Have to step through this backwards
            self.writeLineClose( self._openStack[index] )
        self._sectionName = 'None'
        self.close()
    # end of autoClose
# end of XMLWriter class


def demo():
    """
    Main program to handle command line parameters and then run what they want.
    """
    # Handle command line parameters
    from optparse import OptionParser
    parser = OptionParser( version="v{}".format( versionString ) )
    Globals.addStandardOptionsAndProcess( parser )

    if Globals.verbosityLevel>0: print( "{} V{}".format( progName, versionString ) )

    # Demo the writer object
    outputFolder = "OutputFiles"
    if not os.access( outputFolder, os.F_OK ): os.mkdir( outputFolder ) # Make the empty folder if there wasn't already one there
    xw = XMLWriter().setOutputFilePath( os.path.join( outputFolder, "test.xml" ) )
    xw.setHumanReadable( "All" )
    xw.start()
    xw.writeLineOpen( "vwxyz", [("xmlns","http://someURL.net/namespace"),("xmlns:xsi","http://someURL.net/XMLSchema-instance"),("xsi:schemaLocation","http://someURL.net/namespace http://someURL.net/myOwn.xsd")] )
    xw.writeLineOpen( "header" )
    xw.writeLineOpenClose( "title", "myTitle" )
    xw.writeLineClose( "header" )
    xw.writeLineOpen( "body" )
    xw.writeLineOpen( "division", [('id','Div1'),('name','First division')] )
    xw.writeLineOpenClose( "text", "myText in here", ("font","favouriteFont") )
    xw.autoClose()
    print( xw ) # Just print a summary
# end of main

if __name__ == '__main__':
    demo()
# end of BibleBookOrders.py
