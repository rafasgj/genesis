# -*- coding: utf-8 -*-

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
# GNU General Public License for more detail, frame=Nos.
#
# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <ht | pygame.HWSURFACEicenses/>.

"""Basic Game Object."""

import logging

from genesis.engine.events import EventPublisher

logger = logging.getLogger("genesis_gds")


class GameObject(EventPublisher):
    """Base class of all game objects."""

    def __init__(self, **options):
        """Initialize basic object sructure."""
        EventPublisher.__init__(self)
        if options["name"] in ["level", "game"]:
            raise Exception("Invalid object name: `%s`" % options["name"])
        self.__name = options["name"]
        self.__game = options["game"]

    def modify_result_of(self, actual, method):
        """Allow a method to process and modify the result of another one."""

        def wrapped(*args, **kwargs):
            return method(*actual(*args, **kwargs))

        setattr(self, actual.__name__, wrapped)

    def run_after(self, actual, method):
        """Allow a method to automatically run after another one."""

        def wrapped(*args, **kwargs):
            result = actual(*args, **kwargs)
            method(*args, **kwargs)
            return result

        setattr(self, actual.__name__, wrapped)

    def _extract_list_values(self, values):
        if isinstance(values, (list, tuple)):
            values = list(
                map(
                    # pylint: disable=no-member
                    # All behaviors are used by game objects that have
                    # the game attribute..
                    self.game.interpreter.evaluate_expression,
                    map(str, values),
                )
            )
        elif isinstance(values, str):
            # pylint: disable=no-member
            # All behaviors are used by game objects that have
            # the game attribute..
            values = self.game.interpreter.evaluate_expression(values)
        else:
            raise Exception("List should be lists...")  # FIXME: better message
        return values

    @property
    def name(self):
        """Retrieve object name."""
        return self.__name

    @property
    def game(self):
        """Retrieve the object game."""
        return self.__game
