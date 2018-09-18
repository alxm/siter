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

from siterlib.util import Util

class FileMode(enum.Enum):
    Optional = 0
    Create = 1
    Required = 2

class File:
    def __init__(self, path, mode):
        self.path = os.path.abspath(path)
        self.mode = mode

        if self.mode is FileMode.Required and not self.exists():
            Util.error('Required file {} not found'.format(self.path))

    def exists(self):
        return os.path.exists(self.path)

    def get_path(self):
        return self.path

    def get_name(self):
        return os.path.basename(self.path)

    def get_mod_time(self):
        return os.stat(self.path).st_mtime

class Dir(File):
    def __init__(self, path, mode, read_contents = False):
        File.__init__(self, path, mode)

        self.files = {}
        self.dirs = {}

        if self.mode is FileMode.Create:
            os.makedirs(self.path, exist_ok = True)

        if not self.exists() or not read_contents:
            return

        for path in [os.path.join(self.path, p) for p in os.listdir(self.path)]:
            if os.path.isfile(path):
                self.files[path] = TextFile(path, FileMode.Required)
            elif os.path.isdir(path):
                self.dirs[path] = Dir(path, FileMode.Required, True)
            else:
                Util.error('Invalid file {}'.format(path))

    def get_dirs(self):
        return self.dirs.values()

    def get_files(self):
        return self.files.values()

    def add_dir(self, subdir, mode):
        path = os.path.join(self.path, subdir)

        if path not in self.dirs:
            self.dirs[path] = Dir(path, mode)

        return self.dirs[path]

    def add_file(self, name, mode):
        path = os.path.join(self.path, name)

        if path not in self.files:
            self.files[path] = TextFile(path, mode)

        return self.files[path]

    def path_to(self, target):
        return os.path.relpath(target.get_path(), start = self.path)

    def copy_to(self, dst_dir):
        src = self.path
        dst = dst_dir.path

        Util.message('Copy files', 'From {} to {}'.format(src, dst))

        shutil.rmtree(dst)
        shutil.copytree(src, dst)

class TextFile(File):
    def __init__(self, path, mode):
        File.__init__(self, path, mode)

        self.content = None
        self.lines = None

        if self.mode is not FileMode.Create:
            try:
                with open(self.path, 'rU') as f:
                    self.content = f.read()
            except FileNotFoundError:
                if self.mode is not FileMode.Optional:
                    Util.error('Required file {} not found'.format(self.path))

    def test_line(self, number, min_len = None, max_len = None):
        if self.content is None:
            return False

        error = None
        line = self.get_line(number)

        if line is None:
            error = '{}:{} line not found'.format(self.path, number)
        else:
            if min_len and len(line) < min_len:
                error = '{}:{} length must be at least {}, is {}: "{}"' \
                    .format(self.path, number, min_len, len(line), line)
            elif max_len and len(line) > max_len:
                error = '{}:{} length must not exceed {}, is {}: "{}"' \
                    .format(self.path, number, max_len, len(line), line)

        if error:
            if self.mode is FileMode.Optional:
                Util.warning(error)
            else:
                Util.error(error)

            return False

        return True

    def get_line(self, number):
        if self.lines is None:
            self.lines = self.content.splitlines()

        if number < len(self.lines):
            return self.lines[number].strip()

        return None

    def get_content(self):
        return self.content

    def write(self, text):
        with open(self.path, 'w') as f:
            f.write(text)

class Dirs:
    def __init__(self):
        self.pages = Dir('siter-pages', FileMode.Required, True)
        self.template = Dir('siter-template', FileMode.Required)
        self.config = Dir('siter-config', FileMode.Optional)
        self.static = Dir('siter-static', FileMode.Optional)
        self.out = Dir('siter-out', FileMode.Create)

class Files:
    def __init__(self, dirs):
        self.defs = dirs.config.add_file('defs', FileMode.Optional)
        self.evalhint = dirs.config.add_file('eval', FileMode.Optional)
        self.tags = dirs.config.add_file('tags', FileMode.Optional)
        self.page_html = dirs.template.add_file('page.html', FileMode.Optional)
