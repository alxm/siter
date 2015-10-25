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
from siterlib.binding import BindingType, BindingCollection
from siterlib.functions import Functions

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
        self.bindings = BindingCollection(self)

        # Set built-in global bindings
        self.__set_global_bindings()

        # Get user global bindings, if any
        if self.files.defs.exists():
            self.__set_file_bindings(self.files.defs, False)

    def __set_global_bindings(self):
        self.bindings.add(self.settings.Def,
                          BindingType.Function,
                          num_params = [1, 2, 3],
                          func = Functions.declare_binding,
                          protected = True)

        self.bindings.add(self.settings.If,
                          BindingType.Function,
                          num_params = [2, 3],
                          func = Functions.if_check,
                          protected = True)

        self.bindings.add(self.settings.Generated,
                          BindingType.Function,
                          num_params = [1],
                          func = Functions.gen_time,
                          protected = True)

        self.bindings.add(self.settings.Code,
                          BindingType.Function,
                          num_params = [1, 2, 3],
                          func = Functions.highlight_code,
                          protected = True)

    def __set_local_bindings(self, read_file, read_dir):
        self.bindings.add(self.settings.Modified,
                          BindingType.Function,
                          num_params = [1],
                          func = lambda _, args: Functions.mod_time(read_file, args[0]))

        self.bindings.add(self.settings.Root,
                          BindingType.Function,
                          num_params = [0],
                          func = lambda siter, _: read_dir.path_to(siter.dirs.pages))

    def __set_file_bindings(self, read_file, set_content):
        content = read_file.get_content()
        content_tokens = self.tokenizer.tokenize(content)
        content_tokens = self.__evaluate_collection(content_tokens)

        if set_content:
            self.bindings.add(self.settings.Content,
                              BindingType.Variable,
                              tokens = content_tokens,
                              protected = True)

    def __evaluate_collection(self, collection):
        eval_tokens = TokenCollection()

        for token in collection.get_tokens():
            if token.t_type is TokenType.Block:
                evaluated = self.__evaluate_block(token)

                if evaluated:
                    eval_tokens.add_collection(evaluated)
            else:
                eval_tokens.add_token(token)

        return eval_tokens

    def __evaluate_block(self, block):
        # Get the binding's name
        name = block.capture_call()

        if name is None:
            # This block does not call a binding
            return self.__evaluate_collection(block.tokens)

        if not self.bindings.contains(name):
            # Name is unknown, discard block
            return None

        binding = self.bindings.get(name)
        eval_tokens = TokenCollection()

        if binding.b_type is BindingType.Variable:
            eval_binding = self.__evaluate_collection(binding.tokens)
            eval_tokens.add_collection(eval_binding)
        elif binding.b_type is BindingType.Macro:
            args = block.capture_args(binding.num_params == [1])

            if len(args) not in binding.num_params:
                Util.warning('Macro {} takes {} args, got {}:\n{}'
                    .format(name, binding.num_params, len(args), block))
                return None

            self.bindings.push()

            # Bind each parameter to the supplied argument
            for i, param in enumerate(binding.params):
                self.bindings.add(param.resolve(),
                                  BindingType.Variable,
                                  tokens = TokenCollection([args[i]]))

            eval_binding = self.__evaluate_collection(binding.tokens)
            eval_tokens.add_collection(eval_binding)

            self.bindings.pop()
        elif binding.b_type is BindingType.Function:
            args = block.capture_args(binding.num_params == [1])

            if len(args) not in binding.num_params:
                Util.warning('Function {} takes {} args, got {}:\n{}'
                    .format(name, binding.num_params, len(args), block))
                return None

            if name == self.settings.Def:
                # Create a new user macro or variable
                binding.func(self.bindings, args)
            else:
                # Evaluate and resolve each argument
                arguments = [self.__evaluate_block(a).resolve() for a in args]

                body = binding.func(self, arguments)
                eval_tokens.add_collection(self.tokenizer.tokenize(body))
        else:
            Util.error('{} has an unknown binding type'.format(name))

        # Trim leading and trailing whitespace
        eval_tokens.trim()

        # Run page content through Markdown
        if binding.protected and name == self.settings.Content and self.imports.Md:
            content = eval_tokens.resolve()
            md = self.imports.Md.markdown(content, output_format = 'html5')
            md_token = Token(TokenType.Text, self.settings, text = md)
            eval_tokens = TokenCollection([md_token])

        return eval_tokens

    def __apply_template(self, template_file):
        content = template_file.get_content()
        tokens = self.tokenizer.tokenize(content)
        tokens = self.__evaluate_collection(tokens)

        return tokens.resolve()

    def __work(self, read_dir, write_dir):
        for in_file in read_dir.list_files():
            out_file = write_dir.add_file(in_file.get_name(), FileMode.Create)

            if self.settings.ForceWrite is False and in_file.older_than(out_file):
                Util.message('Up to date', out_file.get_path())
                continue

            Util.message('Updating', out_file.get_path())

            self.bindings.push()

            self.__set_local_bindings(in_file, read_dir)
            self.__set_file_bindings(in_file, True)

            # Load template and replace variables and functions with bindings
            final = self.__apply_template(self.files.page_html)
            out_file.write(final)

            self.bindings.pop()

        for read_subdir in read_dir.list_dirs():
            write_subdir = write_dir.add_dir(read_subdir.get_name(), FileMode.Create)
            self.__work(read_subdir, write_subdir)

    def run(self):
        self.__work(self.dirs.pages, self.dirs.out)
