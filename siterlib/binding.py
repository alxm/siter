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
    def __init__(self, tokens):
        self.tokens = tokens

class MacroBinding(Binding):
    def __init__(self, siter, params, tokens):
        num_required = len(params)

        for i, p in enumerate(params):
            if p.resolve() == siter.settings.OptDelimiter:
                num_required = i
                del params[i]
                break

        self.params = params
        self.num_params = len(params)
        self.num_params_req = num_required
        self.tokens = tokens

class FunctionBinding(Binding):
    def __init__(self, num_params, func, lazy):
        self.num_params = num_params
        self.func = func
        self.lazy = lazy

class BindingCollection:
    def __init__(self, siter):
        self.siter = siter
        self.bindings = {}
        self.stack = []

    def contains(self, name):
        return name in self.bindings

    def __add(self, name, binding, protected):
        if self.contains(name) and self.get(name).protected:
            Util.error('Cannot overwrite binding {}'.format(name))

        binding.protected = protected
        self.bindings[name] = binding

    def add_variable(self, name, tokens, protected = False):
        binding = VariableBinding(tokens)
        self.__add(name, binding, protected)

    def add_macro(self, name, params, tokens, protected = False):
        binding = MacroBinding(self.siter, params, tokens)
        self.__add(name, binding, protected)

    def add_function(self, name, num_params, func,
                     protected = False, lazy = False):
        binding = FunctionBinding(num_params, func, lazy)
        self.__add(name, binding, protected)

    def get(self, name):
        if name not in self.bindings:
            Util.error('{} not in bindings'.format(name))

        return self.bindings[name]

    def push(self):
        self.stack.append(self.bindings.copy())

    def pop(self):
        self.bindings = self.stack.pop()
