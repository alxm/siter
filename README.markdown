Siter
=====

Siter is a very simple static website generator written in Python.

Content from `siter-pages` is fitted in `siter-template/page.html` and rendered pages are written to the site's root directory. Pages can define variables and simple macros that the template and page can call. Variables and macros that start with `siter.` are reserved for the program and should not be defined by pages.

A very simple example is included. My own [website](https://github.com/alxm/alxm.github.com) uses Siter too.

Sample
------

    cd sample
    siter       # generate
    siter force # regenerate all files, even up-to-date ones

License
-------

Copyright 2011 Alex Margarit (alex.margarit@gmail.com)

Licensed under GNU GPL3.
