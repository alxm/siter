# Siter

Siter is a static website generator written in Python 3. I wrote it for my own simple needs and as a way to play with Python.

Content pages from `siter-pages/` are formatted with `siter-template/page.html` and written to `siter-out/`. You can define variables and macros to avoid content and markup duplication.

# Quick Example

A content page:

    {var title Home page}
    ~~~
    Hello world!

And a page template:

    <html>
        <body>
            <h1>{!title}</h1>
            {!s.content}
        </body>
    </html>

Generate this:

    <html>
        <body>
            <h1>Home page</h1>
            <p>Hello world!</p>
        </body>
    </html>


# Variables and Macros

    {var smile :-)}
    {fun format {tag text} <{!tag}>{!text}</{!tag}>}
    ~~~
    {!format {b} {This text is bold {!smile}}}
    {!format {i} {This text is italic.}}

Will give you:

    <b>This text is bold :-)</b>
    <i>This text is italic.</i>

# Special Variables

#### s.content

Everything in a page file after the `~~~` content marker.

#### s.root

Relative path from the current page to the website root.

# Special Macros

#### s.modified

Time the page content was modified. Takes a Python [time format](http://strftime.org/) string as parameter. Example: `{!s.modified {%B %Y}}`

#### s.generated

Time the page was generated. Same argument as `s.modified`.

#### s.code

For displaying code blocks and one-liners. See the [Pygments docs](http://pygments.org/docs/lexers/) for supported languages. There are three ways to call this macro, here are some examples:

##### No syntax highlighting

    {!s.code {int x = 0;}}

##### Use C syntax highlighting

      {!s.code {c} {int x = 0;}}

##### Use Python syntax and mark lines 2 and 5

    {!s.code {py} {2 5} {
    try:
        with open(read_file, 'rU') as f:
            text = f.read()
    except FileNotFoundError:
        return None
    }}

#### s.if

`{!s.if {flag} {a} {b}}` - Expands to the `a` block if the `flag` variable has been declared somewhere, or to the `b` block otherwise. The `b` block is optional.

# Project File Tree

    website/
     |- siter-config/   # Optional config files
     |   '- ...
     |- siter-out/      # Generated pages written here
     |   |- about.html
     |   |- index.html
     |   '- ...
     |- siter-pages/    # Content pages read by Siter
     |   |- about.html
     |   |- index.html
     |   '- ...
     |- siter-static/   # Files copied to siter-out as they are
     |   '- ...
     '- siter-template/ # HTML templates
         '- page.html

### siter-config/

Configuration files that change default settings go here.

#### defs

Variables and macros visible by all pages. This avoids having to declare the same variables and macros in multiple pages.

#### marker

Siter pages start with variable and macro definitions, followed by a special marker. Everything following that marker is considered page content. The default marker is `~~~`, but you can specify a different one like `*****` in this file.

#### tags

Tags are used to indicate variable and macro blocks, `{` and `}` are the default. You can specify your own in this file, each on a separate line. The two tags must be different: `[` and `]` are ok, but `%` and `%` are not.

### siter-pages/

Content pages go here. Example `siter-pages/about.html`:

    {var title About}             # Declare a variable
    ~~~                           # Content marker
    <p>This is a simple page.</p> # Page content starts

### siter-template/

`siter-template/page.html` is the template for every page.

    <html>
        <head>
            <title>{!title}</title> # Use var declared by page
        </head>
        <body>
            <h1>{!title}</h1>       # Use var declared by page
            {!s.content}            # Use special built-in var
        </body>
    </html>

# Calling Siter

    cd website
    siter       # generate website
    siter force # regenerate all pages

# Optional Packages

Siter tries to use [Markdown](https://pythonhosted.org/Markdown/) for text formatting and [Pygments](http://pygments.org/) for code syntax highlighting.

    apt-get install python3-markdown
    apt-get install python3-pygments

# License

Copyright 2011 Alex Margarit (alex@alxm.org)

Licensed under GNU GPL3.
