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
from siterlib.settings import Settings
from siterlib.file import FileMode, Dirs, Files
from siterlib.tokenizer import Tokenizer
from siterlib.token import TokenType, Token, TokenCollection
from siterlib.bindings import Bindings
from siterlib.binding import BindingType

class Imports:
    def __init__(self):
        self.Md = Util.try_import('markdown')
        self.Pygments = Util.try_import('pygments')
        self.PygmentsLexers = Util.try_import('pygments.lexers')
        self.PygmentsFormatters = Util.try_import('pygments.formatters')

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
        self.tokenizer = Tokenizer(self.settings)

        # Copy static files
        self.dirs.static.copy_to(self.dirs.out)

        # Variables, macros, and functions
        self.bindings = Bindings(self)

        # Set built-in global bindings
        self.bindings.set_builtin_global()

        # Get user global bindings, if any
        if self.files.defs.exists():
            self.bindings.set_from_file(self.files.defs, False)

    def evaluate(self, tokens):
        eval_tokens = TokenCollection()

        for token in tokens:
            if token.t_type is not TokenType.Block:
                eval_tokens.add_token(token)
                continue

            # Get the binding's name
            name = token.capture_call()

            if name is None:
                # This block does not call a binding
                token_eval = self.evaluate(token.tokens.get_tokens())
                eval_tokens.add_collection(token_eval)
                continue

            if not self.bindings.contains(name):
                # Name is unknown, discard block
                continue

            binding = self.bindings.get(name)
            temp_tokens = TokenCollection()

            if binding.b_type is BindingType.Variable:
                eval_binding = self.evaluate(binding.tokens.get_tokens())
                temp_tokens.add_collection(eval_binding)
            elif binding.b_type is BindingType.Macro:
                args = token.capture_args(binding.num_params == [1])

                if len(args) not in binding.num_params:
                    Util.warning('Macro {} takes {} args, got {}:\n{}'
                        .format(name, binding.num_params, len(args), token))
                    continue

                arguments = []

                # Evaluate each argument
                for arg in args:
                    arguments.append(self.evaluate([arg]))

                self.bindings.push()

                # Bind each parameter to the supplied argument
                for (i, param) in enumerate(binding.params):
                    self.bindings.add(param.resolve(),
                                      BindingType.Variable,
                                      tokens = arguments[i])

                eval_binding = self.evaluate(binding.tokens.get_tokens())
                temp_tokens.add_collection(eval_binding)

                self.bindings.pop()
            elif binding.b_type is BindingType.Function:
                args = token.capture_args(binding.num_params == [1])

                if len(args) not in binding.num_params:
                    Util.warning('Function {} takes {} args, got {}:\n{}'
                        .format(name, binding.num_params, len(args), token))
                    continue

                if name == self.settings.Def:
                    # Create a new user macro or variable
                    binding.func(self.bindings, args)
                else:
                    arguments = []

                    # Evaluate each argument
                    for arg in args:
                        arg = self.evaluate([arg])
                        arguments.append(arg.resolve())

                    body = binding.func(self, arguments)
                    temp_tokens.add_tokens(self.tokenizer.tokenize(body))
            else:
                Util.error('{} has an unknown binding type'.format(name))

            # Trim leading and trailing whitespace
            temp_tokens.trim()

            # Run page content through Markdown
            if binding.protected and name == self.settings.Content and self.imports.Md:
                content = temp_tokens.resolve()
                md = self.imports.Md.markdown(content, output_format = 'html5')
                md_token = Token(TokenType.Text, self.settings, text = md)
                temp_tokens = TokenCollection([md_token])

            eval_tokens.add_collection(temp_tokens)

        return eval_tokens

    def __apply_template(self, template_file):
        content = template_file.get_content()
        tokens = self.tokenizer.tokenize(content)
        tokens = self.evaluate(tokens)

        return tokens.resolve()

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

            self.bindings.push()

            self.bindings.set_builtin_local(in_file, read_dir)
            self.bindings.set_from_file(in_file, True)

            # Load template and replace variables and functions with bindings
            final = self.__apply_template(self.files.page_html)
            out_file.write(final)

            self.bindings.pop()

        for read_subdir in read_dir.list_dirs():
            write_subdir = write_dir.add_dir(read_subdir.get_name(), FileMode.Create)
            self.run(read_subdir, write_subdir)
