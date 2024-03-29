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

from .settings import *
from .token import *
from .util import *

class CTokenizer:
    def _make_flat_tokens(Text):
        flat_tokens = []
        current_type = None
        current_text = []

        def add_token(Token):
            if len(flat_tokens) == 0:
                flat_tokens.append(Token)
            else:
                last_token = flat_tokens[-1]

                if type(last_token) == CTokenEscape \
                    and isinstance(Token, CTokenMarker):

                    flat_tokens[-1] = CTokenText(Token.DefaultText)
                else:
                    flat_tokens.append(Token)

        for current_char in Text:
            previous_type = current_type

            if current_char.isspace():
                current_type = CTokenWhitespace
            else:
                current_type = CTokenText

            if current_type is previous_type:
                current_text.append(current_char)
            else:
                if len(current_text) > 0:
                    add_token(previous_type(''.join(current_text)))

                current_text = [current_char]

            for token_type in \
                [CTokenTagOpen, CTokenTagClose, CTokenEval, CTokenEscape]:

                token_text = token_type.DefaultText

                if len(current_text) < len(token_text):
                    continue

                if ''.join(current_text[-len(token_text) :]) != token_text:
                    continue

                if len(current_text) > len(token_text):
                    add_token(
                        CTokenText(''.join(current_text[: -len(token_text)])))

                add_token(token_type())

                current_text = []

                break

        if len(current_text) > 0:
            add_token(current_type(''.join(current_text)))

        return flat_tokens

    def _make_block_tokens(FlatTokens):
        stack = []
        block_tokens = CTokenCollection()

        for token in FlatTokens:
            if type(token) is CTokenTagOpen:
                # Subsequent tokens will be added to this new block
                stack.append(CTokenBlock(CTokenCollection()))
            else:
                if type(token) is CTokenTagClose:
                    if len(stack) == 0:
                        CUtil.error('Found extra closing tag')

                    # Got the closing tag, pop the block from the stack
                    token = stack.pop()

                if len(stack) > 0:
                    stack[-1].tokens.add_token(token)
                else:
                    block_tokens.add_token(token)

        if len(stack) > 0:
            CUtil.error('Missing closing tag')

        return block_tokens

    def tokenize(Text):
        flat_tokens = CTokenizer._make_flat_tokens(Text)
        block_tokens = CTokenizer._make_block_tokens(flat_tokens)

        return block_tokens

    def text(Text):
        return CTokenCollection([CTokenText(Text)])
