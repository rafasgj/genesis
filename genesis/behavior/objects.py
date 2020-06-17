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

"""Genesis game objects."""

import pygame  # pylint: disable=import-error

from genesis.behavior import Drawable


class Circle(Drawable):
    """A Circle shaped object."""

    def __init__(self, **options):
        """Initialize the circle object."""
        Drawable.__init__(self, **options)
        self.__radius = options.get("radius", 1)

    def draw(self, screen):
        """Draw Circle to surface."""
        surface = screen.surface
        if hasattr(self, "position"):
            position = getattr(self, "position")
            pygame.draw.circle(surface, self.fg_color, position, self.radius)

    @property
    def radius(self):
        """Retrieve the Circle radius."""
        return self.__radius

    @radius.setter
    def radius(self, value):
        """Set theo radius value."""
        if value >= 0:
            self.__radius = value

    @property
    def center(self):
        """Retrieve the central point of the object."""
        x, y = (0, 0)
        if hasattr(self, "position"):
            x, y = getattr(self, "position")
            x += self.__radius
            y += self.__radius
        return (x, y)

    @property
    def dimension(self):
        """Retrieve the width and height of the object."""
        return (self.radius, self.radius)

    @property
    def rotation(self):
        """Retrieve the object rotation angle in relation to horizonta axis."""
        return 0


# class Square(Drawable):
#     """Square shaped object."""
#
#     def __init__(self, **options):
#         """Initialize object."""
#         Drawable.__init__(self, **options)
#         width = options.get('width', 0)
#         height = options.get('height', 0)
#         self.__size = (width, height)
#
#     def draw_to(self, screen):
#         """Draw square object."""
#         rect = (*self.position, *self.__size)
#         pygame.draw.rect(screen.surface, self.fg_color, rect)
