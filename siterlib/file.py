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
        self.name_noext, _ = os.path.splitext(self.name)
        self.mode = Mode

        if self.mode is CFileMode.Required and not os.path.exists(self.path):
            CUtil.error(f'Required file {self.path} not found')

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
            try:
                shutil.rmtree(self.path)
            except FileNotFoundError:
                pass

            os.makedirs(self.path)

        if ReadContents:
            for rootdir, _, files in os.walk(self.path):
                self.dirs[rootdir] = []

                for f in filter(lambda f: f.endswith(AllowedExtension), files):
                    full_path = os.path.join(rootdir, f)
                    text_file = CTextFile(Path, full_path, CFileMode.Required)

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

        try:
            shutil.copytree(self.path, DstDir.path)
        except FileNotFoundError:
            pass

    def replace(self, DstDir):
        CUtil.message('Move', f'From {self.shortpath} to {DstDir.shortpath}')

        shutil.rmtree(DstDir.path)
        os.replace(self.path, DstDir.path)

class CTextFile(CFile):
    def __init__(self, Prefix, Path, Mode):
        CFile.__init__(self, Path, Mode)
        CUtil.message('Load', self.shortpath)

        path_public, _ = os.path.splitext(os.path.relpath(Path, start = Prefix))
        self.path_public = f'{path_public}.html'

        with open(self.path, 'rU') as f:
            self.tokens = CTokenizer.tokenize(f.read())

    def path_to(self, Target):
        return os.path.relpath(Target.path, start = os.path.dirname(self.path))

    def write(self, Text, WriteRoot, ReadRoot):
        out_dir = os.path.join(WriteRoot.path,
                               os.path.dirname(ReadRoot.path_to(self)))

        os.makedirs(out_dir, exist_ok = True)

        with open(os.path.join(out_dir, f'{self.name_noext}.html'), 'w') as f:
            f.write(Text)

class CDirs:
    _index = {
        CSettings.DirPages: (CFileMode.Required, True, '.md'),
        CSettings.DirTemplate: (CFileMode.Required, True, '.html'),

        CSettings.DirConfig: (CFileMode.Optional, True, ''),
        CSettings.DirForeach: (CFileMode.Optional, True, ''),
        CSettings.DirStatic: (CFileMode.Optional, False, ''),

        CSettings.DirOut: (CFileMode.Create, False, ''),
        CSettings.DirStaging: (CFileMode.Reset, False, ''),
    }

    def __init__(self):
        self.dirs = {}

        for dir_entry in CDirs._index:
            mode, read, allowed_ext = CDirs._index[dir_entry]
            self.dirs[dir_entry] = CDir(dir_entry, mode, read, allowed_ext)

    def get(self, Id):
        return self.dirs[Id]

    @staticmethod
    def validate():
        for dir_entry in CDirs._index:
            if CDirs._index[dir_entry][0] is CFileMode.Required \
                and not os.path.isdir(dir_entry):

                CUtil.error(f'Required dir {dir_entry} not found')

    @staticmethod
    def new_project(Path):
        CUtil.info(f'Creating new project at {Path}')

        try:
            os.makedirs(Path, exist_ok = True if Path == '.' else False)
        except FileExistsError:
            CUtil.error(f'Path {Path} already exists')

        CUtil.chdir(Path)

        for dir_entry in CDirs._index:
            mode = CDirs._index[dir_entry][0]

            if mode is CFileMode.Required:
                os.makedirs(dir_entry, exist_ok = True)

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
        {{!siter-md {{!siter-content}}}}
    </body>
</html>
""")

        write(CSettings.DirPages, 'index.md', """\
*Hello World!*
""")
