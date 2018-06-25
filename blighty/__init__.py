"""
This file is part of "blighty" which is released under GPL.

See file LICENCE or go to http://www.gnu.org/licenses/ for full license
details.

blighty is a desktop widget creation and management library for Python 3.

Copyright (c) 2018 Gabriele N. Tornetta <phoenix1987@gmail.com>.
All rights reserved.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

# XWayland fix
import os
os.environ["GDK_BACKEND"] = "x11"

from . _extended_context import ExtendedContext

from . _brush import brush


class CanvasType(type):
    NORMAL = 0         # _NET_WM_WINDOW_TYPE_NORMAL
    DESKTOP = 1        # _NET_WM_WINDOW_TYPE_DESKTOP
    DOCK = 2           # _NET_WM_WINDOW_TYPE_DOCK
    UNDECORATED = 3    # _NET_WM_WINDOW_TYPE_TOOLBAR


class CanvasGravity(type):
    NORTH_WEST = 1
    NORTH = 2
    NORTH_EAST = 3
    WEST = 4
    CENTER = 5
    EAST = 6
    SOUTH_WEST = 7
    SOUTH = 8
    SOUTH_EAST = 9
    STATIC = 10


class TextAlign(type):
    TOP_RIGHT = 1
    TOP_MIDDLE = 2
    TOP_LEFT = 3
    CENTER_RIGHT = 4
    CENTER_MIDDLE = 5
    CENTER_LEFT = 6
    BOTTOM_RIGHT = 7
    BOTTOM_MIDDLE = 8
    BOTTOM_LEFT = 9
