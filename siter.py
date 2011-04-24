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

def siter_error(error):
    print "Siter Error: " + error
    sys.exit(1)

def siter_evaluate(text, variables, functions):
    for v in variables:
        text = text.replace("{{" + v + "}}", variables[v])

    queue = []
    start_looking = 0

    while start_looking != -1:
        call_start = text.find("{{", start_looking)

        if call_start == -1:
            break

        args_start = text.find(":", call_start)

        if args_start == -1:
            break

        function = text[call_start + 2 : args_start]

        if function not in functions:
            start_looking = call_start + 2
            continue

        count = 1

        last_open = False
        last_close = False

        for i in range(args_start + 1, len(text)):
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
                call = text[call_start : i + 1]
                inside = text[args_start + 1 : i - 1]

                queue.append((call, function, inside))
                start_looking = i + 1

                break

    for (call, f, inside) in queue:
        (params, body) = functions[f]

        functions2 = copy.copy(functions)
        del functions2[f]

        args = siter_evaluate(inside, variables, functions2).split(",,")

        if len(args) != len(params):
            siter_error("Wrong number of arguments in " + f)

        evaluated = body

        for i in range(0, len(args)):
            evaluated = evaluated.replace("{{" + params[i] + "}}", args[i].strip())

        evaluated = siter_evaluate(evaluated, variables, functions2)
        text = text.replace(call, evaluated)

    return text

def siter(siter_dir):
    if not os.path.isdir(siter_dir):
        siter_error("Can't find dir: " + siter_dir)

    siter_pages = siter_dir + "/siter-pages"
    siter_template = siter_dir + "/siter-template.html"

    if not os.path.isdir(siter_pages):
        siter_error("Can't find siter-pages dir: " + siter_pages)

    if not os.path.isfile(siter_template):
        siter_error("Can't find siter-template.html: " + siter_template)

    template = None

    with open(siter_template, "r") as f:
        template = f.read()

    re_define = re.compile("(.+?)=(.*)")      # id = value
    re_function = re.compile("(.+?)\((.*)\)") # func(args)

    for page_file in os.listdir(siter_pages):
        read_file = siter_pages + "/" + page_file
        write_file = siter_dir + "/" + page_file

        with open(read_file, "r") as r:
            doing_bindings = True

            variables = {}
            functions = {}
            page = ""

            for line in r:
                if doing_bindings:
                    # scan for id = value
                    match = re_define.search(line)

                    if match:
                        name = match.group(1).strip()
                        value = match.group(2).strip()

                        # scan for func(args), originally func(args) = value
                        match = re_function.search(name)

                        if match:
                            name = match.group(1).strip()
                            params = match.group(2).strip()

                            functions[name] = (params.split(", "), value)
                        else:
                            variables[name] = value
                    else:
                        doing_bindings = False
                        page = page + line
                else:
                    page = page + line

            variables["page"] = page

            # replace variables and functions
            page = siter_evaluate(template, variables, functions)

            with open(write_file, "w") as w:
                print "Writing " + write_file
                w.write(page)

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        siter(sys.argv[1])
    else:
        siter(".")
