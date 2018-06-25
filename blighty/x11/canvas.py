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

from blighty import ExtendedContext, TextAlign, brush
from blighty._x11 import BaseCanvas
from blighty._brush import BrushSets


class Canvas(BaseCanvas):
    def __init__(self, *args, **kwargs):
        BrushSets.inherit(type(self))
        self._extended_context = None

    def _on_draw(self, ctx):
        # Enrich the cairo context with the draw_methods and the canvas
        if self._extended_context is None:
            self._extended_context = ExtendedContext(ctx, self)

        return self.on_draw(self._extended_context)

    def on_draw(self, ctx):
        raise NotImplementedError("on_draw method not implemented in subclass.")

    def draw_grid(ctx, x = 50, y = 50):
        w, h = ctx.canvas.get_size()

        ctx.save()

        ctx.set_source_rgba(.8, .8, .8, .8)
        ctx.set_line_width(1)
        ctx.set_font_size(9)
        for i in range(x, w, x):
            ctx.write_text(i, 0, str(i), align = TextAlign.BOTTOM_MIDDLE)
            ctx.move_to(i, 8)
            ctx.line_to(i, h)
            ctx.stroke()

        for i in range(y, h, y):
            ctx.write_text(0, i, str(i), align = TextAlign.CENTER_LEFT)
            ctx.move_to(8, i)
            ctx.line_to(w, i)
            ctx.stroke()

        ctx.restore()

    @brush
    def write_text(cr, x, y, text, align = TextAlign.TOP_LEFT):
        ex = cr.text_extents(text)

        if align <= TextAlign.TOP_LEFT:
            dy = 0
        elif align <= TextAlign.CENTER_LEFT:
            dy = ex.height // 2
        else:
            dy = ex.height

        if align % 3 == 1:
            dx = ex.width
        elif align % 3 == 2:
            dx = ex.width // 2
        else:
            dx = 0

        cr.move_to(x - dx, y + dy)
        cr.show_text(text)
        cr.stroke()

        return ex
