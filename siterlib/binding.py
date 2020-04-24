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

class Binding:
    def __init__(self):
        self.protected = False

class VariableBinding(Binding):
    def __init__(self, Tokens):
        self.tokens = Tokens

class MacroBinding(Binding):
    def __init__(self, Siter, Params, Tokens):
        num_required = len(Params)

        for i, p in enumerate(Params):
            if p.resolve() == Siter.settings.OptDelimiter:
                num_required = i
                del Params[i]

                break

        self.params = Params
        self.num_params = len(Params)
        self.num_params_req = num_required
        self.tokens = Tokens

class FunctionBinding(Binding):
    def __init__(self, NumParams, Func, Lazy):
        self.num_params = NumParams
        self.func = Func
        self.lazy = Lazy

class BindingCollection:
    def __init__(self, Siter):
        self.siter = Siter
        self.bindings = {}
        self.stack = []

    def contains(self, Name):
        return Name in self.bindings

    def __add(self, Name, Binding, Protected):
        if self.contains(Name) and self.get(Name).protected:
            Util.error(f'Cannot overwrite binding {Name}')

        Binding.protected = Protected
        self.bindings[Name] = Binding

    def add_variable(self, Name, Tokens, Protected = False):
        binding = VariableBinding(Tokens)
        self.__add(Name, binding, Protected)

    def add_macro(self, Name, params, Tokens, Protected = False):
        binding = MacroBinding(self.siter, params, Tokens)
        self.__add(Name, binding, Protected)

    def add_function(self, Name, NumParams, Func,
                     Protected = False, Lazy = False):
        binding = FunctionBinding(NumParams, Func, Lazy)
        self.__add(Name, binding, Protected)

    def get(self, Name):
        if Name not in self.bindings:
            Util.error(f'{Name} not in bindings')

        return self.bindings[Name]

    def push(self):
        self.stack.append(self.bindings.copy())

    def pop(self):
        self.bindings = self.stack.pop()
