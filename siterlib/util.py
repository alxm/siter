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

import sys, traceback

class CUtil:
    @staticmethod
    def message(Title, Content, Color = 2):
        space = max(2, 12 - len(Title))
        head = '■' * (space // 2)
        tail = '■' * (space - space // 2)

        print(f'\033[{30 + Color};1m{head} {Title} {tail}\033[0m {Content}')

    @staticmethod
    def error(Message):
        CUtil.message('Error', Message, 1)
        CUtil.message('Call Stack', '', 1)
        traceback.print_stack()
        sys.exit(1)

    @staticmethod
    def warning(Message):
        CUtil.message('Warning', Message, 3)

    @staticmethod
    def info(Message):
        CUtil.message('Info', Message, 4)
