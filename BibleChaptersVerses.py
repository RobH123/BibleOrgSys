#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# BibleChaptersVerses.py
#
# Module handling the names of Bible books
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


import os,logging
import SFMFile


builtinSystems = {
    # The first figure is the number of chapters in the book
    # The following figures are the number of verses in each chapter
    'OriginalLanguageSystem' : {
        'GEN': ( 50, 31, 25, 24, 26, 32, 22, 24, 22, 29, 32, 32, 20, 18, 24, 21, 16, 27, 33, 38, 18, 34, 24, 20, 67, 34, 35, 46, 22, 35, 43, 54, 33, 20, 31, 29, 43, 36, 30, 23, 23, 57, 38, 34, 34, 28, 34, 31, 22, 33, 26 ), # Different from English Protestant
        'EXO': ( 40, 22, 25, 22, 31, 23, 30, 29, 28, 35, 29, 10, 51, 22, 31, 27, 36, 16, 27, 25, 26, 37, 30, 33, 18, 40, 37, 21, 43, 46, 38, 18, 35, 23, 35, 35, 38, 29, 31, 43, 38 ), # Different from English Protestant
        'LEV': ( 27, 17, 16, 17, 35, 26, 23, 38, 36, 24, 20, 47, 8, 59, 57, 33, 34, 16, 30, 37, 27, 24, 33, 44, 23, 55, 46, 34 ), # Different from English Protestant
        'NUM': ( 36, 54, 34, 51, 49, 31, 27, 89, 26, 23, 36, 35, 16, 33, 45, 41, 35, 28, 32, 22, 29, 35, 41, 30, 25, 19, 65, 23, 31, 39, 17, 54, 42, 56, 29, 34, 13 ), # Different from English Protestant
        'DEU': ( 34, 46, 37, 29, 49, 33, 25, 26, 20, 29, 22, 32, 31, 19, 29, 23, 22, 20, 22, 21, 20, 23, 29, 26, 22, 19, 19, 26, 69, 28, 20, 30, 52, 29, 12 ), # Different from English Protestant
        'JOS': ( 24, 18, 24, 17, 24, 15, 27, 26, 35, 27, 43, 23, 24, 33, 15, 63, 10, 18, 28, 51, 9, 45, 34, 16, 33 ),
        'JDG': ( 21, 36, 23, 31, 24, 31, 40, 25, 35, 57, 18, 40, 15, 25, 20, 20, 31, 13, 31, 30, 48, 25 ),
        'RUT': ( 4, 22, 23, 18, 22 ),
        '1SA': ( 31, 28, 36, 21, 22, 12, 21, 17, 22, 27, 27, 15, 25, 23, 52, 35, 23, 58, 30, 24, 42, 16, 23, 28, 23, 44, 25, 12, 25, 11, 31, 13 ), # Different from English Protestant
        '2SA': ( 24, 27, 32, 39, 12, 25, 23, 29, 18, 13, 19, 27, 31, 39, 33, 37, 23, 29, 32, 44, 26, 22, 51, 39, 25 ), # Different from English Protestant
        '1KI': ( 22, 53, 46, 28, 20, 32, 38, 51, 66, 28, 29, 43, 33, 34, 31, 34, 34, 24, 46, 21, 43, 29, 54 ), # Different from English Protestant
        '2KI': ( 25, 18, 25, 27, 44, 27, 33, 20, 29, 37, 36, 20, 22, 25, 29, 38, 20, 41, 37, 37, 21, 26, 20, 37, 20, 30 ), # Different from English Protestant
        '1CH': ( 29, 54, 55, 24, 43, 41, 66, 40, 40, 44, 14, 47, 41, 14, 17, 29, 43, 27, 17, 19, 8, 30, 19, 32, 31, 31, 32, 34, 21, 30 ), # Different from English Protestant
        '2CH': ( 36, 18, 17, 17, 22, 14, 42, 22, 18, 31, 19, 23, 16, 23, 14, 19, 14, 19, 34, 11, 37, 20, 12, 21, 27, 28, 23, 9, 27, 36, 27, 21, 33, 25, 33, 27, 23 ), # Different from English Protestant
        'EZR': ( 10, 11, 70, 13, 24, 17, 22, 28, 36, 15, 44 ),
        'NEH': ( 13, 11, 20, 38, 17, 19, 19, 72, 18, 37, 40, 36, 47, 31 ), # Different from English Protestant
        'EST': ( 10, 22, 23, 15, 17, 14, 14, 10, 17, 32, 3 ),
        'JOB': ( 42, 22, 13, 26, 21, 27, 30, 21, 22, 35, 22, 20, 25, 28, 22, 35, 22, 16, 21, 29, 29, 34, 30, 17, 25, 6, 14, 23, 28, 25, 31, 40, 22, 33, 37, 16, 33, 24, 41, 30, 32, 26, 17 ), # Different from English Protestant
        'PSA': ( 150, 6, 12, 9, 9, 13, 11, 18, 10, 21, 18, 7, 9, 6, 7, 5, 11, 15, 51, 15, 10, 14, 32, 6, 10, 22, 12, 14, 9, 11, 13, 25, 11, 22, 23, 28, 13, 40, 23, 14, 18, 14, 12, 5, 27, 18, 12, 10, 15, 21, 23, 21, 11, 7, 9, 24, 14, 12, 12, 18, 14, 9, 13, 12, 11, 14, 20, 8, 36, 37, 6, 24, 20, 28, 23, 11, 13, 21, 72, 13, 20, 17, 8, 19, 13, 14, 17, 7, 19, 53, 17, 16, 16, 5, 23, 11, 13, 12, 9, 9, 5, 8, 29, 22, 35, 45, 48, 43, 14, 31, 7, 10, 10, 9, 8, 18, 19, 2, 29, 176, 7, 8, 9, 4, 8, 5, 6, 5, 6, 8, 8, 3, 18, 3, 3, 21, 26, 9, 8, 24, 14, 10, 8, 12, 15, 21, 10, 20, 14, 9, 6 ), # Different from English Protestant
        'PRO': ( 31, 33, 22, 35, 27, 23, 35, 27, 36, 18, 32, 31, 28, 25, 35, 33, 33, 28, 24, 29, 30, 31, 29, 35, 34, 28, 28, 27, 28, 27, 33, 31 ),
        'ECC': ( 12, 18, 26, 22, 17, 19, 12, 29, 17, 18, 20, 10, 14 ), # Different from English Protestant
        'SNG': ( 8, 17, 17, 11, 16, 16, 12, 14, 14 ), # Different from English Protestant
        'ISA': ( 66, 31, 22, 26, 6, 30, 13, 25, 23, 20, 34, 16, 6, 22, 32, 9, 14, 14, 7, 25, 6, 17, 25, 18, 23, 12, 21, 13, 29, 24, 33, 9, 20, 24, 17, 10, 22, 38, 22, 8, 31, 29, 25, 28, 28, 25, 13, 15, 22, 26, 11, 23, 15, 12, 17, 13, 12, 21, 14, 21, 22, 11, 12, 19, 11, 25, 24 ), # Different from English Protestant
        'JER': ( 52, 19, 37, 25, 31, 31, 30, 34, 23, 25, 25, 23, 17, 27, 22, 21, 21, 27, 23, 15, 18, 14, 30, 40, 10, 38, 24, 22, 17, 32, 24, 40, 44, 26, 22, 19, 32, 21, 28, 18, 16, 18, 22, 13, 30, 5, 28, 7, 47, 39, 46, 64, 34 ), # Different from English Protestant
        'LAM': ( 5, 22, 22, 66, 22, 22 ),
        'EZK': ( 48, 28, 10, 27, 17, 17, 14, 27, 18, 11, 22, 25, 28, 23, 23, 8, 63, 24, 32, 14, 44, 37, 31, 49, 27, 17, 21, 36, 26, 21, 26, 18, 32, 33, 31, 15, 38, 28, 23, 29, 49, 26, 20, 27, 31, 25, 24, 23, 35 ), # Different from English Protestant
        'DAN': ( 12, 21, 49, 33, 34, 30, 29, 28, 27, 27, 21, 45, 13 ), # Different from English Protestant
        'HOS': ( 14, 9, 25, 5, 19, 15, 11, 16, 14, 17, 15, 11, 15, 15, 10 ), # Different from English Protestant
        'JOL': ( 4, 20, 27, 5, 21 ), # Different from English Protestant
        'AMO': ( 9, 15, 16, 15, 13, 27, 14, 17, 14, 15 ),
        'OBA': ( 1, 21 ),
        'JON': ( 4, 16, 11, 10, 11 ), # Different from English Protestant
        'MIC': ( 7, 16, 13, 12, 14, 14, 16, 20 ), # Different from English Protestant
        'NAM': ( 3, 14, 14, 19 ), # Different from English Protestant
        'HAB': ( 3, 17, 20, 19 ),
        'ZEP': ( 3, 18, 15, 20 ),
        'HAG': ( 2, 15, 23 ),
        'ZEC': ( 14, 17, 17, 10, 14, 11, 15, 14, 23, 17, 12, 17, 14, 9, 21 ), # Different from English Protestant
        'MAL': ( 3, 14, 17, 24 ), # Different from English Protestant
        'MAT': ( 28, 25, 23, 17, 25, 48, 34, 29, 34, 38, 42, 30, 50, 58, 36, 39, 28, 27, 35, 30, 34, 46, 46, 39, 51, 46, 75, 66, 20 ),
        'MRK': ( 16, 45, 28, 35, 41, 43, 56, 37, 38, 50, 52, 33, 44, 37, 72, 47, 20 ),
        'LUK': ( 24, 80, 52, 38, 44, 39, 49, 50, 56, 62, 42, 54, 59, 35, 35, 32, 31, 37, 43, 48, 47, 38, 71, 56, 53 ),
        'JHN': ( 21, 51, 25, 36, 54, 47, 71, 53, 59, 41, 42, 57, 50, 38, 31, 27, 33, 26, 40, 42, 31, 25 ),
        'ACT': ( 28, 26, 47, 26, 37, 42, 15, 60, 40, 43, 48, 30, 25, 52, 28, 41, 40, 34, 28, 40, 38, 40, 30, 35, 27, 27, 32, 44, 31 ), # Different from English Protestant at ch 19
        'ROM': ( 16, 32, 29, 31, 25, 21, 23, 25, 39, 33, 21, 36, 21, 14, 23, 33, 27 ),
        '1CO': ( 16, 31, 16, 23, 21, 13, 20, 40, 13, 27, 33, 34, 31, 13, 40, 58, 24 ),
        '2CO': ( 13, 24, 17, 18, 18, 21, 18, 16, 24, 15, 18, 33, 21, 13 ), # Different from English Protestant at ch 13
        'GAL': ( 6, 24, 21, 29, 31, 26, 18 ),
        'EPH': ( 6, 23, 22, 21, 32, 33, 24 ),
        'PHP': ( 4, 30, 30, 21, 23 ),
        'COL': ( 4, 29, 23, 25, 18 ),
        '1TH': ( 5, 10, 20, 13, 18, 28 ),
        '2TH': ( 3, 12, 17, 18 ),
        '1TI': ( 6, 20, 15, 16, 16, 25, 21 ),
        '2TI': ( 4, 18, 26, 17, 22 ),
        'TIT': ( 3, 16, 15, 15 ),
        'PHM': ( 1, 25 ),
        'HEB': ( 13, 14, 18, 19, 16, 14, 20, 28, 13, 28, 39, 40, 29, 25 ),
        'JAS': ( 5, 27, 26, 18, 17, 20 ),
        '1PE': ( 5, 25, 25, 22, 19, 14 ),
        '2PE': ( 3, 21, 22, 18 ),
        '1JN': ( 5, 10, 29, 24, 21, 21 ),
        '2JN': ( 1, 13 ),
        '3JN': ( 1, 15 ), # Different from English Protestant
        'JUD': ( 1, 25 ),
        'REV': ( 22, 20, 29, 22, 11, 14, 17, 17, 13, 21, 11, 19, 18, 18, 20, 8, 21, 18, 24, 21, 15, 27, 21 ), # Different from English Protestant at ch 12
        },
    'EnglishProtestantSystem' : {
        'GEN': ( 50, 31, 25, 24, 26, 32, 22, 24, 22, 29, 32, 32, 20, 18, 24, 21, 16, 27, 33, 38, 18, 34, 24, 20, 67, 34, 35, 46, 22, 35, 43, 55, 32, 20, 31, 29, 43, 36, 30, 23, 23, 57, 38, 34, 34, 28, 34, 31, 22, 33, 26 ),
        'EXO': ( 40, 22, 25, 22, 31, 23, 30, 25, 32, 35, 29, 10, 51, 22, 31, 27, 36, 16, 27, 25, 26, 36, 31, 33, 18, 40, 37, 21, 43, 46, 38, 18, 35, 23, 35, 35, 38, 29, 31, 43, 38 ),
        'LEV': ( 27, 17, 16, 17, 35, 19, 30, 38, 36, 24, 20, 47, 8, 59, 57, 33, 34, 16, 30, 37, 27, 24, 33, 44, 23, 55, 46, 34 ),
        'NUM': ( 36, 54, 34, 51, 49, 31, 27, 89, 26, 23, 36, 35, 16, 33, 45, 41, 50, 13, 32, 22, 29, 35, 41, 30, 25, 18, 65, 23, 31, 40, 16, 54, 42, 56, 29, 34, 13 ),
        'DEU': ( 34, 46, 37, 29, 49, 33, 25, 26, 20, 29, 22, 32, 32, 18, 29, 23, 22, 20, 22, 21, 20, 23, 30, 25, 22, 19, 19, 26, 68, 29, 20, 30, 52, 29, 12 ),
        'JOS': ( 24, 18, 24, 17, 24, 15, 27, 26, 35, 27, 43, 23, 24, 33, 15, 63, 10, 18, 28, 51, 9, 45, 34, 16, 33 ),
        'JDG': ( 21, 36, 23, 31, 24, 31, 40, 25, 35, 57, 18, 40, 15, 25, 20, 20, 31, 13, 31, 30, 48, 25 ),
        'RUT': ( 4, 22, 23, 18, 22 ),
        '1SA': ( 31, 28, 36, 21, 22, 12, 21, 17, 22, 27, 27, 15, 25, 23, 52, 35, 23, 58, 30, 24, 42, 15, 23, 29, 22, 44, 25, 12, 25, 11, 31, 13 ),
        '2SA': ( 24, 27, 32, 39, 12, 25, 23, 29, 18, 13, 19, 27, 31, 39, 33, 37, 23, 29, 33, 43, 26, 22, 51, 39, 25 ),
        '1KI': ( 22, 53, 46, 28, 34, 18, 38, 51, 66, 28, 29, 43, 33, 34, 31, 34, 34, 24, 46, 21, 43, 29, 53 ),
        '2KI': ( 25, 18, 25, 27, 44, 27, 33, 20, 29, 37, 36, 21, 21, 25, 29, 38, 20, 41, 37, 37, 21, 26, 20, 37, 20, 30 ),
        '1CH': ( 29, 54, 55, 24, 43, 26, 81, 40, 40, 44, 14, 47, 40, 14, 17, 29, 43, 27, 17, 19, 8, 30, 19, 32, 31, 31, 32, 34, 21, 30 ),
        '2CH': ( 36, 17, 18, 17, 22, 14, 42, 22, 18, 31, 19, 23, 16, 22, 15, 19, 14, 19, 34, 11, 37, 20, 12, 21, 27, 28, 23, 9, 27, 36, 27, 21, 33, 25, 33, 27, 23 ),
        'EZR': ( 10, 11, 70, 13, 24, 17, 22, 28, 36, 15, 44 ),
        'NEH': ( 13, 11, 20, 32, 23, 19, 19, 73, 18, 38, 39, 36, 47, 31 ),
        'EST': ( 10, 22, 23, 15, 17, 14, 14, 10, 17, 32, 3 ),
        'JOB': ( 42, 22, 13, 26, 21, 27, 30, 21, 22, 35, 22, 20, 25, 28, 22, 35, 22, 16, 21, 29, 29, 34, 30, 17, 25, 6, 14, 23, 28, 25, 31, 40, 22, 33, 37, 16, 33, 24, 41, 30, 24, 34, 17 ),
        'PSA': ( 150, 6, 12, 8, 8, 12, 10, 17, 9, 20, 18, 7, 8, 6, 7, 5, 11, 15, 50, 14, 9, 13, 31, 6, 10, 22, 12, 14, 9, 11, 12, 24, 11, 22, 22, 28, 12, 40, 22, 13, 17, 13, 11, 5, 26, 17, 11, 9, 14, 20, 23, 19, 9, 6, 7, 23, 13, 11, 11, 17, 12, 8, 12, 11, 10, 13, 20, 7, 35, 36, 5, 24, 20, 28, 23, 10, 12, 20, 72, 13, 19, 16, 8, 18, 12, 13, 17, 7, 18, 52, 17, 16, 15, 5, 23, 11, 13, 12, 9, 9, 5, 8, 28, 22, 35, 45, 48, 43, 13, 31, 7, 10, 10, 9, 8, 18, 19, 2, 29, 176, 7, 8, 9, 4, 8, 5, 6, 5, 6, 8, 8, 3, 18, 3, 3, 21, 26, 9, 8, 24, 13, 10, 7, 12, 15, 21, 10, 20, 14, 9, 6 ),
        'PRO': ( 31, 33, 22, 35, 27, 23, 35, 27, 36, 18, 32, 31, 28, 25, 35, 33, 33, 28, 24, 29, 30, 31, 29, 35, 34, 28, 28, 27, 28, 27, 33, 31 ),
        'ECC': ( 12, 18, 26, 22, 16, 20, 12, 29, 17, 18, 20, 10, 14 ),
        'SNG': ( 8, 17, 17, 11, 16, 16, 13, 13, 14 ),
        'ISA': ( 66, 31, 22, 26, 6, 30, 13, 25, 22, 21, 34, 16, 6, 22, 32, 9, 14, 14, 7, 25, 6, 17, 25, 18, 23, 12, 21, 13, 29, 24, 33, 9, 20, 24, 17, 10, 22, 38, 22, 8, 31, 29, 25, 28, 28, 25, 13, 15, 22, 26, 11, 23, 15, 12, 17, 13, 12, 21, 14, 21, 22, 11, 12, 19, 12, 25, 24 ),
        'JER': ( 52, 19, 37, 25, 31, 31, 30, 34, 22, 26, 25, 23, 17, 27, 22, 21, 21, 27, 23, 15, 18, 14, 30, 40, 10, 38, 24, 22, 17, 32, 24, 40, 44, 26, 22, 19, 32, 21, 28, 18, 16, 18, 22, 13, 30, 5, 28, 7, 47, 39, 46, 64, 34 ),
        'LAM': ( 5, 22, 22, 66, 22, 22 ),
        'EZK': ( 48, 28, 10, 27, 17, 17, 14, 27, 18, 11, 22, 25, 28, 23, 23, 8, 63, 24, 32, 14, 49, 32, 31, 49, 27, 17, 21, 36, 26, 21, 26, 18, 32, 33, 31, 15, 38, 28, 23, 29, 49, 26, 20, 27, 31, 25, 24, 23, 35 ),
        'DAN': ( 12, 21, 49, 30, 37, 31, 28, 28, 27, 27, 21, 45, 13 ),
        'HOS': ( 14, 11, 23, 5, 19, 15, 11, 16, 14, 17, 15, 12, 14, 16, 9 ),
        'JOL': ( 3, 20, 32, 21 ),
        'AMO': ( 9, 15, 16, 15, 13, 27, 14, 17, 14, 15 ),
        'OBA': ( 1, 21 ),
        'JON': ( 4, 17, 10, 10, 11 ),
        'MIC': ( 7, 16, 13, 12, 13, 15, 16, 20 ),
        'NAM': ( 3, 15, 13, 19 ),
        'HAB': ( 3, 17, 20, 19 ),
        'ZEP': ( 3, 18, 15, 20 ),
        'HAG': ( 2, 15, 23 ),
        'ZEC': ( 14, 21, 13, 10, 14, 11, 15, 14, 23, 17, 12, 17, 14, 9, 21 ),
        'MAL': ( 4, 14, 17, 18, 6 ),
        'MAT': ( 28, 25, 23, 17, 25, 48, 34, 29, 34, 38, 42, 30, 50, 58, 36, 39, 28, 27, 35, 30, 34, 46, 46, 39, 51, 46, 75, 66, 20 ),
        'MRK': ( 16, 45, 28, 35, 41, 43, 56, 37, 38, 50, 52, 33, 44, 37, 72, 47, 20 ),
        'LUK': ( 24, 80, 52, 38, 44, 39, 49, 50, 56, 62, 42, 54, 59, 35, 35, 32, 31, 37, 43, 48, 47, 38, 71, 56, 53 ),
        'JHN': ( 21, 51, 25, 36, 54, 47, 71, 53, 59, 41, 42, 57, 50, 38, 31, 27, 33, 26, 40, 42, 31, 25 ),
        'ACT': ( 28, 26, 47, 26, 37, 42, 15, 60, 40, 43, 48, 30, 25, 52, 28, 41, 40, 34, 28, 41, 38, 40, 30, 35, 27, 27, 32, 44, 31 ),
        'ROM': ( 16, 32, 29, 31, 25, 21, 23, 25, 39, 33, 21, 36, 21, 14, 23, 33, 27 ),
        '1CO': ( 16, 31, 16, 23, 21, 13, 20, 40, 13, 27, 33, 34, 31, 13, 40, 58, 24 ),
        '2CO': ( 13, 24, 17, 18, 18, 21, 18, 16, 24, 15, 18, 33, 21, 14 ),
        'GAL': ( 6, 24, 21, 29, 31, 26, 18 ),
        'EPH': ( 6, 23, 22, 21, 32, 33, 24 ),
        'PHP': ( 4, 30, 30, 21, 23 ),
        'COL': ( 4, 29, 23, 25, 18 ),
        '1TH': ( 5, 10, 20, 13, 18, 28 ),
        '2TH': ( 3, 12, 17, 18 ),
        '1TI': ( 6, 20, 15, 16, 16, 25, 21 ),
        '2TI': ( 4, 18, 26, 17, 22 ),
        'TIT': ( 3, 16, 15, 15 ),
        'PHM': ( 1, 25 ),
        'HEB': ( 13, 14, 18, 19, 16, 14, 20, 28, 13, 28, 39, 40, 29, 25 ),
        'JAS': ( 5, 27, 26, 18, 17, 20 ),
        '1PE': ( 5, 25, 25, 22, 19, 14 ),
        '2PE': ( 3, 21, 22, 18 ),
        '1JN': ( 5, 10, 29, 24, 21, 21 ),
        '2JN': ( 1, 13 ),
        '3JN': ( 1, 14 ),
        'JUD': ( 1, 25 ),
        'REV': ( 22, 20, 29, 22, 11, 14, 17, 17, 13, 21, 11, 19, 17, 18, 20, 8, 21, 18, 24, 21, 15, 27, 21 ),
        },
    }


class BibleChaptersVerses:
    """
    Class for creating and manipulating Bible book name objects.
    """

    def __init__( self, systemName ):
        self.load( systemName )

    def __str__( self ):
        """
        This method returns the string representation of a Bible object.
        
        @return: the name of a Bible object formatted as a string
        @rtype: string
        """
        result = ""
        if self.systemName: result += ('\n' if result else '') + self.systemName
        return result

    def load( self, systemName ):
        self.BBBDict = {}
        self.systemName = systemName
        if systemName in builtinSystems:
            for BBB, figures in builtinSystems[systemName].items():
                assert( len(figures) >= 2 )
                assert( len(figures) == figures[0] + 1 )
                self.BBBDict[BBB] = figures
            return True
        else:
            self.systemName = None
            logging.error( "Sorry, this program doesn't handle the '%s' system for Bible chapter and verse counts yet." % systemName )
            return False
    # end of load

    def getNumChapters( self, BBB ):
        assert( BBB )
        assert( self.systemName is not None )
        assert( BBB in self.BBBDict )
        return self.BBBDict[BBB][0]
    # end of getNumChapters

    def getNumVerses( self, BBB, C ):
        assert( BBB )
        assert( self.systemName is not None )
        assert( BBB in self.BBBDict )
        assert( C )
        if isinstance( C, str ):
            assert( C.isdigit() )
            C = int( C )
        assert( 1 <= C <= self.BBBDict[BBB][0] )
        return self.BBBDict[BBB][C]
    # end of getNumVerses

    def CVValid( self, BBB, C, V ):
        """
        Returns True or False
        """
        assert( BBB )
        assert( self.systemName is not None )
        assert( BBB in self.BBBDict )
        numC = self.getNumChapters( BBB )
        if isinstance( C, str ):
            assert( C.isdigit() )
            C = int( C )
        if ( C<1  or C>numC): return False
        numV = self.getNumVerses( BBB, C )
        if isinstance( V, str ):
            assert( V.isdigit() )
            V = int( V )
        if ( V<1 or V>numV ): return False
        return True
    # end of CVValid

    def CVValidWithErrorMsgs( self, BBB, C, V, referenceString="(unknown)" ):
        """
        Returns True or False
        """
        assert( self.systemName is not None )
        if not BBB:
            logging.error( "Missing book name in Bible reference '%s'" % ( referenceString ) )
            return False
        if BBB not in self.BBBDict:
            logging.error( "Invalid '%s' book name in Bible reference '%s'" % ( BBB, referenceString ) )
            return False
        haveErrors = False
        numC = self.getNumChapters( BBB )
        if isinstance( C, str ):
            assert( C.isdigit() )
            C = int( C )
        if ( C<1 ):
            logging.error( "Invalid chapter number '%i' in Bible reference '%s'" % ( C, referenceString ) )
            haveErrors = True
        elif ( C>numC ):
            logging.error( "Chapter number '%i' too large for '%s' in Bible reference '%s'" % ( C, BBB, referenceString ) )
            haveErrors = True
        else:
            numV = self.getNumVerses( BBB, C )
            if isinstance( V, str ):
                if V[-1] in ('a','b','c','d','e'): # Could be something like verse 5a
                    V = V[:-1]
                #assert( V.isdigit() )
                if not V.isdigit():
                    logging.error( "Invalid verse number '%s' in Bible reference '%s'" % ( V, referenceString ) )
                V = int( V )
            if ( V<1 ):
                logging.error( "Invalid verse number '%i' in Bible reference '%s'" % ( V, referenceString ) )
                haveErrors = True
            elif ( V>numV ):
                logging.error( "Verse number '%i' too large for '%s %i' in Bible reference '%s'" % ( V, BBB, C, referenceString ) )
                haveErrors = True
        return not haveErrors
    # end of CVValidWithErrorMsgs

    def expandCVRangeWithErrorMsgs( self, startRef, endRef, referenceString="(unknown)" ):
        """
        Accepts two references which form part of a range

        Returns a list of single references.
        """
        assert( startRef and endRef )
        assert( len(startRef)==3 and len(endRef)==3 ) # BBB, C, V (all strings)
        assert( startRef[0] == endRef[0] ) # Assume that the book codes are identical

        haveErrors, haveWarnings = False, False
        BBB1, C1str, V1str = startRef
        BBB2, C2str, V2str = endRef
        if not self.CVValidWithErrorMsgs( BBB1, C1str, V1str, referenceString ):
            haveErrors = True
        if not self.CVValidWithErrorMsgs( BBB2, C2str, V2str, referenceString ):
            haveErrors = True
        if V1str[-1] in ('a','b','c','d','e'): # Could be something like verse 5a
            V1str = V1str[:-1]
        if V2str[-1] in ('a','b','c','d','e'): # Could be something like verse 5a
            V2str = V2str[:-1]
        C1,V1 = int(C1str), int(V1str)
        C2,V2 = int(C2str), int(V2str)
        if C1 > C2:
            logging.error( "Chapter range out of order (%s before %s) in %s Bible reference '%s'" % ( C1str, C2str, BBB1, referenceString ) )
            haveErrors = True
        elif C1==C2 and V1>=V2:
            logging.error( "Verse range out of order (%s before %s) in %s %s Bible reference '%s'" % ( V1str, V2str, BBB1, C1str, referenceString ) )
            haveErrors = True

        resultList = []
        for C in range( C1, C2+1 ):
            if C==C1 and C==C2: # We're on the only chapter
                startV = V1
                endV = V2
            elif C==C1: # We're on the first chapter
                startV = V1
                endV = self.getNumVerses( BBB1, C )
            elif C==C2: # We're on the final chapter
                startV = 1
                endV = V2
            else: # Must be an inbetween chapter
                startV = 1
                endV = self.getNumVerses( BBB1, C )
            for V in range( startV, endV+1 ):
                resultList.append( (BBB1, str(C), str(V)) )

        #print( startRef, endRef, resultList, haveErrors, haveWarnings )
        return resultList, haveErrors, haveWarnings
    # end of expandCVRangeWithErrorMsgs

    def export( self ):
        """Export data to XML"""
        filename = "BibleChaptersVerses-%s.xml.output" % (self.systemName)
        print( "Exporting %s..." % ( filename ) )
        with open( filename, 'wt' ) as myFile:
            myFile.write( "%s\n" % ( self.systemName ) )
            for BBB in self.BBBDict:
                myFile.write( "%s\n" % ( BBB ) )
                numChapters = self.BBBDict[BBB][0]
                myFile.write( "    <numChapters>%i</numChapters>\n" % ( numChapters ) )
                for chapter in range(1,numChapters+1):
                    myFile.write( '    <numVerses chapter="%i">%i</numVerses>\n' % ( chapter, self.BBBDict[BBB][chapter] ) )
    # end of export
# end of class BibleChaptersVerses


def demo():
    """Demonstrate reading and processing some Bible book names.
    """
    bcv = BibleChaptersVerses( "EnglishProtestantSystem" )
    print( bcv )
    print( bcv.getNumChapters('MAT'), bcv.getNumChapters('PHM') )
    print( bcv.getNumVerses('MAT','1'), bcv.getNumVerses('MAT','28'), bcv.getNumVerses('PHM','1') )
    print( bcv.CVValidWithErrorMsgs('MAT','1','1','Mat. 1:1'), bcv.CVValidWithErrorMsgs('MAT','1','10','Mat. 1:10'), bcv.CVValidWithErrorMsgs('MAT','1','25','Mat. 1:25') )
    print( bcv.CVValidWithErrorMsgs('MAT','0','1','Mat. 0:1'), bcv.CVValidWithErrorMsgs('MAT','29','1','Mat. 29:1'), bcv.CVValidWithErrorMsgs('MAT','1','0','Mat. 1:0'), bcv.CVValidWithErrorMsgs('MAT','1','26','Mat. 1:26') )
    # Now using integers instead of strings for C V
    print( bcv.getNumVerses('MAT',1), bcv.getNumVerses('MAT',28), bcv.getNumVerses('PHM',1) )
    print( bcv.CVValidWithErrorMsgs('MAT',1,1,'Mat. 1:1'), bcv.CVValidWithErrorMsgs('MAT',1,10,'Mat. 1:10'), bcv.CVValidWithErrorMsgs('MAT',1,25,'Mat. 1:25') )
    print( bcv.CVValidWithErrorMsgs('MAT',0,1,'Mat. 0:1'), bcv.CVValidWithErrorMsgs('MAT',29,1,'Mat. 29:1'), bcv.CVValidWithErrorMsgs('MAT',1,0,'Mat. 1:0'), bcv.CVValidWithErrorMsgs('MAT',1,26,'Mat. 1:26') )

    bcv = BibleChaptersVerses( "OriginalLanguageSystem" )
    bcv.export()

    bcv = BibleChaptersVerses( "EnglishProtestantSystem" )
    bcv.export()

if __name__ == '__main__':
    demo()
# end of BibleChaptersVerses.py
