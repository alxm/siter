# Siter

Siter is a static website generator written in Python 3.

I made it for my own [simple needs](https://www.alxm.org/ "My personal website is made with Siter") and as a way to play with Python. One of the goals was to generate websites that are fully usable locally without needing a web server.

## What does it do?

Siter is called from the project's root directory, where it looks for several files and directories:

    <project>/
    ├── siter-config/
    │   └── defs
    ├── siter-out/
    ├── siter-pages/
    ├── siter-static/
    ├── siter-stubs/
    └── siter-template/

* Files and directories from `siter-static/` are copied to `siter-out/` as they are.

* Source pages from `siter-pages/` are evaluated, formatted with Markdown, fitted in `siter-template/page.html`, and finally written to `siter-out/`.

* `siter-config/defs` has global definitions available to every page.

### Quick Example

A source page `siter-pages/index.html`,

```
{{!def {{title}} {{Home}}}}

## Hello world!

This page is called *{{!title}}*.
```

Combined with the page template `siter-template/page.html`,

    <html>
        <body>
            <h1>{{!title}}</h1>
            {{!content}}
        </body>
    </html>

Are used to make `siter-out/index.html`:

    <html>
        <body>
            <h1>Home</h1>
            <h2>Hello world!</h2>
            <p>This page is called <i>Home</i>.</p>
        </body>
    </html>

## Blocks, Variables, Macros, Functions

A block is text enclosed between `{{` and `}}` tags. If the first character in a block is the eval marker `!`, then the block is evaluated as a variable or macro. So `{{!modified %Y}}` might expand to `2011` if you travelled back in time, but `{{modified %Y}}` would just be replaced with `modified %Y`.

### Macros Example

    {{!def {{image}} {{filename description}} {{
        <img src="images/{{!filename}}" title="{{!description}}">
    }}}}

    {{!def {{album}} {{images}} {{
        <div>
            {{!images}}
        </div>
    }}}}

    {{!album
        {{!image {{landscape.jpg}} {{A painting}}}}
        {{!image {{ufo.jpg}} {{A photo}}}}
    }}

Becomes

    <div>
        <img src="images/landscape.jpg" title="A painting">
        <img src="images/ufo.jpg" title="A photo">
    </div>

When a macro takes a single argument, like `album` does above, you may ommit block tags around the argument.

## Special Macros and Variables

These are the built-in definitions.

Name | About
--- | ---
`content` | Used by `siter-template/page.html`. Contains the evaluated contents of the page file, ran through Markdown.
`root` | Relative path from the current page to the website root, so you can reference static files from nested pages.
`modified` | The time the source page file was modified. Takes a Python [time format](http://strftime.org/) string as parameter. For example, `{{!modified %B %Y}}` expands to something like `September 2015`.
`generated` | The time the page file was generated, same argument as `modified`.
`md` | Runs the supplied argument through Markdown.
`if` | `{{!if {{flag}} {{then}} {{else}}}}` evaluates `{{then}}` if the `flag` variable has been declared somewhere (like with `{{!def flag}}`), or to `{{else}}` otherwise. The else block is optional.

## Dependencies

Siter uses [Python-Markdown](https://python-markdown.github.io/) (with CodeHiliteExtension and FencedCodeExtension) and [Pygments](https://pygments.org/) for text formatting and code syntax highlighting.

    sudo apt install python3 python3-markdown python3-pygments

## License

Copyright 2011-2020 Alex Margarit (alex@alxm.org)

Licensed under [GNU GPL 3.0](https://www.gnu.org/licenses/gpl.html) (see `COPYING`).
