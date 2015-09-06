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

import time

from siterlib.util import Util
from siterlib.token import TokenType
from siterlib.binding import BindingType, Binding
from siterlib.file import FileMode
from siterlib.functions import Functions

class Bindings:
    def __init__(self, settings, tokenizer):
        self.settings = settings
        self.tokenizer = tokenizer
        self.bindings = {}
        self.stack = []

    def contains(self, name):
        return name in self.bindings

    def add(self, name, b_type, tokens = None, num_params = None, params = None, func = None, overwrite = True):
        if overwrite or not self.contains(name):
            binding = Binding(b_type, tokens, num_params, params, func)
            self.bindings[name] = binding

    def get(self, name):
        if name not in self.bindings:
            Util.error('{} not in bindings'.format(name))

        return self.bindings[name]

    def push(self):
        self.stack.append(self.bindings.copy())

    def pop(self):
        self.bindings = self.stack.pop()

    def set_from_file(self, read_file):
        start = 0
        text = read_file.get_content()
        marker = text.find(self.settings.Marker)

        if marker != -1:
            declarations = text[: marker]
            content = text[marker + len(self.settings.Marker) :]
        else:
            declarations = text
            content = ''

        content_tokens = self.tokenizer.tokenize(content)
        content_tokens = self.tokenizer.evaluate(content_tokens, self)

        self.add('s.content', BindingType.Variable, tokens = content_tokens)

        for b in [t for t in self.tokenizer.tokenize(declarations) if t.t_type is TokenType.Block]:
            results = b.capture_variable()

            if results:
                name, body = results
                self.add(name.resolve(), BindingType.Variable, tokens = body)
                continue

            results = b.capture_macro()

            if results:
                name, args, body = results
                self.add(name.resolve(), BindingType.Macro, params = args, tokens = body)
                continue

            Util.warning('Unknown binding block:\n{}'.format(b))

    def set_builtin(self, read_file, read_dir, dirs):
        self.add('s.var',
                 BindingType.Function,
                 num_params = [2],
                 func = Functions.declare_variable)

        self.add('s.fun',
                 BindingType.Function,
                 num_params = [3],
                 func = Functions.declare_function)

        self.add('s.if',
                 BindingType.Function,
                 num_params = [2, 3],
                 func = lambda _, args: args[1] if self.contains(args[0]) else args[2] if len(args) == 3 else '')

        self.add('s.modified',
                 BindingType.Function,
                 num_params = [1],
                 func = lambda _, args: time.strftime(args[0], time.localtime(read_file.get_mod_time())),
                 overwrite = False)

        self.add('s.generated',
                 BindingType.Function,
                 num_params = [1],
                 func = lambda _, args: time.strftime(args[0]))

        self.add('s.code',
                 BindingType.Function,
                 num_params = [1, 2, 3],
                 func = Functions.highlight_code)

        current_subdir = dirs.pages.path_to(read_dir)
        here = dirs.out.add_dir(current_subdir, FileMode.Optional)
        rel_root_path = here.path_to(dirs.out)

        self.add('s.root',
                 BindingType.Variable,
                 tokens = self.tokenizer.tokenize(rel_root_path),
                 overwrite = False)
