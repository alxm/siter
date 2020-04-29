# Siter

Siter is a static website generator written in Python 3, "Markdown with macros and variables" for my [own simple needs](https://www.alxm.org/ "My personal website is made with Siter").

## What does it do?

You call `siter` from the project's root directory, which is structured like this:

    <project>/
    ├── siter-config/   # Config files
    ├── siter-out/      # The final generated website
    ├── siter-pages/    # Markdown source pages to be processed
    ├── siter-static/   # Static files copied as they are
    ├── siter-stubs/    # Small Markdown files included by pages
    └── siter-template/ # HTML templates

* Files and directories from `siter-static/` are copied to `siter-out/` as they are.
* Source pages from `siter-pages/` are evaluated, formatted with Markdown, fitted in `siter-template/page.html`, and finally written to `siter-out/`.
* `siter-config/defs` file contains global definitions that are available to every page and template to use.

### Quick Example

A source page `siter-pages/index.md`,

```
{{!def {{title}} {{Home}}}}

## Hello world!

This page is called *{{!title}}*.
```

Combined with the page template `siter-template/page.html`,

    <html>
        <body>
            <h1>{{!title}}</h1>
            {{!md {{!content}}}}
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

A block is text enclosed between `{{` and `}}`. If the first character in a block is the eval marker `!`, then the block is evaluated as a variable or macro. So `{{!modified %Y}}` might expand to `2011` if you travelled back in time, but `{{modified %Y}}` would just be replaced with the literal `modified %Y`.

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

When a macro takes a single argument like `album` does above, you may ommit block tags around the argument.

## Special Macros and Variables

These are the built-in definitions.

Variable | About | Example
--- | --- | ---
`content` | The evaluated content of the page file, used in `siter-template/page.html`. | `{{!md {{!content}}}}`
`root` | Relative path from the current page to the website root, so you can reference static files from nested pages. | `<img src="{{!root}}/photos/cloud.jpg">`

Macro | About | Example
--- | --- | ---
`modified` | The time the source page file was modified, takes a Python [time format string](http://strftime.org/) as parameter. | `Page last updated {{!modified %B %Y}}`
`generated` | The time the page file was generated, also takes a time format string. | `Page generated {{!modified %B %Y}}`
`md` | Runs the supplied argument through Markdown. | `{{!md **Hello world!**}}`
`if` | `{{!if {{flag}} {{then}} {{else}}}}` evaluates `{{then}}` if the `flag` variable was previously declared (`{{!def flag}}`), or to `{{else}}` otherwise. The else block is optional. | `{{!if {{show-heading}} {{<h1>Welcome!</h1>}}}}`

## Dependencies

Siter uses [Python-Markdown](https://python-markdown.github.io/) (with CodeHiliteExtension and FencedCodeExtension) and [Pygments](https://pygments.org/) for text formatting and code syntax highlighting.

    sudo apt install python3 python3-markdown python3-pygments

## License

Copyright 2011-2020 Alex Margarit (alex@alxm.org)

Licensed under [GNU GPL 3.0](https://www.gnu.org/licenses/gpl.html) (see `COPYING`).
