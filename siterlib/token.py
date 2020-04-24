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

class CTokenType(enum.Enum):
    Text = 1
    Whitespace = 3
    TagOpen = 4
    TagClose = 5
    Block = 6
    Eval = 7

class CToken:
    def __init__(self, Type, Text):
        self.t_type = Type
        self.text = Text

    def __str__(self):
        return self.resolve()

    def resolve(self):
        return self.text

class CBlockToken(CToken):
    def __init__(self, TagOpen, TagClose, Tokens):
        super().__init__(CTokenType.Block, None)

        self.tag_open = TagOpen
        self.tag_close = TagClose
        self.tokens = Tokens if Tokens else CTokenCollection()

    def resolve(self):
        return self.tag_open + self.tokens.resolve() + self.tag_close

    def capture_call(self):
        # {{!name ...}}
        head, _ = self.tokens.capture(CTokenType.Eval, CTokenType.Text)

        return head.get_token(1).resolve() if head else None

    def capture_args(self, SingleArg):
        # {{!name {{arg1}} {{arg2}} ...}}
        _, tail = self.tokens.capture(CTokenType.Eval, CTokenType.Text)

        if tail is None or tail.num_tokens() == 0:
            return []

        args = tail.filter(CTokenType.Block)

        if SingleArg or len(args) == 0:
            # Put all the args in a parent block
            tail.trim()
            args = [CBlockToken(self.tag_open, self.tag_close, tail)]

        return args

class CTokenCollection:
    def __init__(self, Tokens = None):
        self.tokens = Tokens if Tokens else []

    def __iter__(self):
        return self.tokens.__iter__()

    def num_tokens(self):
        return len(self.tokens)

    def get_token(self, Index):
        return self.tokens[Index]

    def add_token(self, Token):
        self.tokens.append(Token)

    def add_tokens(self, Tokens):
        self.tokens += Tokens

    def add_collection(self, Collection):
        self.tokens += Collection.tokens

    def resolve(self):
        return ''.join([t.resolve() for t in self.tokens])

    def filter(self, Type):
        return [t for t in self.tokens if t.t_type is Type]

    def trim(self):
        start = 0
        end = len(self.tokens)

        for t in self.tokens:
            if t.t_type is CTokenType.Whitespace:
                start += 1
            else:
                break

        for t in reversed(self.tokens):
            if t.t_type is CTokenType.Whitespace:
                end -= 1
            else:
                break

        self.tokens = self.tokens[start : end]

    def capture(self, *Args):
        i = 0
        head = CTokenCollection()

        for arg in Args:
            found = False

            while i < len(self.tokens):
                token = self.tokens[i]
                i += 1

                if token.t_type is arg:
                    found = True
                    head.add_token(token)

                    break
                elif token.t_type is not CTokenType.Whitespace:
                    break

            if not found:
                return None, None

        # Capture the remaining tokens
        tail = CTokenCollection(self.tokens[i:])

        return head, tail
