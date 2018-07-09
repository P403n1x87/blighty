# This file is part of "blighty" which is released under GPL.
#
# See file LICENCE or go to http://www.gnu.org/licenses/ for full license
# details.
#
# blighty is a desktop widget creation and management library for Python 3.
#
# Copyright (c) 2018 Gabriele N. Tornetta <phoenix1987@gmail.com>.
# All rights reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
This module contains the common objects and types for the different kind of
canvases provided by ``blighty``.
"""

# XWayland fix
import os
os.environ["GDK_BACKEND"] = "x11"

from . _extended_context import ExtendedContext

from . _brush import brush, TextAlign


class CanvasType(type):
    """The Canvas type.

    The canvas types enumerated in this Python type reflect the same window
    types that one can request to the window manager via the `Extended
    Window Manager Hints <https://standards.freedesktop.org/wm-spec/wm-spec-1.3.html>`_.

    - ``NORMAL`` is a normal top-level window.
    - ``DESKTOP`` is a window drawn directly on the desktop.
    - ``DOCK`` indicates a dock or panel window that will usually stay on top
      of other windows.
    - ``UNDECORATED`` is a type of window that behaves as a toolbar. As such,
      it is undecorated.
    """

    NORMAL = 0         # _NET_WM_WINDOW_TYPE_NORMAL
    DESKTOP = 1        # _NET_WM_WINDOW_TYPE_DESKTOP
    DOCK = 2           # _NET_WM_WINDOW_TYPE_DOCK
    UNDECORATED = 3    # _NET_WM_WINDOW_TYPE_TOOLBAR


class CanvasGravity(type):
    """Window gravity control type.

    The positioning of a canvas on the screen is controlled by its gravity.
    By default, a window is positioned in a coordinate system where the origin
    is located in the top-left corner of the screen, with the *x* axis running
    horizontally from left to right, and the *y* from top to bottom. To change
    the location of the origin, use one of the following values.
    """

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
