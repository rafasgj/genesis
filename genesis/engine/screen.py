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

"""Windowing elements."""

import pygame  # pylint: disable=import-error


class Screen:
    """Class screen."""

    def __init__(self, **options):
        """
        Initialize Screen object.

        Available options:
            width: Window width. Default to 720.
            height: Window height. Default to 480.
            frame: Create a frame with border and controls. Default to True.
            fullscreen: Create a full screen window. Default to False.
            scaled: Set pygame screen to run in scaled mode. Default to False.
            bg_color: Set the background color. Default to (0,0,0) [Black].
        """
        self.__bg = options.get("bg_color", (0, 0, 0))
        width = options.get("width", 720)
        height = options.get("height", 480)
        fullscreen = options.get("fullscreen", False)
        frame = options.get("framed", True)
        flags = pygame.DOUBLEBUF | pygame.HWSURFACE
        flags |= pygame.FULLSCREEN if fullscreen else 0
        flags |= pygame.NOFRAME if not frame else 0
        self.__width = width
        self.__height = height
        self.__surface = pygame.display.set_mode((width, height), flags)

    def clear(self, color=None):
        """Clear the surface with the given color."""
        if color is None:
            color = self.bg_color
        self.__surface.fill(color)

    def update(self):  # pylint: disable=no-self-use
        """Update screen object."""
        pygame.display.flip()

    @property
    def name(self):
        """Retrieve screen name."""
        return "screen"

    @property
    def surface(self):
        """Query surface."""
        return self.__surface

    @property
    def bg_color(self):
        """Retrieve the background color."""
        return self.__bg

    @bg_color.setter
    def bg_color(self, color):
        """Set the background color to the provided color."""
        self.__bg = color

    @property
    def dimension(self):
        """Return the screen dimension."""
        return (self.__width, self.__height)

    @property
    def width(self):
        """Return the screen dimension."""
        return self.dimension[0]

    @property
    def height(self):
        """Return the screen dimension."""
        return self.dimension[1]

    @property
    def center(self):
        """Return the point at the center of the screen."""
        width, height = self.dimension
        return (width // 2, height // 2)

    @property
    def client_area(self):
        """Retrieve the rectangular area of the screen client area."""
        return (0, 0, *self.dimension)
