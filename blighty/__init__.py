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
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Blighty — Desktop Widget Manager.

This module provides the base Widget class and core types.
"""

# XWayland fix
import os
os.environ.setdefault("GDK_BACKEND", "x11")


class CanvasType:
    """Window type hints matching Extended Window Manager Hints."""

    NORMAL = 0         # _NET_WM_WINDOW_TYPE_NORMAL
    DESKTOP = 1        # _NET_WM_WINDOW_TYPE_DESKTOP
    DOCK = 2           # _NET_WM_WINDOW_TYPE_DOCK
    UNDECORATED = 3    # _NET_WM_WINDOW_TYPE_TOOLBAR


class CanvasGravity:
    """Window gravity control for positioning."""

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


class TextAlign:
    """Text alignment constants for use with write_text()."""

    TOP_RIGHT = 1
    TOP_MIDDLE = 2
    TOP_LEFT = 3
    CENTER_RIGHT = 4
    CENTER_MIDDLE = 5
    CENTER_LEFT = 6
    BOTTOM_RIGHT = 7
    BOTTOM_MIDDLE = 8
    BOTTOM_LEFT = 9


class Widget:
    """Base class for all Blighty widgets.

    Subclass this and implement ``update()``, ``draw()``, and optionally
    input handlers. The framework manages the event loop, canvas lifecycle,
    and periodic data-driven redraws.

    Dunder class attributes configure the canvas geometry and behaviour::

        class MyWidget(Widget):
            __interval__ = 1000   # ms between update() calls
            __width__ = 200
            __height__ = 200
            __gravity__ = CanvasGravity.CENTER

    The ``update()`` method must return a hashable value (e.g. a frozen
    dataclass). ``draw()`` is called only when the hash of the data changes.
    """

    __interval__ = 1000
    __width__ = 200
    __height__ = 200
    __x__ = 0
    __y__ = 0
    __gravity__ = CanvasGravity.NORTH_WEST
    __screen__ = 0
    __window_type__ = CanvasType.DESKTOP
    __sticky__ = True
    __keep_below__ = True
    __skip_taskbar__ = True
    __skip_pager__ = True

    def __init__(self):
        self.data = None
        self._prev_hash = None
        self._running = False
        self._canvas = None  # Set by the canvas adapter

    @property
    def width(self):
        return self.__width__

    @property
    def height(self):
        return self.__height__

    async def update(self):
        """Fetch and return new data. Must be hashable (e.g. a frozen dataclass).

        Override this in your subclass.
        """
        raise NotImplementedError("Subclasses must implement update()")

    async def draw(self, ctx):
        """Render the widget using ``self.data`` and the cairo context ``ctx``.

        Override this in your subclass. Only called when data has changed.
        """
        raise NotImplementedError("Subclasses must implement draw()")

    async def on_button_pressed(self, button, state, x, y):
        """Handle mouse button press events. Override to handle."""
        pass

    async def on_key_pressed(self, keysym, state):
        """Handle key press events. Override to handle."""
        pass

    async def _tick(self):
        """Internal: fetch data, compare hash, redraw if changed."""
        new_data = await self.update()
        new_hash = hash(new_data)
        if new_hash != self._prev_hash:
            self.data = new_data
            self._prev_hash = new_hash
            await self._canvas._dispatch_draw()

    def dispose(self):
        """Schedule destruction of this widget's canvas."""
        if self._canvas is not None:
            self._canvas.dispose()

    def destroy(self):
        """Immediately destroy this widget's canvas."""
        if self._canvas is not None:
            self._canvas.destroy()
