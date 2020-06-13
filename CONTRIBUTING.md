# Contributing to Genesis

There are many ways to contribute to [Genesis]:

* using and evaluating it
* contributing feature requests
* contributing bug reports
* contributing documentation
* contributing with code

As with any open source project, Genesis will evolve better and faster
if people collaborate in its development. And there is no such thing as
an invaluable contribution, any help you can provide is of great value.


## Setting Up A Development Environment

To contribute to [Genesis]'s development, you'll need:

    Python 3.7 (or later)

Python 3.7 is supported by all major Linux distributions. Under macOS
follow the instructions on [Python.org].

It is recommended that you use a virtual environment, and if you name
it `.venv` Git will ignore it when displaying repository status:

```
$ python3 -m venv .venv
$ . .venv/bin/activate
```

As the project uses some Python modules that are not usually found on
standard Python setups. The required modules and the appropriate
versions can be found in the file [requirements.txt]

It is suggested that you install all of them through pip:

```
$ python3 -m pip install --user -r requirements.txt
```

Or install each package, one by one, for example, to test with a new
version of one package.

Some tools are needed only during development, so if you want to
contribute with code, you should also install the modules listed on
the file [requirements-dev.txt]:

```
$ python3 -m pip install --user -r requirements-dev.txt
```

You should also use a Python virtual environment. The scripts that run
`pylint` and `flake8` use the module `virtualenv`, and it is not
installed as a requirement, as it is optional.


<!-- Commented out, as tests are not yet setup. Shame on me. - Rafael
## Reporting a bug

[Genesis] aims to be well tested, but you might encounter yourself in a
situation that do not work as expected. In such case, you can
contribute by reporting what happened. To report a bug, create an issue
in the project's [Github repository].

For reporting a bug, it is important that the provided information
allows the bug to be reproduced, so, remember to describe what you
wanted to achieve, what steps were executed, what was the expected
behavior and the observed behavior. Also, inform the software and
catalog versions.
-->

## Requesting a New Feature

When requesting a new feature for [Genesis], please fill out a
[new issue] on Github.

Provide example use cases, describe what you want to do, how you want
to do it, and why you want to do what the new feature will provide.

If possible, use the [Gherkin language] (or something similar) to write
your feature request:

```gherkin
Given that <>,
    And <> ...
When <>,
    And <> ...
Then <>,
    And <> ...
```

<!-- Until there is a CI setup, and tests, sorry, no code contribution.
Again, shame on me. Bad Rafael, bad Rafael.

## Contributing Code

[Genesis] development happens on Github. Code contributions should be
submitted there, through [pull requests].

Your pull requests should contain:

* Tests (pytest) to test the implemented behavior;
* Fix one issue and fix it well;
* Fix the issue, but do not include extraneous refactoring or code
reformatting. Refactoring should be an issue on itself;
* Have descriptive titles and descriptions.

If your pull request changes, in any way, the behavior for users, you
must also add or modify a `feature`, and provide the required steps to
test it.

You should run `codecheck.sh`, on your code before commit. You must
have a score of 10.00 from `pylint`. The script will evaluate the
API.yml file and all Python source files. For a faster execution,
the `--fast` option can be used so only new and modified files are
evaluated.

You might also want to run `behave` or `pytest` to if all tests are
passing before commit. The script `run_tests.sh` runs all available
tests, and report test coverage. At least 90% of the code should be
covered with tests, either through `behave` (BDD) and `pytests`, and
your commit should never reduce test coverage.

Remember that 100% coverage is a nice measure, but it does not mean
that everything that should been tested is being tested, so you should
strive for not only code coverage, but for the even more important
usage coverage.

If you want to test on different versions of Python (3.7 and up), you
can use `tox`, it will execute all the automated set of code
verification and in your code.

Once you create a pull request, it will be reviewed, and, if approved,
merged into the `master` branch.

Your pull request will only be considered for review if the CI tests
succeed. Travis-CI is used in the project, so it might take a while
before tests are executed.

-->

[Genesis]: https://github.com/rafsgj/genesis
[github repository]: https://github.com/rafsgj/genesis
[new issue]: https://github.com/rafsgj/genesis/issues
[new issue]: https://github.com/rafsgj/genesis/pulls
[python.org]:https://python.org
[requirements.txt]: requirements.txt
[requirements-dev.txt]: requirements-dev.txt

> This CONTRIBUTING document is based on the contribution rules of
[fpi](https://github.com/rafasg/fpi-project).
