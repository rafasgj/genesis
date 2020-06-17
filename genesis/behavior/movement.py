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

"""Behaviors that add movement to objects."""

import math
from collections import defaultdict
from genesis.objects import GameEvent


class Movable:
    """Base class for all objects that can be moved."""

    def __init__(self, **options):
        """Initialize game object."""
        # pylint: disable=no-member
        values = options.get("position", (0, 0))
        self.__x, self.__y = self._extract_list_values(values)
        self.__delta_x, self.__delta_y = (0, 0)

    def update(self):
        """Update object position."""
        x, y = self.__x, self.__y
        delta_x, delta_y = self.delta_move()
        x += delta_x
        y += delta_y
        self.__x, self.__y = x, y
        self.__delta_x, self.__delta_y = (0, 0)

    @property
    def position(self):
        """Retrieve object position."""
        return (int(self.__x), int(self.__y))

    def move(self, delta_x, delta_y):
        """Move object by an amount in the x and y axis."""
        self.__delta_x = delta_x
        self.__delta_y = delta_y

    def move_to(self, x, y):  # pylint: disable=invalid-name
        """Move object by an amount in the x and y axis."""
        self.__delta_x = x - self.__x
        self.__delta_y = y - self.__y

    def delta_move(self):
        # pylint: disable=no-self-use
        """Retrieve the amount of movement an object should have."""
        return self.__delta_x, self.__delta_y


class LimitMovement:
    """
    Limit movement to an area.

    This class injects verification to `delta_move()` result so that object
    movement lies within a limited area.
    """

    # pylint: disable=no-member, too-few-public-methods
    # We do rely on late binding for most GameObject and behaviors.

    def __init__(self, **options):
        """Initialize game object."""
        # pylint: disable=no-member
        # TODO: assert limit_area has 4 values, and w and h are greater than 0.
        values = options.get("limit_area", [0, 0, -1, -1])
        self.__limit_area = self._extract_list_values(values)
        self.modify_result_of(self.delta_move, self.__verify_limits)

    def limit_area(self):
        """Query object limited movement area."""
        return self.__limit_area

    def __verify_limits(self, delta_x, delta_y):
        limit_x, limit_y, limit_width, limit_height = self.__limit_area
        x, y = self.position
        new_x = x + delta_x
        new_y = y + delta_y

        event_data = defaultdict(list)
        if limit_width > 0 and limit_height > 0:
            if new_x < limit_x:
                event_data["limit"].append("left")
                event_data["amount"].append(abs(new_x - limit_x))
                delta_x = limit_x - x
            if new_x > limit_x + limit_width:
                event_data["limit"].append("right")
                event_data["amount"].append(
                    abs(new_x - (limit_x + limit_width))
                )
                delta_x = (limit_x + limit_width) - x
            if new_y < limit_y:
                event_data["limit"].append("top")
                event_data["amount"].append(
                    abs(new_y - (limit_y + limit_height))
                )
                delta_y = limit_y - y
            if new_y > limit_y + limit_height:
                event_data["limit"].append("bottom")
                event_data["amount"].append(
                    abs(new_y - (limit_y + limit_height))
                )
                delta_y = (limit_y + limit_height) - y
        if event_data:
            self.emit(  # pylint: disable=no-member
                GameEvent(sender=self, event="offlimits", **event_data,)
            )

        return (delta_x, delta_y)


class LinearMove(Movable):
    """Move an object linearly."""

    def __init__(self, **options):
        """Initialize movement object."""
        Movable.__init__(self, **options)
        self.__speed = options.get("speed", 5)
        angle = options.get("angle", 0)
        self.__angle = 2 * math.pi - (math.pi / 180.0 * angle)
        self.__dx = 0
        self.__dy = 0

    def delta_move(self):
        """Retrieve the amount of movement for the object."""
        angle = self.__angle
        delta_x = self.speed * math.cos(angle)
        delta_y = self.speed * math.sin(angle)
        return (delta_x, delta_y)

    def flip_horizontal_movement(self):
        """Change movement angle so that in reverse horizontal direction."""
        self.__angle = (2 * math.pi + (math.pi - self.__angle)) % (2 * math.pi)

    def flip_vertical_movement(self):
        """Change movement angle so that in reverse horizontal direction."""
        self.__angle = (2 * math.pi + (-1 * self.__angle)) % (2 * math.pi)

    @property
    def speed(self):
        """Retrieve object movement speed."""
        return self.__speed

    @speed.setter
    def speed(self, value):
        """Set the object movement speed."""
        self.__speed = value

    @property
    def angle(self):
        """Retrieve the object movement angle, in degrees."""
        return self.__angle * 180.0 / math.pi

    @angle.setter
    def angle(self, value):
        """Set the movement angle, in degress."""
        self.__angle = 2 * math.pi - (math.pi / 180.0 * value)
