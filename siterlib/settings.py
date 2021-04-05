"""
    Copyright 2011 Alex Margarit
    This file is part of Siter, a static website generator.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License version 3,
    as published by the Free Software Foundation.

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
    TemplatePage = 'page.html'

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
    Markdown = 'md'
    Anchor = 'anchor'
    Stubs = 'stubs'

    # HTML container class for highlighted code
    PygmentsDiv = 'siter_code'

    # TocExtension title text
    TocTitle = 'Contents'

    # Text content for header permalinks
    HeaderLink = '#'
