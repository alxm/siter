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

import time

import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.toc import TocExtension

from .binding import *
from .file import *
from .functions import *
from .settings import *
from .token import *
from .tokenizer import *
from .util import *

class CSiter:
    def __init__(self, Argv):
        try:
            command = Argv[1]
        except IndexError:
            command = ''

        try:
            path_arg = Argv[2]
        except IndexError:
            path_arg = '.'

        if command == 'new':
            CDirs.new_project(path_arg)
        else:
            do_gen = False
            do_serve = False

            if command == 'gen':
                do_gen = True
            elif command == 'run':
                do_gen = True
                do_serve = True
            elif command == 'serve':
                do_serve = True
            elif command == '':
                do_gen = True
            else:
                do_gen = True
                path_arg = command

            CUtil.chdir(path_arg)
            CDirs.validate()

            self._log_out = []

            if do_gen:
                self._log('Total Gen', self._step_main)

            if do_serve:
                self._log('Total Serve', self._step_serve)

            for line in self._log_out:
                CUtil.info(line)

    def _log(self, Tag, Function):
        self._log_out.append(f'{Tag}: {CUtil.time_step(Function)}s')

    def _step_main(self):
        self.md = markdown.Markdown(
                    output_format = 'html5',
                    extensions = [
                        CodeHiliteExtension(css_class = CSettings.PygmentsDiv,
                                            linenums = True),
                        FencedCodeExtension(),
                        TocExtension(title = CSettings.TocTitle,
                                     permalink = CSettings.HeaderLink),
                    ])

        self._log('Load pages', self._step_load)
        self._log('Copy static', self._step_static)
        self._log('Generate pages', self._step_gen)
        self._log('Copy output', self._step_copy)

    def _step_serve(self):
        CUtil.run_server(CSettings.DirOut)

    def _step_load(self):
        self.dirs = CDirs()
        self.bindings = CBindingCollection(self)
        self._stubs_cache = {}
        self._set_global_bindings()

        for f in self.dirs.get(CSettings.DirConfig).get_files():
            self._set_file_bindings(f, False)

    def _step_static(self):
        self.dirs.get(CSettings.DirStatic).copy_to(
            self.dirs.get(CSettings.DirStaging))

    def _step_gen(self):
        page_template = self.dirs.get(CSettings.DirTemplate).get_file(
                            CSettings.TemplatePage)

        for in_file in self.dirs.get(CSettings.DirPages).get_files():
            in_file.write(self.process_file(in_file, page_template),
                          self.dirs.get(CSettings.DirStaging),
                          self.dirs.get(CSettings.DirPages))

    def _step_copy(self):
        self.dirs.get(CSettings.DirStaging).replace(
            self.dirs.get(CSettings.DirOut))

    def _set_global_bindings(self):
        self.bindings.add_variable(CSettings.Generated,
                                   CTokenizer.text(time.strftime('%Y-%m-%d')))

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

        self.bindings.add_function(CSettings.Datefmt,
                                   [2],
                                   CFunctions.datefmt,
                                   Protected = True)

        self.bindings.add_function(CSettings.Markdown,
                                   [1],
                                   CFunctions.markdown,
                                   Protected = True)

        self.bindings.add_function(CSettings.Anchor,
                                   [1],
                                   CFunctions.anchor,
                                   Protected = True)

        self.bindings.add_function(CSettings.Stubs,
                                   [2, 3, 4],
                                   CFunctions.stubs,
                                   Protected = True)

    def _set_local_bindings(self, ReadFile):
        f_time = ReadFile.get_mod_time()
        time_obj = time.localtime(f_time)

        self.bindings.add_variable(CSettings.Modified,
                                   CTokenizer.text(time.strftime('%Y-%m-%d',
                                                                 time_obj)))

        rel_root = ReadFile.path_to(self.dirs.get(CSettings.DirPages))

        self.bindings.add_variable(CSettings.Root, CTokenizer.text(rel_root))

    def _set_file_bindings(self, ReadFile, SetContent):
        content_tokens = self._evaluate_collection(ReadFile.tokens)

        if SetContent:
            self.bindings.add_variable(CSettings.Content,
                                       content_tokens,
                                       Protected = True)

    def _evaluate_collection(self, Collection):
        eval_tokens = CTokenCollection()

        for token in Collection:
            if type(token) is CTokenBlock:
                eval_tokens.add_collection(self.evaluate_block(token))
            else:
                eval_tokens.add_token(token)

        return eval_tokens

    def evaluate_block(self, Block):
        eval_tokens = CTokenCollection()

        # Get the binding's name
        name = Block.capture_call()

        if name is None:
            # This Block does not call a binding
            return self._evaluate_collection(Block.tokens)

        if not self.bindings.contains(name):
            # Name is unknown, discard Block
            CUtil.warning(f'Use of unknown binding {name}:\n{Block}')

            return eval_tokens

        binding = self.bindings.get(name)

        if type(binding) is CBindingVariable:
            eval_binding = self._evaluate_collection(binding.tokens)
            eval_tokens.add_collection(eval_binding)
        elif type(binding) is CBindingMacro:
            args = Block.capture_args(binding.num_params == 1)

            if len(args) < binding.num_params_req or \
                len(args) > binding.num_params:

                CUtil.warning(
                    f'Macro {name} takes ' \
                    f'{binding.num_params_req}-{binding.num_params} ' \
                    f'args, got {len(args)}:\n{Block}')

                return eval_tokens

            self.bindings.push()

            # Bind each parameter to the supplied argument
            for param, arg in zip(binding.params, args):
                self.bindings.add_variable(param, self.evaluate_block(arg))

            # Fill in missing optional arguments
            for param in binding.params[len(args) :]:
                self.bindings.add_variable(param, CTokenCollection())

            # Evaluate macro body's tokens with the set parameters
            eval_binding = self._evaluate_collection(binding.tokens)
            eval_tokens.add_collection(eval_binding)

            self.bindings.pop()
        elif type(binding) is CBindingFunction:
            args = Block.capture_args(binding.num_params == [1])

            if len(args) not in binding.num_params:
                CUtil.warning(f'Function {name} takes ' \
                              f'{binding.num_params} args, ' \
                              f'got {len(args)}:\n{Block}')

                return eval_tokens

            if binding.lazy:
                # Feed block tokens directly to function
                result = binding.func(self, args)
                eval_tokens.add_collection(self.evaluate_block(result))
            else:
                # Evaluate and resolve each argument
                arguments = [self.evaluate_block(a).resolve() for a in args]

                body = binding.func(self, arguments)
                eval_tokens.add_token(CTokenText(body))

        # Trim leading and trailing whitespace
        eval_tokens.trim()

        return eval_tokens

    def process_file(self, InFile, TemplateFile, IsStub = False):
        CUtil.message('Process', InFile.shortpath)

        if IsStub and InFile.shortpath in self._stubs_cache:
            return self._stubs_cache[InFile.shortpath]

        self.bindings.push()

        # Keep root path relative to the file that invoked the stub
        if not IsStub:
            self._set_local_bindings(InFile)

        self._set_file_bindings(InFile, True)

        # Load template and replace variables and functions with bindings
        final = self._evaluate_collection(TemplateFile.tokens).resolve()

        self.bindings.pop()

        if IsStub:
            self._stubs_cache[InFile.shortpath] = final

        return final
