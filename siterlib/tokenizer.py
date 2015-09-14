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
from siterlib.token import TokenType, Token, TokenCollection

class Tokenizer:
    def __init__(self, settings):
        self.settings = settings

    def __make_flat_tokens(self, text):
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

            if c in [' ', '\t', '\n']:
                current_type = TokenType.Whitespace
            else:
                current_type = TokenType.Text

            if current_type is previous_type:
                token += c
            else:
                if len(token) > 0:
                    flat_tokens.append(Token(previous_type, self.settings, text = token))

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
                        Token(TokenType.Text, self.settings, text = token[: -len(delim)]))

                flat_tokens.append(Token(delim_type, self.settings, text = token[-len(delim) :]))
                token = ''
                escaped_index = -1
                break

        if len(token) > 0:
            flat_tokens.append(Token(current_type, self.settings, text = token))

        return flat_tokens

    def __make_block_tokens(self, flat_tokens):
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
                    stack[-1].tokens.add_token(token)
                else:
                    block_tokens.append(token)

        if len(stack) > 0:
            Util.error("Missing closing tag")

        return block_tokens

    def tokenize(self, text):
        flat_tokens = self.__make_flat_tokens(text)
        block_tokens = self.__make_block_tokens(flat_tokens)

        return TokenCollection(block_tokens)
