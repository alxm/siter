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

class TokenType(enum.Enum):
    Text = 1
    Whitespace = 3
    TagOpen = 4
    TagClose = 5
    Block = 6
    Eval = 7

class Token:
    def __init__(self, t_type, text):
        self.t_type = t_type
        self.text = text

    def __str__(self):
        return self.resolve()

    def resolve(self):
        return self.text

class BlockToken(Token):
    def __init__(self, settings, tokens):
        super().__init__(TokenType.Block, None)

        self.settings = settings
        self.tokens = tokens if tokens else TokenCollection()

    def resolve(self):
        return self.settings.TagOpen + self.tokens.resolve() + self.settings.TagClose

    def capture_call(self):
        # {`name ...}
        head, _ = self.tokens.capture(TokenType.Eval, TokenType.Text)
        return head.get_token(1).resolve() if head else None

    def capture_args(self, single_arg):
        # {`name {arg1} {arg2} ...}
        _, tail = self.tokens.capture(TokenType.Eval, TokenType.Text)

        if tail is None or tail.num_tokens() == 0:
            return []

        args = tail.filter(TokenType.Block)

        if single_arg or len(args) == 0:
            # Put all the args in a parent block
            tail.trim()
            args = [BlockToken(self.settings, tail)]

        return args

class TokenCollection:
    def __init__(self, tokens = None):
        self.tokens = tokens if tokens else []

    def __iter__(self):
        return self.tokens.__iter__()

    def num_tokens(self):
        return len(self.tokens)

    def get_token(self, i):
        return self.tokens[i]

    def add_token(self, token):
        self.tokens.append(token)

    def add_tokens(self, tokens):
        self.tokens += tokens

    def add_collection(self, collection):
        self.tokens += collection.tokens

    def resolve(self):
        return ''.join([t.resolve() for t in self.tokens])

    def filter(self, t_type):
        return [t for t in self.tokens if t.t_type is t_type]

    def trim(self):
        start = 0
        end = len(self.tokens)

        for t in self.tokens:
            if t.t_type is TokenType.Whitespace:
                start += 1
            else:
                break

        for t in reversed(self.tokens):
            if t.t_type is TokenType.Whitespace:
                end -= 1
            else:
                break

        self.tokens = self.tokens[start : end]

    def capture(self, *args):
        i = 0
        head = TokenCollection()

        for arg in args:
            found = False

            while i < len(self.tokens):
                token = self.tokens[i]
                i += 1

                if token.t_type is arg:
                    found = True
                    head.add_token(token)
                    break
                elif token.t_type is not TokenType.Whitespace:
                    break

            if not found:
                return None, None

        # Capture the remaining tokens
        tail = TokenCollection(self.tokens[i:])

        return head, tail
