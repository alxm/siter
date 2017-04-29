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

from siterlib.token import TokenType, TokenCollection
from siterlib.util import Util

class Functions:
    @staticmethod
    def declare_binding(siter, args):
        if len(args) == 3:
            # {name} {arg1 arg2 ...} {body}
            name = args[0].tokens.get_token(0).resolve()
            params = args[1].tokens.filter(TokenType.Text)
            body = [args[2]]

            siter.bindings.add_macro(name, params, TokenCollection(body))
        else:
            # {name} / {name} {body}
            name = args[0].tokens.get_token(0).resolve()
            body = [args[1]] if len(args) == 2 else []

            siter.bindings.add_variable(name, TokenCollection(body))

        return None

    @staticmethod
    def if_check(siter, args):
        clause = siter.evaluate_block(args[0]).resolve()

        if siter.bindings.contains(clause):
            return args[1]
        elif len(args) == 3:
            return args[2]
        else:
            return None

    @staticmethod
    def mod_time(_, args):
        read_file = args[0]
        fmt = args[1]

        f_time = read_file.get_mod_time()
        time_obj = time.localtime(f_time)

        return time.strftime(fmt, time_obj)

    @staticmethod
    def gen_time(_, args):
        return time.strftime(args[0])

    @staticmethod
    def datefmt(_, args):
        iso_date = args[0]
        fmt_string = args[1]

        try:
            time_obj = time.strptime(iso_date, '%Y-%m-%d')
        except ValueError:
            Util.warning('Date not in YYYY-MM-DD format: {}'.format(iso_date))
            return iso_date

        return time.strftime(fmt_string, time_obj)

    @staticmethod
    def highlight_code(siter, args):
        if len(args) == 1:
            lang = 'text'
            code = args[0]
            lines = []
        elif len(args) == 2:
            lang = args[0].lower()
            code = args[1]
            lines = []
        elif len(args) == 3:
            lang = args[0].lower()
            code = args[2]
            lines = args[1].split()

        def clean_code(code):
            # Replace < and > with HTML entities
            code = code.replace('<', '&lt;')
            code = code.replace('>', '&gt;')
            return code

        if code.find('\n') == -1:
            # This is a one-liner
            code = '<code>{}</code>'.format(clean_code(code))
        else:
            # This is a code block
            div_class = 'siter_code'

            if siter.imports.Pygments:
                lexer = siter.imports.PygmentsLexers.get_lexer_by_name(lang)
                formatter = siter.imports.PygmentsFormatters.HtmlFormatter(
                    linenos = True, cssclass = div_class, hl_lines=lines)
                code = siter.imports.Pygments.highlight(code, lexer, formatter)
            else:
                code = '<div class="{}"><pre>{}</pre></div>' \
                    .format(div_class, clean_code(code))

        return code

    @staticmethod
    def markdown(siter, args):
        content = args[0]

        if siter.imports.Md:
            content = siter.imports.Md.markdown(content,
                                                output_format = 'html5')

        return content

    @staticmethod
    def lowercase(_, args):
        return args[0].lower()
