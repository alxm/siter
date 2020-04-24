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

import enum
import os
import shutil

from siterlib.util import CUtil

class CFileMode(enum.Enum):
    Optional = 0
    Create = 1
    Required = 2

class CFile:
    def __init__(self, Path, Mode):
        self.path = os.path.abspath(Path)
        self.mode = Mode

        if self.mode is CFileMode.Required and not self.exists():
            CUtil.error(f'Required file {self.path} not found')

    def exists(self):
        return os.path.exists(self.path)

    def get_path(self):
        return self.path

    def get_name(self):
        return os.path.basename(self.path)

    def get_mod_time(self):
        return os.stat(self.path).st_mtime

class CDir(CFile):
    def __init__(self, Path, Mode, ReadContents = False):
        CFile.__init__(self, Path, Mode)

        self.files = {}
        self.dirs = {}

        if self.mode is CFileMode.Create:
            os.makedirs(self.path, exist_ok = True)

        if not self.exists() or not ReadContents:
            return

        for Path in [os.path.join(self.path, p) for p in os.listdir(self.path)]:
            if os.path.isfile(Path):
                self.files[Path] = CTextFile(Path, CFileMode.Required)
            elif os.path.isdir(Path):
                self.dirs[Path] = CDir(Path, CFileMode.Required, True)
            else:
                CUtil.error(f'Invalid file {Path}')

    def get_dirs(self):
        return self.dirs.values()

    def get_files(self):
        return self.files.values()

    def add_dir(self, SubDir, Mode):
        path = os.path.join(self.path, SubDir)

        if path not in self.dirs:
            self.dirs[path] = CDir(path, Mode)

        return self.dirs[path]

    def add_file(self, Name, Mode):
        path = os.path.join(self.path, Name)

        if path not in self.files:
            self.files[path] = CTextFile(path, Mode)

        return self.files[path]

    def path_to(self, Target):
        return os.path.relpath(Target.get_path(), start = self.path)

    def copy_to(self, DstDir):
        src = self.path
        dst = DstDir.path

        CUtil.message('Copy files', f'From {src} to {dst}')

        shutil.rmtree(dst)
        shutil.copytree(src, dst)

class CTextFile(CFile):
    def __init__(self, Path, Mode):
        CFile.__init__(self, Path, Mode)

        self.content = None
        self.lines = None

        if self.mode is not CFileMode.Create:
            try:
                with open(self.path, 'rU') as f:
                    self.content = f.read()
            except FileNotFoundError:
                if self.mode is not CFileMode.Optional:
                    CUtil.error(f'Required file {self.path} not found')

    def test_line(self, Number, MinLen = None, MaxLen = None):
        if self.content is None:
            return False

        error = None
        line = self.get_line(Number)

        if line is None:
            error = f'{self.path}:{Number} line not found'
        else:
            if MinLen and len(line) < MinLen:
                error = f'{self.path}:{Number} length must be at least ' \
                        f'{MinLen}, is {len(line)}: "{line}"'
            elif MaxLen and len(line) > MaxLen:
                error = f'{self.path}:{Number} length must not exceed ' \
                        f'{MaxLen}, is {len(line)}: "{line}"'

        if error:
            if self.mode is CFileMode.Optional:
                CUtil.warning(error)
            else:
                CUtil.error(error)

            return False

        return True

    def get_line(self, Number):
        if self.lines is None:
            self.lines = self.content.splitlines()

        if Number < len(self.lines):
            return self.lines[Number].strip()

        return None

    def get_content(self):
        return self.content

    def write(self, Text):
        with open(self.path, 'w') as f:
            f.write(Text)

class CDirs:
    def __init__(self):
        self.pages = CDir('siter-pages', CFileMode.Required, True)
        self.template = CDir('siter-template', CFileMode.Required)
        self.config = CDir('siter-config', CFileMode.Optional)
        self.static = CDir('siter-static', CFileMode.Optional)
        self.stubs = CDir('siter-stubs', CFileMode.Optional, True)
        self.out = CDir('siter-out', CFileMode.Create)

class CFiles:
    def __init__(self, Dirs):
        self.defs = Dirs.config.add_file('defs', CFileMode.Optional)
        self.evalhint = Dirs.config.add_file('eval', CFileMode.Optional)
        self.tags = Dirs.config.add_file('tags', CFileMode.Optional)
        self.page_html = Dirs.template.add_file('page.html', CFileMode.Optional)
