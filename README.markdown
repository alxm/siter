Siter
=====

Siter is a very simple static website generator written in Python.

Content from `siter-pages` is fitted in `siter-template/page.html` and rendered pages are written to `siter-out`. Pages can define variables and functions that the template and page can call. Variables and functions that start with `s.` are reserved for the program and should not be defined by pages. Configuration files go in `siter-config`.

See a simple example below. My [own website](http://www.alxm.org) uses Siter too.

Example
-------

### File tree

    website/
     |
     |- siter-config/      # Siter config files, all are optional
     |   |
     |   |- defs           # Global variables and macros
     |   |- marker         # Custom content delimiter
     |   |- out            # Custom output dir
     |   |- tags           # Custom block tags
     |
     |- siter-out/         # Generated pages are written here
     |   |
     |   |- about.html
     |   |- index.html
     |   |
     |   |- nested/
     |       |
     |       |- page.html
     |
     |- siter-pages/       # Content pages
     |   |
     |   |- about.html
     |   |- index.html
     |   |
     |   |- nested/
     |       |
     |       |- page.html
     |
     |- siter-template/    # HTML templates
         |
         |- page.html

### siter-config/

Siter config files go in here.

#### defs

Variables and functions that are visible to all pages. See the `siter-pages` example below for syntax.

#### marker

Siter pages start with variable and function definitions, followed by a special marker. Everything following that marker is considered page content. The default marker is `~~~`, but you can specify a different one in this file. For example, if you'd prefer `*****` instead, then the `marker` file whould look like this:

    *****

#### out

Siter writes generated pages in `siter-out`. You can specify a different output directory in this file.

#### tags

Specifies custom opening and closing tags, each on its own line. The two tags must be different: `[` and `]` are ok, but `%` and `%` are not. Siter defaults to `{` and `}`. I like using `[` and `]`, so my `tags` file looks like this:

    [
    ]

### siter-pages/

These are content pages that are fitted into a template file before site generation. For example,

#### index.html

    {title Home page}
    ~~~
    <p>Hello world!</p>

#### about.html

    {title About}
    ~~~
    <p>This is a very simple website.</p>

### siter-template/

HTML templates live here. Content pages will be fitted into `page.html` at generation time.

#### page.html

    <html>
        <head>
            <title>{title}</title>
        </head>
        <body>
            <h1>{title}</h1>
            {s.content}
        </body>
    </html>

### Calling Siter

    cd website
    siter          # generate
    siter force    # regenerate all pages, even if they are up to date

### Example Output

The example above will generate `website/siter-out/index.html` and `website/siter-out/about.html`:

#### siter-out/index.html

    <html>
        <head>
            <title>Home page</title>
        </head>
        <body>
            <h1>Home page</h1>
            Hello world!
        </body>
    </html>

#### siter-out/about.html

    <html>
        <head>
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
