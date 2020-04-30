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

import time

import pygments, pygments.lexers, pygments.formatters

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

        return None

    @staticmethod
    def if_check(Siter, Args):
        clause = Siter.evaluate_block(Args[0]).resolve()

        if Siter.bindings.contains(clause):
            return Args[1]
        elif len(Args) == 3:
            return Args[2]
        else:
            return None

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
    def highlight_code(Siter, Args):
        if len(Args) == 1:
            lang = 'text'
            code = Args[0]
            lines = []
        elif len(Args) == 2:
            lang = Args[0].lower()
            code = Args[1]
            lines = []
        elif len(Args) == 3:
            lang = Args[0].lower()
            code = Args[2]
            lines = Args[1].split()

        if code.find('\n') == -1:
            def clean_code(Code):
                # Replace special chars with HTML entities
                Code = Code.replace('<', '&lt;')
                Code = Code.replace('>', '&gt;')

                return Code

            # This is a one-liner
            code = f'<code>{clean_code(code)}</code>'
        else:
            # This is a code block
            lexer = pygments.lexers.get_lexer_by_name(lang)
            formatter = pygments.formatters.HtmlFormatter(
                            linenos = True,
                            cssclass = CSettings.PygmentsDiv,
                            hl_lines=lines)
            code = pygments.highlight(code, lexer, formatter)

        return code

    @staticmethod
    def markdown(Siter, Args):
        return Siter.md.reset().convert(Args[0])

    @staticmethod
    def anchor(_, Args):
        return Args[0].lower().replace(' ', '-')

    @staticmethod
    def apply_template(Siter, Args):
        out = ''

        templateFile = Siter.dirs.template.add_file(Args[0], CFileMode.Optional)
        stubsSubDir = Siter.dirs.stubs.add_dir(Args[1], CFileMode.Required)

        stubFiles = sorted(stubsSubDir.get_files(),
                           key = lambda f: f.get_name(),
                           reverse = True)

        if len(Args) == 3:
            stubFiles = stubFiles[: int(Args[2])]

        for f in stubFiles:
            out += Siter.process_file(f, stubsSubDir, templateFile, True)

        return out
