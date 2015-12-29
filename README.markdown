# Siter

Siter is a static website generator written in Python 3. I made it for my own simple needs and as a way to play with Python.

Content pages from `siter-pages/` are formatted with `siter-template/page.html` and written to `siter-out/`. Files from `siter-static/` are copied to `siter-out/` as they are. You can define variables and macros to avoid content and markup duplication.

# Quick Example

A content page:

    {!def {title} {Home page}}

    Hello world!

    This is my {!title}.

And a page template:

    <html>
        <body>
            <h1>{!title}</h1>
            {!content}
        </body>
    </html>

Generate this:

    <html>
        <body>
            <h1>Home page</h1>
            <p>Hello world!</p>
            <p>This is my Home page.</p>
        </body>
    </html>


# Blocks, Variables, Macros, and Functions

A block is text enclosed in block tags. The default block tags are `{` and `}`, but you can override them with the `siter-config/tags` file which is described further down.

A block may be used to define variables and macros, as well as to invoke them. A block that starts with the evaluation marker `!` is interpreted as a call to a particular definition.

In the example below, we call the built-in `def` function to create a new variable `smile` and a new macro `format` that takes the arguments `tag` and `text`. Afterwards, we use them with `{!smile}` and `{!format ...}` respectively:

    {!def {smile} {:-)}}
    {!def {format} {tag text} {<{!tag}>{!text}</{!tag}>}}

    {!format {b} {This text is bold {!smile}}}

    {!format {i} {This text is italic}}

This will output:

    <p><b>This text is bold :-)</b></p>
    <p><i>This text is italic</i></p>

The `tag` and `text` arguments are defined as local variables in the context of `format`'s body. If a macro or function takes a single argument, you may ommit the block tags around the argument:

    {!def
        {bold}
        {text}
        {<b>{!text}</b>}
    }
    {!bold This line is bold}
    {!bold {And so is this one}}

# Special Macros and Variables

### content

Everything in a page file that is not a variable or macro definition, ran through Markdown.

### root

Relative path from the current page to the website root, so you can reference static files from nested pages.

### modified

Time the page content was modified. Takes a Python [time format](http://strftime.org/) string as parameter. For example, `{!modified {%B %Y}}` expands to something like `September 2015`.

### generated

Time the page was generated. Same argument as `modified`.

### code

For displaying code blocks and one-liners. See the [Pygments docs](http://pygments.org/docs/lexers/) for supported languages. There are three ways to call this macro, here are some examples:

##### No syntax highlighting

    {!code {int x = 0;}}

##### Use C syntax highlighting

    {!code {c} {int x = 0;}}

##### Use Python syntax and select lines 2 and 5

    {!code {py} {2 5} {
    try:
        with open(read_file, 'rU') as f:
            text = f.read()
    except FileNotFoundError:
        return None
    }}

### md

`{!md ...}` - Runs the supplied argument through Markdown.

### if

`{!if {flag} {then} {else}}` - Expands to the `then` block if the `flag` variable has been declared somewhere (say with `{!def flag}`), or to the `else` block otherwise. The `else` block is optional.

# Project File Tree

    website/
     |- siter-config/   # Optional config files
     |   '- ...
     |- siter-out/      # Pages and files get written here
     |   |- about.html
     |   |- index.html
     |   '- ...
     |- siter-pages/    # Content pages processed by Siter
     |   |- about.html
     |   |- index.html
     |   '- ...
     |- siter-static/   # Static files like CSS and images
     |   '- ...
     '- siter-template/ # HTML templates
         '- page.html

### siter-config/

Configuration files that change default settings go here.

##### siter-config/defs

For declaring global variables and macros visible to all pages.

##### siter-config/eval

The default eval marker is `` ` ``, but you can declare a custom one like `!` in this file. Blocks that start with an eval mark are evaluated as variables or macros, while the rest expand to their literal selves. So `{!modified %Y}` would expand to `2015`, while `{modified}` would expand to `modified`.

##### siter-config/tags

Tags are used to delimitate blocks. `{` and `}` are the default, but you can specify your own in this file, each on a separate line. The two tags must be different: `[` and `]` are ok, but `%` and `%` are not. Multi-character tags like like `{{` and `}}` are valid too.

### siter-pages/

Content pages go here. Example `siter-pages/about.html` that would be processed and written to `siter-out/about.html`:

    {!def {title} {About}}        # Declare a variable
    <p>This is a simple page.</p> # Page content

### siter-template/

##### siter-template/page.html

This is the template for every page. Example:

    <html>
        <head>
            <title>{!title}</title> # Use var declared by page
        </head>
        <body>
            <h1>{!title}</h1>       # Use var declared by page
            {!content}              # Use special built-in var
        </body>
    </html>

# Calling Siter

    $ cd website-project
    $ siter

# Optional Packages

Siter uses [Markdown](https://pythonhosted.org/Markdown/) for text formatting and [Pygments](http://pygments.org/) for code syntax highlighting, if they are available.

    apt-get install python3-markdown
    apt-get install python3-pygments

# License

Copyright 2011 Alex Margarit (alex@alxm.org)

Licensed under GNU GPL3.
