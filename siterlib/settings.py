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

from siterlib.util import Util

class Settings:
    def __init__(self, argv, files):
        # Whether to re-generate up-to-date files
        self.ForceWrite = False

        # Blocks that start with this are evaluated; must be exactly 1 char
        self.EvalHint = '`'

        # Block delimiters
        self.TagOpen = '{'
        self.TagClose = '}'

        # Built-in binding names
        self.Def = 'def'
        self.If = 'if'
        self.Content = 'content'
        self.Modified = 'modified'
        self.Generated = 'generated'
        self.Root = 'root'
        self.Code = 'code'

        # Load user settings
        self.from_args(argv)
        self.from_files(files)

    def from_args(self, argv):
        # Go through command line arguments
        for arg in argv:
            if arg in ['-f', '--force']:
                self.ForceWrite = True

    def from_files(self, files):
        if files.evalhint.test_line(0, 1, 1):
            self.EvalHint = files.evalhint.get_line(0)
            Util.info('Using {} as block eval hint'.format(self.EvalHint))

        if files.tags.test_line(0, 1) and files.tags.test_line(1, 1):
            self.TagOpen = files.tags.get_line(0)
            self.TagClose = files.tags.get_line(1)

            Util.info('Using {} and {} as block tags'
                .format(self.TagOpen, self.TagClose))
