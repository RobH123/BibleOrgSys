#!/usr/bin/python3
#
# USFMBibleMarkers.py
#
# Module handling the USFM markers for Bible books
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
Module for defining and manipulating USFM Bible markers.
"""


# Globals
USFMVersion = "2.2"


# Line markers
ProjectMarkers = ( 'id', 'ide', 'sts', 'rem', 'h' )
IntroductionMarkers = ( 'toc1', 'toc2', 'toc3', 'imt1', 'is1', 'ip', 'ipi', 'im', 'imi', 'ipq', 'imq', 'ipr', 'iq1', 'iq2', 'ib', 'ili', 'iot', 'io1', 'io2', 'ior', 'iex', 'ie' )
HeaderMarkers = ( 'mt1', 'mt2', 'mt3', 'mte1', 'mte2' )
TextMarkers = ( 'ms1', 'ms2', 'mr', 's1', 's2', 'sr', 'r', 'd', 'sp', 'p', 'v', 'q1', 'q2', 'q3', 'm', 'b' )
AllParagraphMarkers = ProjectMarkers + IntroductionMarkers + HeaderMarkers + TextMarkers


# Character markers
IntroductionCharacterMarkers = ( 'iqt' )
HeaderCharacterMarkers = ( 'rq' )
AllCharacterMarkers = IntroductionCharacterMarkers + HeaderCharacterMarkers


MarkerDB = ( # marker, status code, text code, name, type, occurs, details
    # Status code = C:compulsory, O:optional
    # Text code = M:must, N:never, C:can contain text, D:digits only
# Identification
    ( 'id', 'C', 'M', "File identification", "paragraph", "Introduction", "This is the initial USFM marker in any scripture text file" ),
    ( 'ide', 'O', 'M', "An optional character encoding specification", "paragraph", "Introduction", "This marker should be used to specify the character encoding of the text within the file" ),
    ( 'sts', 'O', 'M', "Project status tracking", "paragraph", "Introduction", "The contents of the status marker can be defined by the downstream system being used to track project status" ),
    ( 'rem', 'O', 'M', "Used for adding brief comments by a translator, consultant, or support person", "paragraph", "Introduction", "" ),
    ( 'h', 'C', 'M', "Running header text", "paragraph", "Introduction", "" ),
    ( 'toc1', 'O', 'M', "Long table of contents text", "paragraph", "Introduction", "" ),
    ( 'toc2', 'O', 'M', "Short table of contents text", "paragraph", "Introduction", "" ),
    ( 'toc3', 'O', 'M', "Book abbreviation", "paragraph", "Introduction", "" ),
# Introductions
    ( 'imt', 'O', 'M', "Introduction main title", "paragraph", "Introduction", "" ),
    ( 'is', 'O', 'M', "Introduction section heading", "paragraph", "Introduction", "" ),
    ( 'ip', 'O', 'M', "Introduction paragraph", "paragraph", "Introduction", "" ),
    ( 'ipi', 'O', 'M', "Indented introduction paragraph", "paragraph", "Introduction", "" ),
    ( 'im', 'O', 'M', "Introduction flush left (margin) paragraph", "paragraph", "Introduction", "" ),
    ( 'imi', 'O', 'M', "Introduction flush left (margin) paragraph", "paragraph", "Introduction", "" ),
    ( 'ipq', 'O', 'M', "Introduction quote from text paragraph", "paragraph", "Introduction", "" ),
    ( 'imq', 'O', 'M', "Introduction flush left (margin) quote from text paragraph", "paragraph", "Introduction", "" ),
    ( 'ipr', 'O', 'M', "Introduction right-aligned paragraph", "paragraph", "Introduction", "Typically used for a quote from text reference" ),
    ( 'iq', 'O', 'M', "Introduction poetic line", "paragraph", "Introduction", "" ),
    ( 'ib', 'O', 'N', "Introduction blank line", "paragraph", "Introduction", "May be used to explicitly indicate additional white space between paragraphs" ),
    ( 'ili', 'O', 'M', "Introduction list item", "paragraph", "Introduction", "" ),
    ( 'iot', 'O', 'M', "Introduction outline title", "paragraph", "Introduction", "" ),
    ( 'io', 'O', 'M', "Introduction outline entry", "paragraph", "Introduction", "The outline entry typically ends with a range of references in parentheses" ),
    ( 'iot', 'O', 'M', "Introduction outline title", "paragraph", "Introduction", "" ),
    ( 'ior', 'O', 'M', "Introduction outline reference range", "paragraph", "Introduction", "An outline entry typically ends with a range of references in parentheses. This is an optional character style for marking (and potentially formatting) these references separately" ),
    ( 'iex', 'O', 'M', "Introduction explanatory or bridge text", "paragraph", "Introduction", "e.g. explanation of missing book in a short Old Testament" ),
    ( 'iqt', 'O', 'M', "Introduction quoted text", "character", "Introduction", "Scripture quotations, or other quoted text, appearing in the introduction" ),
    ( 'imte', 'O', 'M', "Introduction major title ending", "paragraph", "Introduction", "Used to mark a major title indicating the end of the introduction" ),
    ( 'ie', 'O', 'M', "Introduction end", "paragraph", "Introduction", "Optionally included to explicitly indicate the end of the introduction material" ),
# Titles, headings, and labels
    ( 'b', 'O', 'N', "Blank line", "paragraph", "Text", "May be used to explicitly indicate additional white space between paragraphs" ),
)

MarkerConversions = (
    ( 'imt', 'imt1' ),
    ( 'is', 'is1' ),
    ( 'iq', 'iq1' ),
    ( 'ili', 'ili1' ),
    ( 'io', 'io1' ),
    ( 'imte', 'imte1' ),
    ( 'mt', 'mt1' ),
    ( 'mte', 'mte1' ),
    ( 'ms', 'ms1' ),
    ( 's', 's1' ),
    ( 'q', 'q1' ),
)

MarkerBackConversions = (
    ( 'imt1', 'imt' ), ( 'imt2', 'imt' ),
    ( 'is1', 'is' ), ( 'is2', 'is' ),
    ( 'iq1', 'iq' ), ( 'iq2', 'iq' ),
    ( 'ili1', 'ili' ), ( 'ili2', 'ili' ),
    ( 'io1', 'io' ), ( 'io2', 'io' ),
    ( 'imte1', 'imte' ), ( 'imte2', 'imte' ),
    ( 'mt1', 'mt' ), ( 'mt2', 'mt' ), ( 'mt3', 'mt' ),
    ( 'mte1', 'mte' ), ( 'mte2', 'mte' ),
    ( 'ms1', 'ms' ), ( 'ms2', 'ms' ),
    ( 's1', 's' ), ( 's2', 's' ),
    ( 'q1', 'q' ), ( 'q2', 'q' ),
)

def demo():
    """Demonstrate reading and processing some Bible databases.
    """
    pass

if __name__ == '__main__':
    demo()
