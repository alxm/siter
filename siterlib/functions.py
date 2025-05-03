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

import time

from .file import *
from .settings import *
from .token import *
from .util import *

class CFunctions:
    @staticmethod
    def declare_binding(Siter, Args):
        if len(Args) == 3:
            # `{{name}} {{arg1 arg2 ...}} {{body}}`
            name = Args[0].tokens.get_token(0).resolve()
            params = Args[1].tokens.filter(CTokenText)
            body = [Args[2]]

            Siter.bindings.add_macro(name, params, CTokenCollection(body))
        else:
            # `{{name}}` or `{{name}} {{body}}`
            name = Args[0].tokens.get_token(0).resolve()
            body = [Args[1]] if len(Args) == 2 else []

            Siter.bindings.add_variable(name, CTokenCollection(body))

        return CTokenBlock(CTokenCollection())

    @staticmethod
    def if_check(Siter, Args):
        clause = Siter.evaluate_block(Args[0]).resolve()

        if Siter.bindings.contains(clause):
            return Args[1]
        elif len(Args) == 3:
            return Args[2]
        else:
            return CTokenBlock(CTokenCollection())

    @staticmethod
    def datefmt(_, Args):
        iso_date = Args[0]
        fmt_string = Args[1]

        try:
            time_obj = time.strptime(iso_date, '%Y-%m-%d')
        except ValueError:
            CUtil.warning(f'Date not in YYYY-MM-DD format: {iso_date}')

            return iso_date

        return time.strftime(fmt_string, time_obj)

    @staticmethod
    def markdown(Siter, Args):
        return Siter.md.reset().convert(Args[0])

    @staticmethod
    def anchor(_, Args):
        return Args[0].lower().replace(' ', '-')

    @staticmethod
    def foreach(Siter, Args):
        a_stubs_dir = Args[0]
        a_template = Args[1]
        a_num_max = 0

        template_file = Siter.dirs.get(CSettings.DirTemplate) \
                            .get_file(a_template)
        stub_files = sorted(Siter.dirs.get(CSettings.DirForeach)
                                .get_dir_files(a_stubs_dir),
                            key = lambda f: f.name,
                            reverse = True)

        if len(Args) == 3:
            try:
                a_num_max = int(Args[2])
            except ValueError:
                CUtil.error(f'"{Args[2]}" is not an integer')

        if a_num_max > 0:
            stub_files = stub_files[: a_num_max]

        return ''.join([Siter.process_file(f, template_file, True)
                            for f in stub_files])
