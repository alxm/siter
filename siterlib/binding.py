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

class BindingType(enum.Enum):
    Variable = 0
    Macro = 1
    Function = 2

class Binding:
    def __init__(self, b_type, tokens = None, num_params = None, params = None, func = None):
        self.b_type = b_type
        self.tokens = tokens
        self.num_params = [len(params)] if params else num_params
        self.params = params
        self.func = func
