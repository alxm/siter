Siter
=====

Siter is a static website generator written in Python.

Content pages from `siter-pages/` are formatted with `siter-template/page.html` and written to `siter-out/`. Pages can define variables and macros to avoid content and markup duplication.

Quick Example
=============

A content page

    {title Home page}
    ~~~
    <p>Hello world!</p>

and a page template

    <html>
        <body>
            <h1>{title}</h1>
            {s.content}
        </body>
    </html>

generate this:

    <html>
        <body>
            <h1>Home page</h1>
            <p>Hello world!</p>
        </body>
    </html>

Manual
======

File tree
---------

    website/
     |- siter-config/   # Optional config files
     |   |- ...
     |- siter-out/      # Generated pages are written here
     |   |- about.html
     |   |- index.html
     |   |- ...
     |- siter-pages/    # Content pages
     |   |- about.html
     |   |- index.html
     |   |- ...
     |- siter-template/ # HTML templates
         |- page.html

siter-config/
-------------

Configuration files that change default settings go here.

### defs

Variables and macros that can be used by all pages. See the example below for syntax. Variables and macros that start with `s.` are reserved and should not be defined by the user.

### marker

Siter pages start with variable and macro definitions, followed by a special marker. Everything following that marker is considered page content. The default marker is `~~~`, but you can specify a different one like `*****` in this file.

### out

Siter writes generated pages to `siter-out/`. You can specify a different output directory in this file.

### tags

Specifies custom opening and closing block tags (used for variable use and declaration), each on a separate line. The two tags must be different: `[` and `]` are ok, but `%` and `%` are not. Siter defaults to `{` and `}`.

siter-pages/
------------

Content pages go here. Example `siter-pages/about.html`:

    {title About}                 # Declare a variable
    ~~~                           # Content marker
    <p>This is a simple page.</p> # Page content starts from here on

siter-template/
---------------

`siter-template/page.html` is the template for all content pages. Example `siter-template/page.html`:

    <html>
        <head>
            <title>{title}</title> # Use variable declared by page
        </head>
        <body>
            <h1>{title}</h1>       # Use variable declared by page
            {s.content}            # Special variable for page content
        </body>
    </html>

Calling Siter
-------------

    cd website
    siter       # generate website
    siter force # regenerate all pages

License
-------

Copyright 2011 Alex Margarit (alex@alxm.org)

Licensed under GNU GPL3.
