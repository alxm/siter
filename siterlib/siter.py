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
from siterlib.binding import VariableBinding, MacroBinding, FunctionBinding, BindingCollection
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
        self.tokenizer = Tokenizer(self.settings.EvalHint,
                                   self.settings.TagOpen,
                                   self.settings.TagClose)

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
        self.bindings.add_function(self.settings.Def,
                                   [1, 2, 3],
                                   Functions.declare_binding,
                                   protected = True,
                                   lazy = True)

        self.bindings.add_function(self.settings.If,
                                   [2, 3],
                                   Functions.if_check,
                                   protected = True,
                                   lazy = True)

        self.bindings.add_function(self.settings.Generated,
                                   [1],
                                   Functions.gen_time,
                                   protected = True)

        self.bindings.add_function(self.settings.Code,
                                   [1, 2, 3],
                                   Functions.highlight_code,
                                   protected = True)

        self.bindings.add_function(self.settings.Markdown,
                                   [1],
                                   Functions.markdown,
                                   protected = True)

    def __set_local_bindings(self, read_file, read_dir):
        self.bindings.add_function(self.settings.Modified,
                                   [1],
                                   lambda _, args: Functions.mod_time(_, [read_file] + args))

        self.bindings.add_variable(self.settings.Root,
                                   self.tokenizer.tokenize(read_dir.path_to(self.dirs.pages)))

    def __set_file_bindings(self, read_file, set_content):
        content = read_file.get_content()
        content_tokens = self.tokenizer.tokenize(content)
        content_tokens = self.__evaluate_collection(content_tokens)

        if set_content:
            self.bindings.add_variable(self.settings.Content,
                                       content_tokens,
                                       protected = True)

    def __evaluate_collection(self, collection):
        eval_tokens = TokenCollection()

        for token in collection:
            if token.t_type is TokenType.Block:
                evaluated = self.evaluate_block(token)

                if evaluated:
                    eval_tokens.add_collection(evaluated)
            else:
                eval_tokens.add_token(token)

        return eval_tokens

    def evaluate_block(self, block):
        # Get the binding's name
        name = block.capture_call()

        if name is None:
            # This block does not call a binding
            return self.__evaluate_collection(block.tokens)

        if not self.bindings.contains(name):
            # Name is unknown, discard block
            Util.warning('Use of unknown binding {}:\n{}'.format(name, block))
            return None

        binding = self.bindings.get(name)
        eval_tokens = TokenCollection()

        if type(binding) is VariableBinding:
            eval_binding = self.__evaluate_collection(binding.tokens)
            eval_tokens.add_collection(eval_binding)
        elif type(binding) is MacroBinding:
            args = block.capture_args(binding.num_params == 1)

            if len(args) != binding.num_params:
                Util.warning('Macro {} takes {} args, got {}:\n{}'
                    .format(name, binding.num_params, len(args), block))
                return None

            self.bindings.push()

            # Bind each parameter to the supplied argument
            for arg, param in zip(args, binding.params):
                self.bindings.add_variable(param.resolve(), TokenCollection([arg]))

            eval_binding = self.__evaluate_collection(binding.tokens)
            eval_tokens.add_collection(eval_binding)

            self.bindings.pop()
        elif type(binding) is FunctionBinding:
            args = block.capture_args(binding.num_params == [1])

            if len(args) not in binding.num_params:
                Util.warning('Function {} takes {} args, got {}:\n{}'
                    .format(name, binding.num_params, len(args), block))
                return None

            if binding.lazy:
                # Feed block tokens directly to function
                result = binding.func(self, args)

                if result:
                    result = self.evaluate_block(result)
                    eval_tokens.add_collection(result)
            else:
                # Evaluate and resolve each argument
                arguments = [self.evaluate_block(a).resolve() for a in args]

                body = binding.func(self, arguments)
                eval_tokens.add_collection(self.tokenizer.tokenize(body))

        # Trim leading and trailing whitespace
        eval_tokens.trim()

        # Run page content through Markdown
        if binding.protected and name == self.settings.Content and self.imports.Md:
            content = eval_tokens.resolve()
            md = self.imports.Md.markdown(content, output_format = 'html5')
            md_token = Token(TokenType.Text, md)
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
