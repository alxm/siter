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

class CToken:
    def __str__(self):
        return self.resolve()

class CTokenText(CToken):
    def __init__(self, Text):
        self.text = Text

    def resolve(self):
        return self.text

class CTokenWhitespace(CTokenText):
    pass

class CTokenMarker(CToken):
    def resolve(self):
        return self.__class__.DefaultText

class CTokenTagOpen(CTokenMarker):
    DefaultText = CSettings.TagOpen

class CTokenTagClose(CTokenMarker):
    DefaultText = CSettings.TagClose

class CTokenEval(CTokenMarker):
    DefaultText = CSettings.EvalHint

class CTokenEscape(CTokenMarker):
    DefaultText = '\\'

class CTokenBlock(CToken):
    def __init__(self, Tokens):
        self.tokens = Tokens

    def resolve(self):
        return CSettings.TagOpen + self.tokens.resolve() + CSettings.TagClose

    def capture_call(self):
        # `!name ...`
        head, _ = self.tokens.capture(CTokenEval, CTokenText)

        return head.get_token(1).resolve() if head else None

    def capture_args(self, SingleArg):
        # `!name {{arg1}} {{arg2}} ...`
        _, tail = self.tokens.capture(CTokenEval, CTokenText)

        if tail is None or tail.num_tokens() == 0:
            return []

        args = tail.filter(CTokenBlock)

        if SingleArg or len(args) == 0:
            # Put all the args in a parent block
            tail.trim()
            args = [CTokenBlock(tail)]

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

    def add_collection(self, Collection):
        self.tokens += Collection.tokens

    def resolve(self):
        return ''.join([t.resolve() for t in self.tokens])

    def filter(self, Type):
        return [t for t in self.tokens if type(t) is Type]

    def trim(self):
        start = 0
        end = len(self.tokens)

        for t in self.tokens:
            if type(t) is CTokenWhitespace:
                start += 1
            else:
                break

        for t in reversed(self.tokens):
            if type(t) is CTokenWhitespace:
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

                if type(token) is arg:
                    found = True
                    head.add_token(token)

                    break
                elif type(token) is not CTokenWhitespace:
                    break

            if not found:
                return None, None

        # Capture the remaining tokens
        tail = CTokenCollection(self.tokens[i:])

        return head, tail
