Genesis Game Design Engine
==========================

[![Build Status](https://travis-ci.com/rafasgj/genesis.svg?branch=master)](https://travis-ci.com/rafasgj/genesis)

`Genesis` is a tool designed to aid in teaching game design. It is not a
full fledged game engine (not even for 2D games). It is not a library
to develop games. It does not even make it easier to create games. If
you want to develop your own games, you should be using [Godot],
[pygame] or [Ogre].

The focus of `Genesis` in on creating a platform where 2D games can be
created, with minimal to none programming logic, so that students
starting to learn game programming, or game design, can create games
based on the description of objects and events.


Running the examples
--------------------

After cloning de repository, on its root (the same directory as this file),
execute the following steps to run `Genesis` examples.

Use a python virtual environment:

```shell
$ python -m venv .venv
$ . .venv/bin/activate
```

Install all dependencies.

```shell
$ python -m pip install -r requirements.txt
```

It might happen that `pygame` fails to install. In this case, use your
preferred package manager to install `pygame`, preferably, version 1.9.6.
Under Linux, use your distro package manager, under MacOS, [homebrew] is
recommended.

Install `Genesis` as a local package:

```shell
$ python -m pip install -e .
```

Execute one of the example scripts:

```shell
$ python -m genesis tests/examples/multi_ball.yml
```

`Genesis` requires Python 3, adapt the commands to use `python3` if your
system requires it.


Using `repl.it`
---------------

Genesis can be used under [repl.it], it even has a command line argument
to simulate it, but be warned that the experience is far from smooth.

<!--links -->
[godot]: https://godotengine.org
[pygame]: https://pygame.org
[Ogre]: https://ogre3dengine.org
[homebrew]: https://brew.sh
[repl.it]: https://repl.it

