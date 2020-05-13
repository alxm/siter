# Siter

Siter is a static website generator written in Python 3, "Markdown with macros and variables" for my [own simple needs](https://www.alxm.org/ "My personal website is made with Siter").

## What Does It Do?

```sh
$ siter new mywebsite

$ tree mywebsite/
mywebsite/
├── siter-config/   # Global definitions
├── siter-out/      # The final generated website
├── siter-pages/    # Markdown source pages to be processed
│   └── index.md
├── siter-static/   # Static files copied as they are
└── siter-template/ # HTML templates
    └── page.html
```

* To build, `cd mywebsite` and call `siter [gen | run | serve]`.
* Files and directories from `siter-static` are copied to `siter-out` as they are.
* Markdown files from `siter-pages` are evaluated, formatted, fitted in `siter-template/page.html`, and finally written to `siter-out` as HTML pages.
* Files from `siter-config` contain global definitions that are available during page generation.

### Quick Example

A source page `siter-pages/index.md`,

```md
{{!def {{title}} {{Home}}}}

# Hello world!

This page is called *{{!title}}*.
```

Combined with the page template `siter-template/page.html`,

```html
<html>
    <head>
        <title>{{!title}}</title>
    </head>
    <body>
        {{!md {{!content}}}}
    </body>
</html>
```

Are used to make `siter-out/index.html`:

```html
<html>
    <head>
        <title>Home</title>
    </head>
    <body>
        <h1>Hello world!</h1>
        <p>This page is called <em>Home</em>.</p>
    </body>
</html>
```

## Blocks, Variables, Macros, Functions

A block is text enclosed between `{{` and `}}`. If the first character in a block is the eval marker `!`, then the block is evaluated as a variable or macro. So `{{!modified %Y}}` might expand to `2011` if you travelled back in time, but `{{modified %Y}}` would just be replaced with the literal `modified %Y`.

### Macros Example

```md
{{!def {{album}} {{image_elements}} {{
    <div>
        {{!image_elements}}
    </div>
}}}}

{{!def {{image}} {{filename description}} {{
    <img src="images/{{!filename}}" title="{{!description}}">
}}}}

{{!album
    {{!image {{landscape.jpg}} {{A painting}}}}
    {{!image {{ufo.jpg}} {{A photo}}}}
}}
```

Becomes

```html
<div>
    <img src="images/landscape.jpg" title="A painting">
    <img src="images/ufo.jpg" title="A photo">
</div>
```

When a macro takes a single argument like `album` does above, you may ommit block tags around the argument.

## Special Macros and Variables

These are the built-in definitions.

Variable | About | Example
--- | --- | ---
`content` | The evaluated page file, used by `siter-template/page.html`. | `<html><body>{{!content}}</body></html>`
`generated` | `YYYY-MM-DD` date when the output file was generated. | `<footer>Page generated on {{!generated}}</footer>`
`root` | Relative path from the current page to the website root, so you can reference static files from nested pages. | `<img src="{{!root}}/photos/cloud.jpg">`
`modified` | `YYYY-MM-DD` date when the source file was last modified. | `<footer>Page updated on {{!modified}}</footer>`

Macro | About | Example
--- | --- | ---
`anchor` | Makes the text argument suitable to use as an HTML anchor. | `<a href="#{{!anchor Hello World}}">Permalink</a>`
`apply` | Formats files from a `siter-stubs` subdir with a template file from `siter-template`. | `{{!apply {{news.html}} {{news}} {{5}}}}`
`datefmt` | Format a `YYYY-MM-DD` date with a Python [time format string](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes). | `<footer>Last updated {{!datefmt {{!modified}} {{%b %Y}}}}</footer>`
`def` | Bind a new macro or variable. | `{{!def {{page-title}} {{Home Page}}}}`
`if` | `{{!if {{flag}} {{then}} {{else}}}}` evaluates `{{then}}` if the `flag` variable was previously declared (`{{!def flag}}`), or to `{{else}}` otherwise. The else block is optional. | `{{!if {{show-heading}} {{<h1>Welcome!</h1>}}}}`
`md` | Runs Markdown on the supplied argument. | `{{!md **Hello world!**}}`

## Dependencies

Siter uses [Python-Markdown](https://python-markdown.github.io/) (with CodeHiliteExtension, FencedCodeExtension, and TocExtension) and [Pygments](https://pygments.org/) for text formatting and code syntax highlighting, along with *enum, http.server, os, shutil, socketserver, subprocess, sys, threading, time,* and *traceback* from the standard library.

```sh
sudo apt install python3 python3-markdown python3-pygments
```

## License

Copyright 2011-2020 Alex Margarit (alex@alxm.org)

Licensed under [GNU GPL 3.0](https://www.gnu.org/licenses/gpl.html) (see `COPYING`).
