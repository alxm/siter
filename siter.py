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

def siter(siter_dir):
    siter_pages = siter_dir + "/siter-pages"
    siter_template = siter_dir + "/siter-template.html"

    if not os.path.isdir(siter_pages):
        siter_error("Can't find siter-pages dir: " + siter_pages)

    if not os.path.isfile(siter_template):
        siter_error("Can't find siter-template.html: " + siter_template)

    template = None

    with open(siter_template, "r") as f:
        template = string.Template(f.read())

    varbinder = re.compile("(.+?)=(.*)")

    for page_file in os.listdir(siter_pages):
        read_file = siter_pages + "/" + page_file
        write_file = siter_dir + "/" + page_file

        with open(read_file, "r") as f:
            print "Reading " + read_file

            doing_bindings = True
            bindings = {}
            page = ""

            for line in f:
                if doing_bindings:
                    match = varbinder.search(line)

                    if match:
                        bindings[match.group(1).strip()] = match.group(2).strip()
                    else:
                        doing_bindings = False
                        page = page + line
                else:
                    page = page + line

            bindings["page"] = page

            with open(write_file, "w") as p:
                print "Writing " + write_file
                p.write(template.safe_substitute(bindings))

def siter_error(error):
    print "Siter Error: " + error
    sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        siter_error("Usage: " + sys.argv[0] + " PathToSite")

    siter_dir = sys.argv[1]

    if not os.path.isdir(siter_dir):
        siter_error("Can't find dir: " + siter_dir)

    siter(siter_dir)
