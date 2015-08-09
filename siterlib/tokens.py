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

from siterlib.util import Util
from siterlib.bindings import BindingType, Binding

class TokenType(enum.Enum):
    Text = 1
    Newline = 2
    Whitespace = 3
    TagOpen = 4
    TagClose = 5
    Block = 6
    Eval = 7

class Token:
    def __init__(self, t_type, settings, text = None, tokens = None):
        self.settings = settings
        self.t_type = t_type
        self.text = text
        self.tokens = tokens if tokens else []

    def resolve(self):
        if self.t_type is TokenType.Block:
            output = ''.join([t.resolve() for t in self.tokens])
            return self.settings.TagOpen + output + self.settings.TagClose
        else:
            return self.text

    def capture(self, *args, rest = True):
        i = 0
        results = []

        for arg in args:
            found = False

            while i < len(self.tokens):
                token = self.tokens[i]
                i += 1

                if token.t_type is arg:
                    found = True
                    results.append(token)
                    break

                if (token.t_type is not TokenType.Newline and
                    token.t_type is not TokenType.Whitespace):
                    break

            if not found:
                return None

        if rest:
            # Capture all the remaining tokens
            results.append(self.tokens[i:])

        return results

    def capture_variable(self):
        # {var name *}
        results = self.capture(TokenType.Text, TokenType.Text)

        if results and results[0].resolve() == 'var':
            name = results[1]
            body = results[2]

            return name, body

        return None

    def capture_macro(self):
        # {fun name {args} body}
        results = self.capture(TokenType.Text, TokenType.Text, TokenType.Block)

        if results and results[0].resolve() == 'fun':
            name = results[1]
            args = [t for t in results[2].tokens if t.t_type is TokenType.Text]
            body = results[3]

            return name, args, body

        return None

    def capture_call(self):
        # {`name ...}
        results = self.capture(TokenType.Eval, TokenType.Text, rest = False)
        return results[1].resolve() if results else None

    def capture_args(self):
        # {`name {arg1} {arg2} ...}
        results = self.capture(TokenType.Eval, TokenType.Text)

        if results is None:
            return []

        args = [t for t in results[2] if t.t_type is TokenType.Block]

        if len(args) == 0:
            # Allow a single arg without block tags
            return [Token(TokenType.Block, self.settings, tokens = results[2])]

        return args

class Tokenizer:
    def __init__(self, siter):
        self.siter = siter
        self.settings = self.siter.settings

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
        block_tokens = self.make_block_tokens(flat_tokens)

        return block_tokens

    def evaluate(self, tokens, bindings):
        eval_tokens = []

        for token in tokens:
            if token.t_type is not TokenType.Block:
                eval_tokens.append(token)
                continue

            # Get the binding's name
            name = token.capture_call()

            if name is None:
                # This block does not call a binding
                eval_tokens += self.evaluate(token.tokens, bindings)
                continue

            if name not in bindings:
                # Name is unknown, discard block
                continue

            binding = bindings[name]
            temp_tokens = []

            if binding.b_type == BindingType.Variable:
                body_tokens = self.evaluate(binding.tokens, bindings)

                # Run page content through Markdown
                if name == 's.content' and self.siter.Md:
                    content = ''.join([t.resolve() for t in body_tokens])
                    md = self.siter.Md.markdown(content, output_format = 'html5')
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
                    arg = self.evaluate([arg], bindings)
                    arguments.append(arg)

                bindings2 = bindings.copy()

                # Bind each parameter to the supplied argument
                for (i, param) in enumerate(binding.params):
                    bindings2[param.resolve()] = Binding(BindingType.Variable,
                                                         tokens = arguments[i])

                temp_tokens += self.evaluate(binding.tokens, bindings2)
            elif binding.b_type == BindingType.Function:
                args = token.capture_args()

                if len(args) != binding.num_params != -1:
                    Util.warning('Function {} takes {} args, got {}'
                        .format(name, binding.num_params, len(args)))
                    continue

                arguments = []

                # Evaluate each argument
                for arg in args:
                    arg = self.evaluate([arg], bindings)
                    arguments.append(''.join([t.resolve() for t in arg]))

                body = binding.func(self.siter, arguments)
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
