"""Setup script for the Genesis Game Design Engine project."""

# This file is part of Genesis Game Design Engine
#
# Genesis is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Foobar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <https://www.gnu.org/licenses/>.

from setuptools import setup

__FPI_DESCRIPTION = """
Genesis Game Design Engine is a tool designed to teach Game Design.
"""


def __dependencies():
    with open("requirements.txt", "r") as reqfile:
        return [
            req
            for req in map(str.strip, reqfile.readlines())
            if req and not req.startswith("#")
        ]


setup(
    name="Genesis Game Design Engine",
    version="0.1",
    author="Rafael Guterres Jeffman",
    author_email="rafasgj@gmail.com",
    description="Genesis Game Design Engine",
    long_description=__FPI_DESCRIPTION,
    license="GPLv3",
    packages=["genesis"],
    package_data={"": ["resources/*"]},
    install_requires=__dependencies(),
    url="https://github.com/rafasgj/genesis",
)
