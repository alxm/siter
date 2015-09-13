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
    def __init__(self, t_type, settings, text = None, tokens = None):
        self.settings = settings
        self.t_type = t_type
        self.text = text
        self.tokens = tokens if tokens else []

    def __str__(self):
        return self.resolve()

    def resolve(self):
        if self.t_type is TokenType.Block:
            output = ''.join([t.resolve() for t in self.tokens])
            return self.settings.TagOpen + output + self.settings.TagClose
        else:
            return self.text

    def __capture(self, capture_rest, *args):
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

                if token.t_type is not TokenType.Whitespace:
                    break

            if not found:
                return None

        if capture_rest:
            # Capture all the remaining tokens into a list
            results.append(self.tokens[i:])

        return results

    def capture_call(self):
        # {`name ...}
        results = self.__capture(False, TokenType.Eval, TokenType.Text)
        return results[1].resolve() if results else None

    def capture_args(self, single_arg):
        # {`name {arg1} {arg2} ...}
        results = self.__capture(True, TokenType.Eval, TokenType.Text)

        if results is None or len(results[2]) == 0:
            return []

        args = [t for t in results[2] if t.t_type is TokenType.Block]

        if single_arg or len(args) == 0:
            # Put all the args in a parent block if we only want a single arg,
            # or if there were no blocks in the args.
            args = [Token(TokenType.Block, self.settings, tokens = results[2])]

        return args

class TokenCollection:
    def __init__(self, tokens = None):
        self.tokens = tokens if tokens else []

    def get_tokens(self):
        return self.tokens

    def add_tokens(self, tokens):
        self.tokens += tokens

    def resolve(self):
        return ''.join([t.resolve() for t in self.tokens])

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
