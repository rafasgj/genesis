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

"""Game event object."""


class GameEvent:
    """
    Base class for all events.

    Each event object is different, and create its own attributes.
    """

    def __init__(self, sender, event, **attributes):
        """Initialize the event object and create its attributes."""
        self.sender = sender
        self.event = event
        self.name = event
        self.__attributes = attributes
        self.__iter = None
        self.__attributes.update(
            {"sender": sender, "event": event, "name": event}
        )
        for key, value in attributes.items():
            setattr(self, key, value)

    def __iter__(self):
        """Obtain an iterator over event attributes."""
        self.__iter = iter(self.__attributes)
        return self

    def __next__(self):
        """Get next iterator element."""
        return next(self.__iter)

    def __getitem__(self, item):
        """Allow subscriptable access to GameEvent."""
        if hasattr(self, item):
            return getattr(self, item)
        return self.__attributes[item]
