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

"""Basic behaviors."""


class Drawable:
    """Abstract class for drawable objects."""

    def __init__(self, **options):
        """Initialize object."""
        self.__color = options.get("color", (255, 255, 255))

    def draw(self, screen):
        """Draw the object to the given screen."""
        raise NotImplementedError("Not implemented: `draw()`")

    @property
    def fg_color(self):
        """Retrieve object position."""
        return self.__color

    @fg_color.setter
    def fg_color(self, color):
        """Set object position."""
        if not isinstance(color, tuple) and len(color) != 3:
            raise Exception("Color must be a tuple with 3 values.")
        self.__color = color
