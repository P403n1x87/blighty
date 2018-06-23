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

from cairo import Context
from blighty import ExtendedContext
from blighty._x11 import BaseCanvas


class Canvas(BaseCanvas):
    def __init__(self, *args, **kwargs):
        self._extended_context = None

    def _on_draw(self, ctx):
        # Enrich the cairo context with the draw_methods and the canvas
        if self._extended_context is None:
            self._extended_context = ExtendedContext(ctx, self)

        return self.on_draw(self._extended_context)

    def on_draw(self, ctx):
        raise NotImplementedError("on_draw method not implemented in subclass.")
