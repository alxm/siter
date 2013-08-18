Siter
=====

Siter is a very simple static website generator written in Python.

Content from `siter-pages` is fitted in `siter-template/page.html` and rendered pages are written to the site's root directory. Pages can define variables and simple functions that the template and page can call. Variables and functions that start with `s.` are reserved for the program and should not be defined by pages.

See a simple example below. My [games website](https://github.com/alxm/alxm.github.com) uses Siter too.

Example
-------

### File tree

    website/
        siter-config/      # stores Siter config files
            tags           # optional file to specify custom block tags
        siter-pages/       # content pages
            about.html
            index.html
            ...
        siter-template/    # design template
            page.html
            style.css
            ...
        about.html         # generated page
        index.html         # generated page
        ...

### siter-config

Siter config files go in here.

#### tags

Specifies custom opening and closing tags, each on its own line. The two tags must be different: `[` and `]` are ok, but `%` and `%` are not. Siter defaults to `{{` and `}}`. I like using `(` and `)`, so my `tags` file would look like this:

    (
    )

### siter-pages

These are content pages that are fitted into a template file before site generation. For example,

#### index.html

    {{s.var title Home page}}
    {{s.var content
        Hello world!
    }}

#### about.html

    {{s.var title About}}
    {{s.var content
        <p>This is a very simple website.</p>
    }}

### siter-template

This is the design template, including HTML, CSS, and images. Content pages will be fitted into `page.html` at generation time.

#### page.html

    <html>
        <head>
            <link rel="stylesheet" type="text/css" href="./style.css" media="screen">
            <title>{{s.use title}}</title>
        </head>
        <body>
            <h1>{{s.use title}}</h1>
            {{s.use content}}
        </body>
    </html>

### Calling Siter

    cd website
    siter          # generate
    siter force    # regenerate all pages, even if they are up to date

### Example Output

The example above will generate `website/index.html` and `website/about.html`:

#### index.html

    <html>
        <head>
            <link rel="stylesheet" type="text/css" href="siter-template/style.css" media="screen">
            <title>Home page</title>
        </head>
        <body>
            <h1>Home page</h1>
            Hello world!
        </body>
    </html>

#### about.html

    <html>
        <head>
            <link rel="stylesheet" type="text/css" href="siter-template/style.css" media="screen">
            <title>About</title>
        </head>
        <body>
            <h1>About</h1>
            <p>This is a very simple website.</p>
        </body>
    </html>

License
-------

Copyright 2011 Alex Margarit (alex@alxm.org)

Licensed under GNU GPL3.
