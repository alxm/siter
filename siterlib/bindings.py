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
            # s.content is everything after the first marker occurence
            self.add('s.content', BindingType.Variable,
                tokens = self.tokenizer.tokenize(text[marker + len(self.settings.Marker) :]))
            text = text[: marker]

        for b in [t for t in self.tokenizer.tokenize(text) if t.t_type is TokenType.Block]:
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
                 func = BuiltInFunctions.highlight_code)

        current_subdir = dirs.pages.path_to(read_dir)
        here = dirs.out.add_dir(current_subdir, FileMode.Optional)
        rel_root_path = here.path_to(dirs.out)

        self.add('s.root',
                 BindingType.Variable,
                 tokens = self.tokenizer.tokenize(rel_root_path),
                 overwrite = False)

class BuiltInFunctions:
    @staticmethod
    def highlight_code(imports, args):
        if len(args) == 1:
            lang = 'text'
            code = args[0]
            lines = []
        elif len(args) == 2:
            lang = args[0]
            code = args[1]
            lines = []
        elif len(args) == 3:
            lang = args[0]
            code = args[2]
            lines = args[1].split()

        def clean_code(code):
            # Replace < and > with HTML entities
            code = code.replace('<', '&lt;')
            code = code.replace('>', '&gt;')
            return code

        if code.find('\n') == -1:
            # This is a one-liner
            code = '<code>{}</code>'.format(clean_code(code))
        else:
            # This is a code block
            div_class = 'siter_code'

            if imports.Pygments:
                lexer = imports.PygmentsLexers.get_lexer_by_name(lang.lower())
                formatter = imports.PygmentsFormatters.HtmlFormatter(
                    linenos = True, cssclass = div_class, hl_lines=lines)
                code = imports.Pygments.highlight(code, lexer, formatter)
            else:
                code = '<div class="{}"><pre>{}</pre></div>' \
                    .format(div_class, clean_code(code))

        return code
