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

"""Legacy visual tools, inspired by Conky."""

from collections import deque


class Graph:
    """A Conky-style scrolling graph.

    Instantiate inside a Widget and use ``push_value()`` in your
    ``update()`` method, then call ``draw(ctx)`` in your ``draw()``
    method.

    Args:
        x: X position of the graph.
        y: Y position of the graph.
        width: Graph width in pixels.
        height: Graph height in pixels.
        scale: Y-axis scale. ``None`` for auto-scaling.
    """

    def __init__(self, x, y, width, height, scale=100):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.scale = scale if scale else 0
        self.auto = not scale
        self._values = deque(maxlen=width)

    def push_value(self, v):
        """Push a new value onto the graph."""
        self._values.append(v)
        if self.auto:
            self.scale = max(self._values)

    def draw(self, cr):
        """Draw the graph on the given cairo context."""
        if not self.scale:
            return

        offset = self.x + self.width - len(self._values)
        for i in range(len(self._values)):
            cr.set_line_width(1)
            if self.height > 0:
                cr.move_to(offset + i + .5, self.y + self.height)
                cr.line_to(
                    offset + i + .5,
                    self.y + int(self.height * (1 - self._values[i] / self.scale))
                )
            else:
                cr.move_to(offset + i + .5, self.y)
                cr.line_to(
                    offset + i + .5,
                    self.y + int(-self.height * self._values[i] / self.scale)
                )
            cr.stroke()
