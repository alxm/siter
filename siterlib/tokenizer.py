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
from siterlib.token import TokenType, Token, BlockToken, TokenCollection

class Tokenizer:
    def __init__(self, eval_hint, tag_open, tag_close):
        self.special_tokens = {
            TokenType.Eval: eval_hint,
            TokenType.TagOpen: tag_open,
            TokenType.TagClose: tag_close
        }

    def __make_flat_tokens(self, text):
        flat_tokens = []
        current_type = None
        escaped = False
        escaped_index = -1
        current_token = ''

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
                current_token += c
            else:
                if len(current_token) > 0:
                    flat_tokens.append(Token(previous_type, current_token))

                current_token = c
                escaped_index = -1

            if escaped:
                escaped = False
                escaped_index = len(current_token) - 1

            for delim_type in self.special_tokens:
                delim = self.special_tokens[delim_type]

                if len(current_token) - escaped_index <= len(delim):
                    continue

                if current_token[-len(delim) :] != delim:
                    continue

                if len(current_token) > len(delim):
                    flat_tokens.append(
                        Token(TokenType.Text, current_token[: -len(delim)]))

                flat_tokens.append(Token(delim_type, current_token[-len(delim) :]))
                current_token = ''
                escaped_index = -1
                break

        if len(current_token) > 0:
            flat_tokens.append(Token(current_type, current_token))

        return flat_tokens

    def __make_block_tokens(self, flat_tokens):
        stack = []
        block_tokens = TokenCollection()

        for token in flat_tokens:
            if token.t_type is TokenType.TagOpen:
                # Subsequent tokens will be added to this new block
                stack.append(BlockToken(self.special_tokens[TokenType.TagOpen],
                                        self.special_tokens[TokenType.TagClose],
                                        None))
            else:
                if token.t_type is TokenType.TagClose:
                    if len(stack) == 0:
                        Util.error("Found extra closing tag")

                    # Got the closing tag, pop the block from the stack
                    token = stack.pop()

                if len(stack) > 0:
                    stack[-1].tokens.add_token(token)
                else:
                    block_tokens.add_token(token)

        if len(stack) > 0:
            Util.error("Missing closing tag")

        return block_tokens

    def tokenize(self, text):
        flat_tokens = self.__make_flat_tokens(text)
        block_tokens = self.__make_block_tokens(flat_tokens)

        return block_tokens
