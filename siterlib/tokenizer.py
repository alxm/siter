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
        current_token = ''

        special_tokens = {
            CTokenType.Eval: CSettings.EvalHint,
            CTokenType.TagOpen: CSettings.TagOpen,
            CTokenType.TagClose: CSettings.TagClose
        }

        for c in Text:
            if c == '\\' and not escaped:
                escaped = True

                continue

            previous_type = current_type

            if c in [' ', '\t', '\n']:
                current_type = CTokenType.Whitespace
            else:
                current_type = CTokenType.Text

            if current_type is previous_type:
                current_token += c
            else:
                if len(current_token) > 0:
                    flat_tokens.append(CToken(previous_type, current_token))

                current_token = c
                escaped_index = -1

            if escaped:
                escaped = False
                escaped_index = len(current_token) - 1

            for token_type in special_tokens:
                token_text = special_tokens[token_type]

                if len(current_token) - escaped_index <= len(token_text):
                    continue

                if current_token[-len(token_text) :] != token_text:
                    continue

                if len(current_token) > len(token_text):
                    text = current_token[: -len(token_text)]

                    flat_tokens.append(CToken(CTokenType.Text, text))

                flat_tokens.append(CToken(token_type,
                                          current_token[-len(token_text) :]))
                current_token = ''
                escaped_index = -1

                break

        if len(current_token) > 0:
            flat_tokens.append(CToken(current_type, current_token))

        return flat_tokens

    def __make_block_tokens(FlatTokens):
        stack = []
        block_tokens = CTokenCollection()

        for token in FlatTokens:
            if token.t_type is CTokenType.TagOpen:
                # Subsequent tokens will be added to this new block
                stack.append(CBlockToken(CTokenCollection()))
            else:
                if token.t_type is CTokenType.TagClose:
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
