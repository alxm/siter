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

from siterlib.util import CUtil

class CSettings:
    def __init__(self):
        # Blocks that start with this are evaluated; must be exactly 1 char
        self.EvalHint = '!'

        # Block delimiters
        self.TagOpen = '{{'
        self.TagClose = '}}'

        # Macro args following this delimiter are optional
        self.OptDelimiter = '/'

        # Built-in binding names
        self.Def = 'def'
        self.If = 'if'
        self.Content = 'content'
        self.Modified = 'modified'
        self.Generated = 'generated'
        self.Datefmt = 'datefmt'
        self.Root = 'root'
        self.Code = 'code'
        self.Markdown = 'md'
        self.Anchor = 'anchor'
        self.Apply = 'apply'

        self.PygmentsDiv = 'siter_code'
