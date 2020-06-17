# This file is part of the Genesis project.
#
# Copyright (C) 2020 Rafael Guterres Jeffman
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

"""Run Genesis as an application."""


import sys
import argparse
import logging

import yaml

import genesis
from genesis.engine.game import Game


# setup logger.
stdout = logging.StreamHandler(sys.stdout)
stdout.formatter = logging.Formatter("%(message)s")
log = logging.getLogger("genesis_gds")
log.addHandler(stdout)

cmdparser = argparse.ArgumentParser(
    prog="genesis", description="Genesis Game Design Engine"
)

cmdparser.add_argument("script", nargs=1, help="Game script to run.")
cmdparser.add_argument(
    "--version",
    action="version",
    version="%(prog)s {}".format(genesis.VERSION),
)
cmdparser.add_argument(
    "-v", action="store_true", help="Increase verbosity level."
)
cmdparser.add_argument(
    "-vv", action="store_true", help="Increase verbosity level even more."
)

options = cmdparser.parse_args()

if options.v:
    log.setLevel(logging.INFO)
if options.vv:
    log.setLevel(logging.DEBUG)

with open(options.script[0], "r") as stream:
    script = yaml.safe_load(stream)

game = Game(script)
log.info("\n".join(game.game_info()))
game.run()
