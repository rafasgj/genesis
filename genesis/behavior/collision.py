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

"""Collision objects and algorithms."""

import logging
from math import sin, cos, atan2, copysign, radians

from genesis.objects import GameEvent


logger = logging.getLogger("genesis_gsd")


class Collider:
    """Encapsulates all collision detect methods."""

    # pylint: disable=no-member
    # disabling `no-member` due to the use of lazy binding for GameObject.

    ELLIPSE = "ellipse"
    RECT = "rect"
    CIRCLE = "circle"
    LINE = "line"
    POINT = "point"

    def __init__(self, **options):
        """Initialize the collision detection algorithms."""
        self.__bounding_shape = options.get("bounding_shape", "circle")
        self.should_collide = options.get("should_collide", True)
        self.run_after(self.update, self.check_collisions)

    @property
    def bounding_shape(self):
        """Retrieve the object bounding shape."""
        return self.__bounding_shape

    @property
    def bounds(self):
        """Query object bounds."""
        # pylint: disable=no-member
        # Objects using collision will define these properties, if needed.
        if self.bounding_shape == Collider.CIRCLE:
            return (*self.center, self.radius)
        if self.bounding_shape == Collider.RECT:
            return self.rect
        if self.bounding_shape == Collider.ELLIPSE:
            return (*self.center, *self.dimension, self.rotation)
        raise Exception("Invalid object bounding shape.")
        # case = {
        #     Collider.ELLIPSE: [*self.center, *self.dimension, self.rotation],
        #       # TODO: angledrect collision
        #     Collider.RECT: self.rect if hasattr(rect) or None,
        #     Collider.CIRCLE: [*self.center, self.radius],
        # }
        # return case[self.bounding_shape]

    def did_collide(self, obj):
        """Return true if collides with object."""
        result = False
        if all([self.should_collide, obj.should_collide]):
            shape = "%s_%s" % (self.bounding_shape, obj.bounding_shape)
            method = Collider.__functions.get(
                shape, lambda a, b: (False, 0, 0)
            )
            result = method(self.bounds, obj.bounds)
        return result

    def check_collisions(self):
        """Check collision event."""
        for obj in self.game.game_objects:
            if (self is not obj) and hasattr(obj, "should_collide"):
                if self.should_collide or obj.should_collide:
                    shape_fn = "%s_%s" % (
                        self.bounding_shape,
                        obj.bounding_shape,
                    )
                    func = Collider.__functions.get(shape_fn, None)
                    if func:
                        collision, point, angle = func(self.bounds, obj.bounds)
                        if collision:
                            event_data = {"point": point, "angle": angle}
                            logger.debug(
                                msg="Collision: {}:{}".format(
                                    self.name, obj.name
                                )
                            )
                            event = GameEvent(
                                self,
                                event="collision",
                                against=[obj.name],
                                **event_data
                            )
                            self.emit(event)  # TODO: add proper values
                            event = GameEvent(
                                obj,
                                event="collision",
                                against=[self.name],
                                **event_data
                            )
                            obj.emit(event)  # TODO: add proper values

    class __Algo:
        # pylint: disable=invalid-name
        @staticmethod
        def __distance_to_ellipse(ellipse, point):
            x, y = point
            h, k, rx, ry, angle = ellipse
            rx, ry = (rx // 2, ry // 2) if rx <= ry else (ry // 2, rx // 2)
            sina = sin(-1 * radians(angle))
            cosa = cos(-1 * radians(angle))
            xh = x - h
            yk = y - k
            t1 = xh * cosa - yk * sina
            t2 = xh * sina + yk * cosa
            return ((t1 * t1) / (rx * rx)) + ((t2 * t2) / (ry * ry))

        @classmethod
        def ellipse_point(cls, ellipse, point):
            """Verify colision between an ellipse and a rectangle."""
            return cls.__distance_to_ellipse(ellipse, point) <= 0.95

        @classmethod
        def ellipse_circle(cls, ellipse, circle):
            """Verify colision between an ellipse and a rectangle."""
            x, y, r = circle
            return cls.__distance_to_ellipse(ellipse, (x, y)) <= (1 + r)

        @classmethod
        def ellipse_rect(cls, ellipse, rect):
            """Verify colision between an ellipse and a rectangle."""
            x, y, width, height = rect
            for p in (
                (x, y),
                (x, y + height),
                (x + width, y),
                (x + width, y + height),
            ):
                d = cls.__distance_to_ellipse(ellipse, p)
                if d <= 0.95:
                    return True
            return False

        @classmethod
        def ellipse_ellipse(cls, e1, e2):  # pylint: disable=unused-argument
            """Verify collision between two ellipses."""
            raise NotImplementedError("Not implemented: `ellipse_ellipse`")

        @classmethod
        def ellipse_line(cls, ellipse, line):
            """Verify colision between an ellipse and a rectangle."""
            for p in line:
                if cls.ellipse_point(ellipse, p):
                    return True
            return False

        @classmethod
        def circle_rect(cls, circle, rect):
            """Verify colision between an ellipse and a rectangle."""
            x, y, w, h = rect
            cx, cy, r = circle
            r *= r
            for a, b in [(x, y), (x + w, y), (x, y + h), (x + w, y + h)]:
                dx = (a - cx) ** 2
                dy = (b - cy) ** 2
                if (dx + dy) < r:
                    return True
            return False

        @classmethod
        def circle_circle(cls, c1, c2):
            """Verify colision between an ellipse and a rectangle."""
            cx1, cy1, r1 = c1
            cx2, cy2, r2 = c2
            h = (cx1 - cx2) ** 2 + (cy1 - cy2) ** 2
            r = (r1 + r2) ** 2
            #
            point = (cx1 + (cx2 - cx1) / 2, cy1 + (cy2 - cy1) / 2)
            angle = atan2(cx2 - cx1, cy2 - cy1)
            return (h <= r, point, angle)

        @classmethod
        def point_rect(cls, point, rect):
            """Verify collision between point and rectangle."""
            xo, yo = point
            x, y, w, h = rect
            return (x <= xo <= x + w) and (y <= yo <= y + h)

        @classmethod
        def rect_rect(cls, r1, r2):
            """Verify colision between an ellipse and a rectangle."""
            x1, y1, w1, h1 = r1
            x2, y2, w2, h2 = r2
            if x1 > x2 + w2 or x1 + w1 < x2:
                return False
            if y1 > y2 + h2 or y1 + h1 < y2:
                return False
            return True

        @classmethod
        def line_line(cls, l1, l2):
            """Check if a line segment intersects another."""

            def abc(p1, p2):
                x1, y1 = p1
                x2, y2 = p2
                a = y2 - y1
                b = x1 - x2
                c = x2 * y1 - x1 * y2
                return (a, b, c)

            def verify(abc, p1, p2):
                a, b, c = abc
                x1, y1 = p1
                x2, y2 = p2
                r1 = a * x2 + b * y1 + c
                r2 = a * x1 + b * y2 + c
                return r1 != 0 and r2 != 0 and copysign(1, r1) == copysign(r2)

            p1, p2 = l1
            p3, p4 = l2

            if verify(abc(p1, p2), p3, p4):
                return False
            if verify(abc(p3, p4), p1, p2):
                return False
            return True

        @classmethod
        def line_rect(cls, line, rect):
            """Check if a line segment intersects a rectangle."""
            p1, p2 = line
            x, y, w, h = rect
            if cls.point_rect(p1, rect) or cls.point_rect(p2, rect):
                return True
            for _line in (
                ((x, y), (x + w, y)),
                ((x, y), (x, y + h)),
                ((x, y + h), (x + w, y + h)),
                ((x + w, y), (x + w, y + h)),
            ):
                if cls.line_line(line, _line):
                    return True
            return False

        @classmethod
        def line_circle(cls, line, circle):  # pylint: disable=unused-argument
            """Check if a line segment intersects a circle."""
            raise NotImplementedError("Not implemented: `ellipse_ellipse`")

        @classmethod
        def invert(cls, fn):
            """Invert function arguments."""

            def do_it(a, b):
                return fn(b, a)

            return do_it

    __functions = {
        "ellipse_rect": __Algo.ellipse_rect,
        "rect_ellipse": __Algo.invert(__Algo.ellipse_rect),
        "ellipse_circle": __Algo.ellipse_circle,
        "circle_ellipse": __Algo.invert(__Algo.ellipse_circle),
        "circle_rect": __Algo.circle_rect,
        "rect_circle": __Algo.invert(__Algo.circle_rect),
        "rect_rect": __Algo.rect_rect,
        "circle_circle": __Algo.circle_circle,
        "ellipse_ellipse": __Algo.ellipse_ellipse,
        "line_line": __Algo.line_line,
        # circle-line collision not implemented yet
        "line_circle": __Algo.line_circle,
        "circle_line": __Algo.invert(__Algo.line_circle),
        "line_rect": __Algo.line_rect,
        "rect_line": __Algo.invert(__Algo.line_rect),
        "line_ellipse": __Algo.invert(__Algo.ellipse_line),
        "ellipse_line": __Algo.ellipse_line,
        "point_ellipse": __Algo.invert(__Algo.ellipse_point),
        "ellipse_point": __Algo.ellipse_point,
        "point_rect": __Algo.point_rect,
        "rect_point": __Algo.invert(__Algo.point_rect),
    }
