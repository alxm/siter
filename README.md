# Siter

Siter is a static website generator written in Python 3, "Markdown with macros and variables" for [my own simple needs](https://www.alxm.org/ "My personal website is made with Siter").

## *Hello, World* Example

### Generate New Project

```sh
$ siter new hello-world

$ tree hello-world/
hello-world/
├── siter-pages
│   └── index.md
└── siter-template
    └── page.html

$ cat hello-world/siter-pages/index.md
{{!siter-def {{title}} {{Home Page}}}}
*Hello World!*

$ cat hello-world/siter-template/page.html
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="generator" content="Siter">
        <title>{{!title}}</title>
    </head>
    <body>
        {{!siter-md {{!siter-content}}}}
    </body>
</html>
```

### Generate HTML Pages

```sh
$ siter gen hello-world

$ tree hello-world/
hello-world/
├── siter-out
│   └── index.html
├── siter-pages
│   └── index.md
└── siter-template
    └── page.html

$ cat hello-world/siter-out/index.html
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="generator" content="Siter">
        <title>Home Page</title>
    </head>
    <body>
        <p><em>Hello World!</em></p>
    </body>
</html>
```

### Local Web Server

```sh
$ siter serve hello-world
```

## Blocks, Variables, Macros, Functions

A block is text enclosed between `{{` and `}}`. If the first character in a block is the evaluation marker `!`, then the block is evaluated as a macro or variable. So `{{!siter-modified %Y}}` might expand to `2099` if you're a time traveller, but `{{siter-modified %Y}}` without the `!` would just be replaced with the string literal `siter-modified %Y`.

### Macros Example

#### Define

```md
{{!siter-def {{image-album}} {{images}} {{
    <div>
        {{!images}}
    </div>
}}}}

{{!siter-def {{image-element}} {{file text}} {{
    <img src="media/{{!file}}" title="{{!text}}" alt="{{!text}}">
}}}}
```

#### Invoke

```md
{{!image-album
    {{!image-element {{landscape.jpg}} {{A painting}}}}
    {{!image-element {{ufo.jpg}} {{A photo}}}}
}}
```

#### Generate

```html
<div>
    <img src="media/landscape.jpg" title="A painting" alt="A painting">
    <img src="media/ufo.jpg" title="A photo" alt="A photo">
</div>
```

When a macro takes a single argument like `image-album` does above, you may ommit block tags around the argument for brevity.

## Special Macros and Variables

All the built-in definitions start with `siter-`.

Variable | About | Example
--- | --- | ---
`siter-content` | The evaluated page content, used by `siter-template/page.html`. | `<html><body>{{!siter-content}}</body></html>`
`siter-generated` | YYYY-MM-DD date when the HTML file in `siter-out` was generated. | `<footer>Page generated on {{!siter-generated}}</footer>`
`siter-modified` | YYYY-MM-DD date when the source file in `siter-pages` was last modified. | `<footer>Page updated on {{!siter-modified}}</footer>`
`siter-name` | The page file name without extension. | `<h1>{{!siter-name}}</h1>`
`siter-path` | The page file path relative from root. | `You are at {{!siter-path}}`
`siter-root` | Relative path from the current page to the website root, so you can reference static files from nested pages. | `<img src="{{!siter-root}}/photos/cloud.jpg">`

Macro | About | Example
--- | --- | ---
`siter-def` | Bind a new macro or variable. | `{{!siter-def {{page-title}} {{Home Page}}}}`
`siter-if` | `{{!siter-if {{flag}} {{then}} {{else}}}}` evaluates `{{then}}` if the `flag` variable was previously declared (`{{!siter-def flag}}`), or to `{{else}}` otherwise. The else block is optional. | `{{!siter-if {{show-heading}} {{<h1>Welcome!</h1>}}}}`
`siter-md` | Runs Markdown on the supplied argument. | `{{!siter-md **Hello world!**}}`
`siter-anchor` | Makes the text argument suitable to use as an HTML anchor. | `<a href="#{{!siter-anchor Hello World}}">Permalink</a>`
`siter-datefmt` | Format a `YYYY-MM-DD` date with a Python [time format string](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes). | `<footer>Page last updated {{!siter-datefmt {{!siter-modified}} {{%b %Y}}}}</footer>`
`siter-foreach` | Formats and chains files from a subdir under `siter-foreach` with a template file from `siter-template`. Takes an optional number limit. | `{{!siter-foreach {{news}} {{news.html}} {{10}}}}`

### Full Project Tree

```sh
hello-world/
├── siter-config/   # [Optional] Global definitions
├── siter-foreach/  # [Optional] Markdown source files
├── siter-out/      # [Required] The generated website
├── siter-pages/    # [Required] Markdown source pages
├── siter-static/   # [Optional] Static content
└── siter-template/ # [Required] HTML templates
```

## Dependencies

Siter uses [Python-Markdown](https://python-markdown.github.io/) (with CodeHiliteExtension, FencedCodeExtension, and TocExtension) and [Pygments](https://pygments.org/) for text formatting and code syntax highlighting, along with *enum, http.server, os, shutil, socketserver, subprocess, sys, threading, time,* and *traceback* from the standard library.

```sh
sudo apt install python3 python3-markdown python3-pygments
```

## License

Copyright 2011-2025 Alex Margarit (alex@alxm.org)

Licensed under [GNU GPL 3.0](https://www.gnu.org/licenses/gpl.html) (see `COPYING`).
