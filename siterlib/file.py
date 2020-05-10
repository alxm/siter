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

import enum, os, shutil

from .settings import *
from .tokenizer import *
from .util import *

class CFileMode(enum.Enum):
    Optional = 0
    Create = 1
    Required = 2
    Reset = 3

class CFile:
    def __init__(self, Path, Mode):
        self.path = os.path.abspath(Path)
        self.shortpath = os.path.relpath(Path, start = os.curdir)
        self.name = os.path.basename(Path)
        self.mode = Mode

        if self.mode is CFileMode.Required and not self.exists():
            CUtil.error(f'Required file {self.path} not found')

    def exists(self):
        return os.path.exists(self.path)

    def get_mod_time(self):
        return os.stat(self.path).st_mtime

class CDir(CFile):
    def __init__(self, Path, Mode, ReadContents, AllowedExtension):
        CFile.__init__(self, Path, Mode)

        self.files = {}
        self.dirs = {}

        if self.mode is CFileMode.Create:
            os.makedirs(self.path, exist_ok = True)
        elif self.mode is CFileMode.Reset:
            if self.exists():
                shutil.rmtree(self.path)

            os.makedirs(self.path)

        if not self.exists() or not ReadContents:
            return

        for rootdir, dirs, files in os.walk(self.path):
            self.dirs[rootdir] = []

            for f in filter(lambda f: f.endswith(AllowedExtension), files):
                full_path = os.path.join(rootdir, f)
                text_file = CTextFile(full_path, CFileMode.Required)

                self.files[full_path] = text_file
                self.dirs[rootdir].append(text_file)

    def get_dir_files(self, RelDirPath):
        path = os.path.join(self.path, RelDirPath)

        try:
            return self.dirs[path]
        except KeyError:
            CUtil.error(f'Dir {path} not found')

    def get_files(self):
        return self.files.values()

    def get_file(self, Name):
        path = os.path.join(self.path, Name)

        try:
            return self.files[path]
        except KeyError:
            CUtil.error(f'File {path} not found')

    def path_to(self, Target):
        return os.path.relpath(Target.path, start = self.path)

    def copy_to(self, DstDir):
        CUtil.message('Copy files',
                      f'From {self.shortpath} to {DstDir.shortpath}')

        shutil.rmtree(DstDir.path)
        shutil.copytree(self.path, DstDir.path)

    def replace(self, DstDir):
        CUtil.message('Move files',
                      f'From {self.shortpath} to {DstDir.shortpath}')

        if DstDir.exists():
            shutil.rmtree(DstDir.path)

        os.replace(self.path, DstDir.path)

class CTextFile(CFile):
    def __init__(self, Path, Mode):
        CFile.__init__(self, Path, Mode)
        CUtil.message('Load', self.shortpath)

        with open(self.path, 'rU') as f:
            self.tokens = CTokenizer.tokenize(f.read())

    def path_to(self, Target):
        return os.path.relpath(Target.path, start = os.path.dirname(self.path))

    def write(self, Text, WriteRoot, ReadRoot):
        out_dir = os.path.join(WriteRoot.path,
                               os.path.dirname(ReadRoot.path_to(self)))
        no_ext_name, _ = os.path.splitext(self.name)

        os.makedirs(out_dir, exist_ok = True)

        with open(os.path.join(out_dir, f'{no_ext_name}.html'), 'w') as f:
            f.write(Text)

class CDirs:
    __index = {
        CSettings.DirPages: (CFileMode.Required, True, '.md'),
        CSettings.DirTemplate: (CFileMode.Required, True, ''),

        CSettings.DirConfig: (CFileMode.Optional, True, ''),
        CSettings.DirStatic: (CFileMode.Optional, False, ''),
        CSettings.DirStubs: (CFileMode.Optional, True, ''),

        CSettings.DirOut: (CFileMode.Create, False, ''),
        CSettings.DirStaging: (CFileMode.Reset, False, ''),
    }

    def __init__(self):
        self.dirs = {}

        for dir_entry in CDirs.__index:
            mode, read, allowed_ext = CDirs.__index[dir_entry]
            self.dirs[dir_entry] = CDir(dir_entry, mode, read, allowed_ext)

        self.config = self.dirs[CSettings.DirConfig]
        self.out = self.dirs[CSettings.DirOut]
        self.pages = self.dirs[CSettings.DirPages]
        self.staging = self.dirs[CSettings.DirStaging]
        self.static = self.dirs[CSettings.DirStatic]
        self.stubs = self.dirs[CSettings.DirStubs]
        self.template = self.dirs[CSettings.DirTemplate]

    @staticmethod
    def new_project(Path):
        if os.path.exists(Path):
            CUtil.error(f'{Path} already exists')

        CUtil.info(f'Creating new project at {Path}')

        os.makedirs(Path)
        os.chdir(Path)

        for dir_entry in CDirs.__index:
            mode = CDirs.__index[dir_entry][0]

            if mode is CFileMode.Required:
                os.makedirs(dir_entry)

        def write(Dir, File, Content):
            with open(os.path.join(Dir, File), 'w') as f:
                f.write(Content)

        write(CSettings.DirTemplate, CSettings.TemplatePage, """\
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="generator" content="Siter">
        <title>Default Siter Template</title>
    </head>
    <body>
        {{!md {{!content}}}}
    </body>
</html>
""")

        write(CSettings.DirPages, 'index.md', """\
*Hello World!*
""")
