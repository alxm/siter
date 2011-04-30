#!/usr/bin/python

"""
    Copyright 2011 Alex Margarit

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

import copy, os, re, sys

class Block:
    re_variable = re.compile("(\w+)$")
    re_function = re.compile("(\w+)\s*\:(.*)$", re.DOTALL)

    def __init__(self, index, text):
        self.index = index
        self.whole = text
        self.contents = text[2 : -2].strip()

    def variable(self, bindings):
        match = Block.re_variable.match(self.contents)

        if match:
            variable = match.group()

            if variable in bindings:
                return variable

        return None

    def function(self, bindings):
        match = Block.re_function.match(self.contents)

        if match:
            function = match.group(1)
            arguments = match.group(2)

            if function in bindings:
                return (function, arguments)

        return None

def siter_error(error):
    print "[   Error!   ] " + error
    sys.exit(1)

def siter_get_blocks(text):
    blocks = []
    start = 0

    while True:
        index = text.find("{{", start)

        if index == -1:
            break

        count = 1

        last_open = False
        last_close = False

        for i in range(index + 2, len(text)):
            if text[i] == "{":
                if last_open:
                    count += 1
                    last_open = False
                else:
                    last_open = True
            else:
                last_open = False

            if text[i] == "}":
                if last_close:
                    count -= 1
                    last_close = False
                else:
                    last_close = True
            else:
                last_close = False

            if count == 0:
                start = i + 1
                blocks.append(Block(index, text[index : start]))
                break

        if count != 0:
            break

    return blocks

def siter_evaluate(text, bindings):
    blocks = siter_get_blocks(text)

    for block in blocks:
        variable = block.variable(bindings)
        function = block.function(bindings)

        if variable:
            (_, value) = bindings[variable]
            text = text.replace(block.whole, value, 1)
        elif function:
            (name, args) = function
            (params, body) = bindings[name]

            bindings2 = copy.copy(bindings)
            del bindings2[name]

            args = siter_evaluate(args, bindings2)
            args = [a.strip() for a in args.split(",,")]

            if len(args) != len(params):
                siter_error("Wrong number of arguments\n" + block.whole)

            for i in range(len(args)):
                for m in re.finditer("\{\{\s*" + params[i] + "\s*\}\}", body, re.DOTALL):
                    body = body.replace(m.group(), args[i], 1)

            body = siter_evaluate(body, bindings2)
            text = text.replace(block.whole, body, 1)

    return text

def siter(siter_dir):
    if not os.path.isdir(siter_dir):
        siter_error("Can't find dir " + siter_dir)

    siter_pages = siter_dir + "/siter-pages"
    siter_template = siter_dir + "/siter-template.html"

    if not os.path.isdir(siter_pages):
        siter_error("Can't find dir " + siter_pages)

    if not os.path.isfile(siter_template):
        siter_error("Can't find file " + siter_template)

    template = None

    with open(siter_template, "r") as f:
        template = f.read()

    for page_file in os.listdir(siter_pages):
        read_file = siter_pages + "/" + page_file
        write_file = siter_dir + "/" + page_file

        if os.path.isfile(write_file):
            read_date = os.stat(read_file)[8]
            write_date = os.stat(write_file)[8]
            template_date = os.stat(siter_template)[8]

            if read_date < write_date and template_date < write_date:
                print "[ Up to date ] " + write_file
                continue

        print "[  Updating  ] " + write_file

        header = ""
        content = ""

        with open(read_file, "r") as r:
            in_header = True

            for line in r:
                if in_header and line.strip() == "":
                    in_header = False
                    continue

                if in_header:
                    header += line
                else:
                    content += line

        start = 0
        bindings = {}

        match_asg = re.compile("(.*)=\s*$", re.DOTALL)
        match_var = re.compile("(\w+)$", re.DOTALL)
        match_fun = re.compile("(\w+)\s*\((.*)\)$", re.DOTALL)

        for block in siter_get_blocks(header):
            m_asg = match_asg.match(header[start : block.index].strip())

            if not m_asg:
                siter_error("Missing assignment\n"
                    + header[start : block.index + len(block.whole)].strip())

            lhs = m_asg.group(1).strip()

            m_var = match_var.match(lhs)
            m_fun = match_fun.match(lhs)

            if m_var:
                name = m_var.group(1)
                bindings[name] = (None, block.contents)
            elif m_fun:
                name = m_fun.group(1)
                params = [p.strip() for p in m_fun.group(2).split(",")]
                bindings[name] = (params, block.contents)
            else:
                siter_error("Syntax error\n" + lhs)

            start = block.index + len(block.whole)

        bindings["page"] = (None, siter_evaluate(content, bindings))
        page = siter_evaluate(template, bindings)

        with open(write_file, "w") as w:
            w.write(page)

if __name__ == "__main__":
    siter("." if len(sys.argv) < 2 else sys.argv[1])
