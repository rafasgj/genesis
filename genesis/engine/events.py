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

"""Code related to game events."""

from collections import defaultdict

import logging

logger = logging.getLogger("genesis_gds")


class EventPublisher:
    """An object that publishes events."""

    def __init__(self):
        """Initialize publisher object."""
        self.__observers = defaultdict(list)

    def subscribe(self, event, observer):
        """Register an observer object to an event name."""
        if observer not in self.__observers[event]:
            self.__observers[event].append(observer)

    def emit(self, event):
        """Emit event notification to observer."""
        for observer in self.__observers[event.event]:
            logger.debug(
                msg="Notifying event: %s to %s" % (event.name, observer.name)
            )
            observer.notify(event)

    @staticmethod
    def sender_instance(**params):
        """Instantiate a `sener` object with the given parameters."""
        # pylint: disable=too-few-public-methods
        class SenderObject:
            """A `fake` object to act as a proxy sender for events."""

        sender = SenderObject()
        for key, value in params.items():
            setattr(sender, key, value)
        return sender


class GameEvent:
    """
    Base class for all events.

    Each event object is different, and create its own attributes.
    """

    def __init__(self, sender, name, **attributes):
        """Initialize the event object and create its attributes."""
        self.__attributes = attributes
        self.__iter = None
        self.__attributes.update(
            {"sender": sender, "event": name, "name": name}
        )
        for key, value in attributes.items():
            setattr(self, key, value)

    def as_dict(self):
        """Return a copy of the object attributes, as a dict."""
        return self.__attributes.copy()

    def __iter__(self):
        """Obtain an iterator over event attributes."""
        self.__iter = iter(self.__attributes)
        return self

    def __next__(self):
        """Get next iterator element."""
        return next(self.__iter)

    def __getitem__(self, item):
        """Allow subscriptable access to GameEvent."""
        return self.__attributes[item]

    def __hasitem__(self, item):
        """Allow subscriptable access to GameEvent."""
        return item in self.__attributes
