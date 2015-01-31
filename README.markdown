# Siter

Siter is a static website generator written in Python 3.

Content pages from `siter-pages/` are formatted with `siter-template/page.html` and written to `siter-out/`. You can define variables and macros to avoid content and markup duplication.

# Quick Example

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


# Variables and Macros

    {smile :-)}
    {format {tag text} <{tag}>{text}</{tag}>}
    ~~~
    {format {b} {This text is bold! {smile}}}
    {format {i} {This text is italic.}}

**This text is bold! :-)** *This text is italic.*

# Special Variables

* `s.content` - Everything in a page file after the `~~~` marker.
* `s.root` - Relative path from the current page to the website root.
* `s.media` - Relative path from the current page to siter-media.

# Special Macros

* `s.modified` - Time the page content was modified. Takes a Python [time format](http://strftime.org/) string as parameter. Example: `{s.modified {%B %Y}}`
* `s.generated` - Time the page was generated. Same argument as `s.modified`.
* `s.code` - For displaying code blocks and one-liners. See the [Pygments docs](http://pygments.org/docs/lexers/) for supported languages. Examples:
    * `{s.code {int x = 0;}}`
    * `{s.code {C} {int x = 0;}}`

# Project File Tree

    website/
     |- siter-config/   # Optional config files
     |   '- ...
     |- siter-out/      # Generated pages written here
     |   |- about.html
     |   |- index.html
     |   '- ...
     |- siter-pages/    # Source content pages
     |   |- about.html
     |   |- index.html
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

    {title About}                 # Declare a variable
    ~~~                           # Content marker
    <p>This is a simple page.</p> # Page content starts

### siter-template/

`siter-template/page.html` is the template for every page.

    <html>
        <head>
            <title>{title}</title> # Use var declared by page
        </head>
        <body>
            <h1>{title}</h1>       # Use var declared by page
            {s.content}            # Use special built-in var
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
