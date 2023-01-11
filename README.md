CS 4470 Compilers Template
==========================

Please use this repository to hold all of your work for CS 4470
compilers. You will submit your assigments, and they will be graded,
using the contents of this repository only, at the commit
corresponding to the latest possible submission time (including
all granted extensions).

Picking a Language
------------------

This repository supports work in C++ (version 20), Java (19), or
Python (3.10). It correspondingly includes starter files
`compiler.cpp`, `compiler.java`, and `compiler.py`. Each starter file
compiles and runs, doing nothing and returning successfully. For each
language there is also a Makefile: `Makefile_cpp`, `Makefile_java`,
and `Makefile_py`.

To pick your language, delete the starter files for the other two
languages and rename the remaining Makefile to be named `Makefile`. If
you want to use a language other than C++, Java, or Python, you need
special permission; contact the instructors. Keep in mind that using
another language will be more work, and you will not be able to
receive the same level of instructor support. Compilers are
complicated. It is abjectly irresponsible to try to learn a new
language at the same time as you learn compilers.

Compiling your Compiler
-----------------------

A compiler is just a normal computer program. Before running it you
need to compile it. So, once you've picked a language, compile your
compiler by running:

    make compile

This should complete without errors. If you get an error, you likely
need to install one of `clang++`, `javac`/`java`, or `python3`
(depending on the language you chose), or to add those tools to your
system PATH. If you're having trouble with this step, please talk
to your TA or one of your instructors.

Note that if you're using Python, `make compile` will do a bit of
syntax checking but that's about it. If you are familiar with and want
to use tools like Mypy, feel free to edit your Makefile to do so.

Running your Compiler
---------------------

To test your compiler you need a test program to compile. The file
`test.jpl` is intended to be a quick scratch-pad for such tests. Run
your compiler on it with:

    make run

Of course, longer-term you'll want to save test files and run the
regularly to avoid regressions. You can change the name of the test
file like so:

    make run TEST=something.jpl

We will use this same functionality to grade your assignments.

Github Actions
--------------

Every time you push to this repository, it will compile your program
and then auto-grade the current homework assignment. The auto-grader
will roll over to the next week's assignment on Monday.

In general, you can feel free to rename files and move them around,
but the auto-grader works via Github Actions, which are configured in
the `.github` folder. Do not edit any file in that folder. You will
fail the assignment! Also do not create a folder called `grader`, that
will break the autograder.

Github actions will email you every time you push, if you fail a test.
This will be most times you push, since "failing a test" just means
you haven't finished an assignment. That will be _very_ annoying. We recommend
[turning this off][notification].

[notification]: https://docs.github.com/en/account-and-profile/managing-subscriptions-and-notifications-on-github/setting-up-notifications/about-notifications
