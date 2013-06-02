Siter
=====

Siter is a very simple static website generator written in Python.

Content from `siter-pages` is fitted in `siter-template/page.html` and rendered pages are written to the site's root directory. Pages can define variables and simple functions that the template and page can call. Variables and functions that start with `s.` are reserved for the program and should not be defined by pages.

A very simple example is included in the `sample` dir. My [games website](https://github.com/alxm/alxm.github.com) uses Siter too.

Sample
------

    cd sample
    siter       # generate
    siter force # regenerate all files, even up-to-date ones

License
-------

Copyright 2011 Alex Margarit (alex@alxm.org)

Licensed under GNU GPL3.
