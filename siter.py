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

import os, re, string, sys

def siter_error(error):
    print "Siter Error: " + error
    sys.exit(1)

def siter_replace(text, bindings, functions):
    for b in bindings:
        text = string.replace(text, "${" + b + "}", bindings[b])

    for f in functions:
        (params, body) = functions[f]
        calls = re.finditer("\$\{" + f + "\((.+)\)\}", text)

        for call in calls:
            whole = call.group(0).strip()
            args = call.group(1).split("///")

            if len(args) != len(params):
                siter_error("Wrong number of arguments")

            body2 = body

            for i in range(0, len(args)):
                body2 = string.replace(body2, "${" + params[i] + "}", args[i])

            text = string.replace(text, whole, body2)

    return text

def siter(siter_dir):
    siter_pages = siter_dir + "/siter-pages"
    siter_template = siter_dir + "/siter-template.html"

    if not os.path.isdir(siter_pages):
        siter_error("Can't find siter-pages dir: " + siter_pages)

    if not os.path.isfile(siter_template):
        siter_error("Can't find siter-template.html: " + siter_template)

    template = None

    with open(siter_template, "r") as f:
        template = f.read()

    siter_re_define = re.compile("(.+?)=(.*)")      # id = value
    siter_re_function = re.compile("(.+?)\((.+)\)") # func(args)

    for page_file in os.listdir(siter_pages):
        read_file = siter_pages + "/" + page_file
        write_file = siter_dir + "/" + page_file

        with open(read_file, "r") as r:
            doing_bindings = True

            bindings = {}
            functions = {}
            page = ""

            for line in r:
                if doing_bindings:
                    # scan for id = value
                    match = siter_re_define.search(line)

                    if match:
                        name = match.group(1).strip()
                        value = match.group(2).strip()

                        # scan for func(args), originally func(args) = value
                        match = siter_re_function.search(name)

                        if match:
                            name = match.group(1).strip()
                            params = match.group(2).strip()

                            functions[name] = (params.split(", "), value)
                        else:
                            bindings[name] = value
                    else:
                        doing_bindings = False
                        page = page + line
                else:
                    page = page + line

            # replace variables inside page content
            bindings["page"] = siter_replace(page, bindings, functions)

            # replace variables inside template
            page = siter_replace(template, bindings, functions)

            with open(write_file, "w") as w:
                print "Writing " + write_file
                w.write(page)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        siter_error("Usage: " + sys.argv[0] + " PathToSite")

    siter_dir = sys.argv[1]

    if not os.path.isdir(siter_dir):
        siter_error("Can't find dir: " + siter_dir)

    siter(siter_dir)
