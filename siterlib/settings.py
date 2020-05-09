"""
    Copyright 2011 Alex Margarit

    This file is part of Siter, a static website generator.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

class CSettings:
    # Project dirs
    DirConfig = 'siter-config'
    DirOut = 'siter-out'
    DirPages = 'siter-pages'
    DirStaging = 'siter-staging'
    DirStatic = 'siter-static'
    DirStubs = 'siter-stubs'
    DirTemplate = 'siter-template'

    # Blocks that start with this are evaluated; must be exactly 1 char
    EvalHint = '!'

    # Block delimiters
    TagOpen = '{{'
    TagClose = '}}'

    # Macro args following this delimiter are optional
    OptDelimiter = '/'

    # Built-in binding names
    Def = 'def'
    If = 'if'
    Content = 'content'
    Modified = 'modified'
    Generated = 'generated'
    Datefmt = 'datefmt'
    Root = 'root'
    Code = 'code'
    Markdown = 'md'
    Anchor = 'anchor'
    Apply = 'apply'

    # HTML container class for highlighted code
    PygmentsDiv = 'siter_code'
