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
from .util import *

class CBinding:
    def __init__(self):
        self.protected = False

class CBindingVariable(CBinding):
    def __init__(self, Tokens):
        self.tokens = Tokens

class CBindingMacro(CBinding):
    def __init__(self, Siter, Params, Tokens):
        num_required = len(Params)
        params = [p.resolve() for p in Params]

        for i, p in enumerate(params):
            if p == CSettings.OptDelimiter:
                num_required = i
                del params[i]

                break

        self.params = params
        self.num_params = len(params)
        self.num_params_req = num_required
        self.tokens = Tokens

class CBindingFunction(CBinding):
    def __init__(self, NumParams, Func, Lazy):
        self.num_params = NumParams
        self.func = Func
        self.lazy = Lazy

class CBindingCollection:
    def __init__(self, Siter):
        self.siter = Siter
        self.bindings = {}
        self.stack = []

    def contains(self, Name):
        return Name in self.bindings

    def _add(self, Name, Binding, Protected):
        if self.contains(Name) and self.get(Name).protected:
            CUtil.error(f'Cannot overwrite binding {Name}')

        Binding.protected = Protected
        self.bindings[Name] = Binding

    def add_variable(self, Name, Tokens, Protected = False):
        binding = CBindingVariable(Tokens)
        self._add(Name, binding, Protected)

    def add_macro(self, Name, params, Tokens, Protected = False):
        binding = CBindingMacro(self.siter, params, Tokens)
        self._add(Name, binding, Protected)

    def add_function(self, Name, NumParams, Func,
                     Protected = False, Lazy = False):
        binding = CBindingFunction(NumParams, Func, Lazy)
        self._add(Name, binding, Protected)

    def get(self, Name):
        if Name not in self.bindings:
            CUtil.error(f'{Name} not in bindings')

        return self.bindings[Name]

    def push(self):
        self.stack.append(self.bindings.copy())

    def pop(self):
        self.bindings = self.stack.pop()
