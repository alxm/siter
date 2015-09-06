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
from siterlib.token import TokenType
from siterlib.binding import BindingType, Binding
from siterlib.functions import Functions

class Bindings:
    def __init__(self, siter):
        self.siter = siter
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

    def set_builtin_global(self):
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
                 func = Functions.if_check)

        self.add('s.generated',
                 BindingType.Function,
                 num_params = [1],
                 func = Functions.gen_time)

        self.add('s.code',
                 BindingType.Function,
                 num_params = [1, 2, 3],
                 func = Functions.highlight_code)

    def set_builtin_local(self, read_file, read_dir):
        self.add('s.modified',
                 BindingType.Function,
                 num_params = [1],
                 func = lambda _, args: Functions.mod_time(read_file, args[0]),
                 overwrite = False)

        self.add('s.root',
                 BindingType.Function,
                 num_params = [0],
                 func = lambda siter, _: read_dir.path_to(siter.dirs.pages),
                 overwrite = False)

    def set_from_file(self, read_file):
        content = read_file.get_content()

        content_tokens = self.siter.tokenizer.tokenize(content)
        content_tokens = self.siter.evaluate(content_tokens)

        self.add('s.content', BindingType.Variable, tokens = content_tokens)

        for b in [t for t in self.siter.tokenizer.tokenize(content) if t.t_type is TokenType.Block]:
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
