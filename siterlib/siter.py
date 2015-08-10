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
from siterlib.file import FileMode, Dirs, Files
from siterlib.tokenizer import Tokenizer
from siterlib.bindings import Bindings

class Imports:
    def __init__(self):
        self.Md = Util.try_import('markdown')
        self.Pygments = Util.try_import('pygments')
        self.PygmentsLexers = Util.try_import('pygments.lexers')
        self.PygmentsFormatters = Util.try_import('pygments.formatters')

class Settings:
    def __init__(self, argv, files):
        # Whether to re-generate up-to-date files
        self.ForceWrite = False

        # Blocks that start with this are evaluated; must be exactly 1 char
        self.EvalHint = '`'

        # Block delimiters
        self.TagOpen = '{'
        self.TagClose = '}'

        # Marks the beginning of page content
        self.Marker = '~~~'

        # Load user settings
        self.from_args(argv)
        self.from_files(files)

    def from_args(self, argv):
        # Go through command line arguments
        for arg in argv:
            if arg == '-f' or arg == '--force':
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

        if files.marker.test_line(0, 1):
            self.Marker = files.marker.get_line(0)

class Siter:
    def __init__(self, argv):
        # Declare and optionally create the dirs and files Siter uses
        self.dirs = Dirs()
        self.files = Files(self.dirs)

        # Set defaults and load user settings from args and config files
        self.settings = Settings(argv, self.files)

        # Optional packages
        self.imports = Imports()

        # Token processing utilities
        self.tokenizer = Tokenizer(self.settings, self.imports)

        # Copy site and template media files
        self.dirs.media.copy_to(self.dirs.out_media)
        self.dirs.template_media.copy_to(self.dirs.out_template_media)

        # Global function and variable bindings
        self.bindings = Bindings(self.settings, self.tokenizer)
        self.bindings.set_from_file(self.files.defs)

    def __apply_template(self, template_file, bindings):
        tokens = self.tokenizer.tokenize(template_file.get_content())
        tokens = self.tokenizer.evaluate(tokens, bindings)

        return ''.join([t.resolve() for t in tokens])

    def run(self, read_dir = None, write_dir = None):
        if read_dir is None:
            read_dir = self.dirs.pages

        if write_dir is None:
            write_dir = self.dirs.out

        for in_file in read_dir.list_files():
            out_file = write_dir.add_file(in_file.get_name(), FileMode.Create)

            if self.settings.ForceWrite is False and in_file.older_than(out_file):
                Util.message('Up to date', out_file.get_path())
                continue

            Util.message('Updating', out_file.get_path())

            #   global bindings from the defs file
            # + bindings declared by the current page file
            # + siter built-in bindings
            self.bindings.push()
            self.bindings.set_from_file(in_file)
            self.bindings.set_builtin(in_file, read_dir, self.dirs)

            # Load template and replace variables and functions with bindings
            final = self.__apply_template(self.files.page_html, self.bindings)
            out_file.write(final)

            self.bindings.pop()

        for read_subdir in read_dir.list_dirs():
            write_subdir = write_dir.add_dir(read_subdir.get_name(), FileMode.Create)
            self.run(read_subdir, write_subdir)
