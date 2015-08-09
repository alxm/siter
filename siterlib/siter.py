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
import time

from siterlib.util import Util
from siterlib.files import FileMode, Dirs, Files
from siterlib.tokens import Token, TokenType

class BindingType(enum.Enum):
    Variable = 0
    Macro = 1
    Function = 2

class Binding:
    def __init__(self, b_type, tokens = None, num_params = 0, params = None, func = None):
        self.b_type = b_type
        self.tokens = tokens
        self.num_params = len(params) if params else num_params
        self.params = params
        self.func = func

class BuiltInFunctions:
    @staticmethod
    def highlight_code(siter, args):
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
        else:
            Util.warning('s.code takes 1-3 args, got {}'.format(len(args)))
            return ''

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

            if siter.Pygments:
                lexer = siter.PygmentsLexers.get_lexer_by_name(lang.lower())
                formatter = siter.PygmentsFormatters.HtmlFormatter(
                    linenos = True, cssclass = div_class, hl_lines=lines)
                code = siter.Pygments.highlight(code, lexer, formatter)
            else:
                code = '<div class="{}"><pre>{}</pre></div>' \
                    .format(div_class, clean_code(code))

        return code

class Settings:
    def __init__(self, argv, files):
        # Whether to re-generate up-to-date files
        self.ForceWrite = False

        # Blocks that start with this are evaluated; must be exactly 1 char
        self.EvalHint = '`'

        # Block delimiters
        self.TagOpen = '{'
        self.TagClose = '}'

        # Marks the beginning of page content
        self.Marker = '~~~'

        # Load user settings
        self.from_args(argv)
        self.from_files(files)

    def from_args(self, argv):
        # Go through command line arguments
        for arg in argv:
            if arg == '-f' or arg == '--force':
                self.ForceWrite = True

    def from_files(self, files):
        if files.evalhint.test_line(0, 1, 1):
            self.EvalHint = files.evalhint.get_line(0)
            Util.info('Using {} as block eval hint'.format(self.EvalHint))

        if files.tags.test_line(0, 1) and files.tags.test_line(1, 1):
            self.TagOpen = files.tags.get_line(0)
            self.TagClose = files.tags.get_line(1)

            Util.info('Using {} and {} as block tags'
                .format(self.TagOpen, self.TagClose))

        if files.marker.test_line(0, 1):
            self.Marker = files.marker.get_line(0)

class Siter:
    def __init__(self, argv):
        # Declare and optionally create the dirs and files Siter uses
        self.dirs = Dirs()
        self.files = Files(self.dirs)

        # Set defaults and load user settings from args and config files
        self.settings = Settings(argv, self.files)

        # Copy site and template media files
        self.dirs.in_media.copy_to(self.dirs.out_media)
        self.dirs.in_template_media.copy_to(self.dirs.out_template_media)

        # Global function and variable bindings
        self.bindings = {}
        self.set_file_bindings(self.bindings, self.files.defs)

        self.Md = Util.try_import('markdown')
        self.Pygments = Util.try_import('pygments')
        self.PygmentsLexers = Util.try_import('pygments.lexers')
        self.PygmentsFormatters = Util.try_import('pygments.formatters')

    def make_flat_tokens(self, text):
        flat_tokens = []
        current_type = None
        escaped = False
        escaped_index = -1
        token = ''

        for c in text:
            if c == '\\' and not escaped:
                escaped = True
                continue

            previous_type = current_type

            if c == '\n':
                current_type = TokenType.Newline
            elif c == ' ' or c == '\t':
                current_type = TokenType.Whitespace
            else:
                current_type = TokenType.Text

            if current_type is previous_type:
                token += c
            else:
                if len(token) > 0:
                    flat_tokens.append(Token(previous_type, self.settings, token))

                token = c
                escaped_index = -1

            if escaped:
                escaped = False
                escaped_index = len(token) - 1

            delim_tokens = [
                (TokenType.Eval, self.settings.EvalHint),
                (TokenType.TagOpen, self.settings.TagOpen),
                (TokenType.TagClose, self.settings.TagClose),
            ]

            for delim_type, delim in delim_tokens:
                if len(token) - escaped_index <= len(delim):
                    continue

                if token[-len(delim) :] != delim:
                    continue

                if len(token) > len(delim):
                    flat_tokens.append(
                        Token(TokenType.Text, self.settings, token[: -len(delim)]))

                flat_tokens.append(Token(delim_type, self.settings, token[-len(delim) :]))
                token = ''
                escaped_index = -1
                break

        if len(token) > 0:
            flat_tokens.append(Token(current_type, self.settings, token))

        return flat_tokens

    def make_block_tokens(self, flat_tokens):
        stack = []
        block_tokens = []

        for token in flat_tokens:
            if token.t_type is TokenType.TagOpen:
                # Subsequent tokens will be added to this new block
                stack.append(Token(TokenType.Block, self.settings))
            else:
                if token.t_type is TokenType.TagClose:
                    if len(stack) == 0:
                        Util.error("Found extra closing tag")

                    # Got the closing tag, pop the block from the stack
                    token = stack.pop()

                if len(stack) > 0:
                    stack[-1].tokens.append(token)
                else:
                    block_tokens.append(token)

        if len(stack) > 0:
            Util.error("Missing closing tag")

        return block_tokens

    def tokenize(self, text):
        flat_tokens = self.make_flat_tokens(text)
        return self.make_block_tokens(flat_tokens)

    def evaluate_tokens(self, tokens, bindings):
        eval_tokens = []

        for token in tokens:
            if token.t_type is not TokenType.Block:
                eval_tokens.append(token)
                continue

            # Get the binding's name
            name = token.capture_call()

            if name is None:
                # This block does not call a binding
                eval_tokens += self.evaluate_tokens(token.tokens, bindings)
                continue

            if name not in bindings:
                # Name is unknown, discard block
                continue

            binding = bindings[name]
            temp_tokens = []

            if binding.b_type == BindingType.Variable:
                body_tokens = self.evaluate_tokens(binding.tokens, bindings)

                # Run page content through Markdown
                if name == 's.content' and self.Md:
                    content = ''.join([t.resolve() for t in body_tokens])
                    md = self.Md.markdown(content, output_format = 'html5')
                    body_tokens = [Token(TokenType.Text, self.settings, text = md)]

                temp_tokens += body_tokens
            elif binding.b_type == BindingType.Macro:
                args = token.capture_args()

                if len(args) != binding.num_params:
                    Util.warning('Macro {} takes {} args, got {}'
                        .format(name, binding.num_params, len(args)))
                    continue

                arguments = []

                # Evaluate each argument
                for arg in args:
                    arg = self.evaluate_tokens([arg], bindings)
                    arguments.append(arg)

                bindings2 = bindings.copy()

                # Bind each parameter to the supplied argument
                for (i, param) in enumerate(binding.params):
                    bindings2[param.resolve()] = Binding(BindingType.Variable,
                                                         tokens = arguments[i])

                temp_tokens += self.evaluate_tokens(binding.tokens, bindings2)
            elif binding.b_type == BindingType.Function:
                args = token.capture_args()

                if len(args) != binding.num_params != -1:
                    Util.warning('Function {} takes {} args, got {}'
                        .format(name, binding.num_params, len(args)))
                    continue

                arguments = []

                # Evaluate each argument
                for arg in args:
                    arg = self.evaluate_tokens([arg], bindings)
                    arguments.append(''.join([t.resolve() for t in arg]))

                body = binding.func(self, arguments)
                temp_tokens += self.tokenize(body)
            else:
                Util.error('Unknown binding type')

            # Trim leading and trailing whitespace
            start = 0
            end = len(temp_tokens)

            for t in temp_tokens:
                if t.t_type is TokenType.Text:
                    break
                else:
                    start += 1

            for t in reversed(temp_tokens):
                if t.t_type is TokenType.Text:
                    break
                else:
                    end -= 1

            eval_tokens += temp_tokens[start : end]

        return eval_tokens

    def set_file_bindings(self, bindings, read_file):
        start = 0
        text = read_file.get_content()
        marker = text.find(self.settings.Marker)

        if marker != -1:
            # s.content is everything after the first marker occurence
            bindings['s.content'] = Binding(
                BindingType.Variable,
                tokens = self.tokenize(text[marker + len(self.settings.Marker) :]))
            text = text[: marker]

        for b in [t for t in self.tokenize(text) if t.t_type is TokenType.Block]:
            results = b.capture_variable()

            if results:
                name, body = results
                bindings[name.resolve()] = Binding(BindingType.Variable,
                                                   tokens = body)
                continue

            results = b.capture_macro()

            if results:
                name, args, body = results
                bindings[name.resolve()] = Binding(BindingType.Macro,
                                                   params = args,
                                                   tokens = body)
                continue

            Util.warning('Unknown binding block:\n{}'.format(b.resolve()))

    def set_builtin_bindings(self, bindings, read_file, read_dir):
        bindings['s.if'] = Binding(
            BindingType.Function,
            num_params = 2,
            func = lambda _, args: args[1] if args[0] in bindings else '')

        bindings['s.ifnot'] = Binding(
            BindingType.Function,
            num_params = 2,
            func = lambda _, args: '' if args[0] in bindings else args[1])

        bindings['s.modified'] = Binding(
            BindingType.Function,
            num_params = 1,
            func = lambda _, args: time.strftime(
                args[0], time.localtime(read_file.get_mod_time())))

        bindings['s.generated'] = Binding(
            BindingType.Function,
            num_params = 1,
            func = lambda _, args: time.strftime(args[0]))

        bindings['s.code'] = Binding(
            BindingType.Function,
            num_params = -1,
            func = BuiltInFunctions.highlight_code)

        current_subdir = self.dirs.in_pages.path_to(read_dir)
        here = self.dirs.out_root.add_dir(current_subdir)
        rel_root_path = here.path_to(self.dirs.out_root)
        rel_media_path = here.path_to(self.dirs.out_media)

        bindings['s.root'] = Binding(
            BindingType.Variable,
            tokens = self.tokenize(rel_root_path))

        bindings['s.media'] = Binding(
            BindingType.Variable,
            tokens = self.tokenize(rel_media_path))

    def apply_template(self, template_file, bindings):
        tokens = self.tokenize(template_file.get_content())
        tokens = self.evaluate_tokens(tokens, bindings)

        return ''.join([t.resolve() for t in tokens])

    def run(self, read_dir = None, write_dir = None):
        if read_dir is None:
            read_dir = self.dirs.in_pages

        if write_dir is None:
            write_dir = self.dirs.out_root

        for in_file in read_dir.list_files():
            out_file = write_dir.add_file(in_file.get_name(), FileMode.Create)

            if self.settings.ForceWrite is False and in_file.older_than(out_file):
                Util.message('Up to date', out_file.get_path())
                continue

            Util.message('Updating', out_file.get_path())

            #   global bindings from the defs file
            # + bindings declared by the current page file
            # + siter built-in bindings
            bindings = self.bindings.copy()
            self.set_file_bindings(bindings, in_file)
            self.set_builtin_bindings(bindings, in_file, read_dir)

            # Load template and replace variables and functions with bindings
            final = self.apply_template(self.files.page_html, bindings)
            out_file.write(final)

        for read_subdir in read_dir.list_dirs():
            write_subdir = write_dir.add_dir(read_subdir.get_name())
            self.run(read_subdir, write_subdir)
