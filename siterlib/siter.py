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

import os, time

import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.fenced_code import FencedCodeExtension

from .binding import *
from .file import *
from .functions import *
from .settings import *
from .token import *
from .tokenizer import *
from .util import *

class CSiter:
    def __init__(self, Argv):
        # Cached template tokens
        self.template_tokens = {}

        # Declare and optionally create the dirs and files Siter uses
        self.dirs = CDirs()
        self.files = CFiles(self.dirs)

        self.md = markdown.Markdown(
                    output_format = 'html5',
                    extensions = [
                        CodeHiliteExtension(css_class = CSettings.PygmentsDiv,
                                            linenums = True),
                        FencedCodeExtension()
                    ])

        # Copy static files
        if self.dirs.static.exists():
            self.dirs.static.copy_to(self.dirs.out)

        # Variables, macros, and functions
        self.bindings = CBindingCollection(self)

        # Set built-in global bindings
        self.__set_global_bindings()

        # Get user global bindings, if any
        if self.files.defs.exists():
            self.__set_file_bindings(self.files.defs, False)

    def __set_global_bindings(self):
        self.bindings.add_function(CSettings.Def,
                                   [1, 2, 3],
                                   CFunctions.declare_binding,
                                   Protected = True,
                                   Lazy = True)

        self.bindings.add_function(CSettings.If,
                                   [2, 3],
                                   CFunctions.if_check,
                                   Protected = True,
                                   Lazy = True)

        self.bindings.add_function(CSettings.Generated,
                                   [1],
                                   CFunctions.gen_time,
                                   Protected = True)

        self.bindings.add_function(CSettings.Datefmt,
                                   [2],
                                   CFunctions.datefmt,
                                   Protected = True)

        self.bindings.add_function(CSettings.Code,
                                   [1, 2, 3],
                                   CFunctions.highlight_code,
                                   Protected = True)

        self.bindings.add_function(CSettings.Markdown,
                                   [1],
                                   CFunctions.markdown,
                                   Protected = True)

        self.bindings.add_function(CSettings.Anchor,
                                   [1],
                                   CFunctions.anchor,
                                   Protected = True)

        self.bindings.add_function(CSettings.Apply,
                                   [2, 3],
                                   CFunctions.apply_template,
                                   Protected = True)

    def __set_local_bindings(self, ReadFile, ReadDir):
        self.bindings.add_function(CSettings.Modified,
                                   [1],
                                   lambda _, args: \
                                       CFunctions.mod_time(
                                        _, [ReadFile] + args))

        self.bindings.add_variable(CSettings.Root,
                                   CTokenizer.tokenize(
                                       ReadDir.path_to(self.dirs.pages)))

    def __set_file_bindings(self, ReadFile, SetContent):
        content = ReadFile.get_content()
        content_tokens = CTokenizer.tokenize(content)
        content_tokens = self.__evaluate_collection(content_tokens)

        if SetContent:
            self.bindings.add_variable(CSettings.Content,
                                       content_tokens,
                                       Protected = True)

    def __evaluate_collection(self, Collection):
        eval_tokens = CTokenCollection()

        for token in Collection:
            if type(token) is CTokenBlock:
                evaluated = self.evaluate_block(token)

                if evaluated:
                    eval_tokens.add_collection(evaluated)
            else:
                eval_tokens.add_token(token)

        return eval_tokens

    def evaluate_block(self, Block):
        # Get the binding's name
        name = Block.capture_call()

        if name is None:
            # This Block does not call a binding
            return self.__evaluate_collection(Block.tokens)

        if not self.bindings.contains(name):
            # Name is unknown, discard Block
            CUtil.warning(f'Use of unknown binding {name}:\n{Block}')

            return None

        binding = self.bindings.get(name)
        eval_tokens = CTokenCollection()

        if type(binding) is CBindingVariable:
            eval_binding = self.__evaluate_collection(binding.tokens)
            eval_tokens.add_collection(eval_binding)
        elif type(binding) is CBindingMacro:
            args = Block.capture_args(binding.num_params == 1)

            if len(args) < binding.num_params_req or \
                len(args) > binding.num_params:

                CUtil.warning(
                    f'Macro {name} takes ' \
                    f'{binding.num_params_req}-{binding.num_params} ' \
                    f'args, got {len(args)}:\n{Block}')

                return None

            self.bindings.push()

            # Bind each parameter to the supplied argument
            for param, arg in zip(binding.params, args):
                self.bindings.add_variable(param, self.evaluate_block(arg))

            # Fill in missing optional arguments
            for param in binding.params[len(args) :]:
                self.bindings.add_variable(param, CTokenCollection())

            # Evaluate macro body's tokens with the set parameters
            eval_binding = self.__evaluate_collection(binding.tokens)
            eval_tokens.add_collection(eval_binding)

            self.bindings.pop()
        elif type(binding) is CBindingFunction:
            args = Block.capture_args(binding.num_params == [1])

            if len(args) not in binding.num_params:
                CUtil.warning(f'Function {name} takes ' \
                              f'{binding.num_params} args, ' \
                              f'got {len(args)}:\n{Block}')

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
                eval_tokens.add_token(CTokenText(body))

        # Trim leading and trailing whitespace
        eval_tokens.trim()

        return eval_tokens

    def process_file(self, InFile, ReadDir, TemplateFile, IsStub = False):
        CUtil.message('Process', InFile.get_path())

        self.bindings.push()

        # Keep root path relative to the file that invoked the stub
        if not IsStub:
            self.__set_local_bindings(InFile, ReadDir)

        self.__set_file_bindings(InFile, True)

        # Load template and replace variables and functions with bindings
        try:
            tokens = self.template_tokens[TemplateFile]
        except KeyError:
            tokens = CTokenizer.tokenize(TemplateFile.get_content())
            self.template_tokens[TemplateFile] = tokens

        final = self.__evaluate_collection(tokens).resolve()

        self.bindings.pop()

        return final

    def __work(self, ReadDir, WriteDir):
        counter = 0

        for in_file in ReadDir.get_files():
            name = in_file.get_name()
            root, ext = os.path.splitext(name)

            if ext != '.md':
                CUtil.warning(f'Ignoring page file {name}')

                continue

            out_file = WriteDir.add_file(f'{root}.html', CFileMode.Create)
            output = self.process_file(in_file, ReadDir, self.files.page_html)
            out_file.write(output)
            counter += 1

        for read_subdir in ReadDir.get_dirs():
            write_subdir = WriteDir.add_dir(read_subdir.get_name(),
                                             CFileMode.Create)
            counter += self.__work(read_subdir, write_subdir)

        return counter

    def run(self):
        start = time.perf_counter()
        count = self.__work(self.dirs.pages, self.dirs.out)
        elapsed = round(time.perf_counter() - start + 0.05, 1)

        CUtil.message('Done', f'{count} pages in {elapsed}s')
