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

"""Initialize genesis.behavior module."""

from genesis.behavior.basic import Drawable  # noqa: F401

from genesis.behavior.objects import Circle  # noqa: F401

from genesis.behavior.movement import (  # noqa: F401
    Movable,
    LimitMovement,
    LinearMove,
)

from genesis.behavior.collision import Collider  # noqa: F401
