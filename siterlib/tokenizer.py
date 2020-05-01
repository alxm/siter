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

from .settings import *
from .token import *
from .util import *

class CTokenizer:
    def __make_flat_tokens(Text):
        flat_tokens = []
        current_type = None
        escaped = False
        escaped_index = -1
        current_text = []

        for current_char in Text:
            if current_char == '\\' and not escaped:
                escaped = True

                continue

            previous_type = current_type

            if current_char.isspace():
                current_type = CTokenWhitespace
            else:
                current_type = CTokenText

            if current_type is previous_type:
                current_text.append(current_char)
            else:
                if len(current_text) > 0:
                    flat_tokens.append(previous_type(''.join(current_text)))

                current_text = [current_char]
                escaped_index = -1

            if escaped:
                escaped = False
                escaped_index = len(current_text) - 1

            for token_type in [CTokenTagOpen, CTokenTagClose, CTokenEval]:
                token_text = token_type.DefaultText

                if len(current_text) - escaped_index <= len(token_text):
                    continue

                if ''.join(current_text[-len(token_text) :]) != token_text:
                    continue

                if len(current_text) > len(token_text):
                    flat_tokens.append(
                        CTokenText(''.join(current_text[: -len(token_text)])))

                flat_tokens.append(token_type())

                current_text = []
                escaped_index = -1

                break

        if len(current_text) > 0:
            flat_tokens.append(current_type(''.join(current_text)))

        return flat_tokens

    def __make_block_tokens(FlatTokens):
        stack = []
        block_tokens = CTokenCollection()

        for token in FlatTokens:
            if type(token) is CTokenTagOpen:
                # Subsequent tokens will be added to this new block
                stack.append(CTokenBlock(CTokenCollection()))
            else:
                if type(token) is CTokenTagClose:
                    if len(stack) == 0:
                        CUtil.error("Found extra closing tag")

                    # Got the closing tag, pop the block from the stack
                    token = stack.pop()

                if len(stack) > 0:
                    stack[-1].tokens.add_token(token)
                else:
                    block_tokens.add_token(token)

        if len(stack) > 0:
            CUtil.error("Missing closing tag")

        return block_tokens

    def tokenize(Text):
        flat_tokens = CTokenizer.__make_flat_tokens(Text)
        block_tokens = CTokenizer.__make_block_tokens(flat_tokens)

        return block_tokens

    def text(Text):
        return CTokenCollection([CTokenText(Text)])
