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

from functools import wraps


def not_callable_from_instance(*args, **kwargs):
    raise RuntimeError(
        "Method not callable on instances of type {}".format(
            type(args[0]).__name__
        )
    )


class BrushSets:
    brush_sets = {}
    inherited = {}

    @staticmethod
    def add_brush(brush_set, method_name, method):
        if brush_set not in BrushSets.brush_sets:
            BrushSets.brush_sets[brush_set] = {}

        BrushSets.brush_sets[brush_set][method_name] = method

    @staticmethod
    def get_brush_set(brush_set):
        return BrushSets.brush_sets.get(brush_set, {})

    @staticmethod
    def inherit(klass):
        if klass.__qualname__ in BrushSets.inherited:
            return

        for e in klass.__bases__:
            try:
                BrushSets.inherit(e)
                if klass.__qualname__ not in BrushSets.brush_sets:
                    BrushSets.brush_sets[klass.__qualname__] = {}
                BrushSets.brush_sets[klass.__qualname__].update(BrushSets.brush_sets[e.__qualname__])
            except KeyError:
                # No brushes registered for the superclass so we can skip it
                pass

        BrushSets.inherited[klass.__qualname__] = True


def brush(f):
    """Brush decorator.

    Used to mark a bound method of a subclass of the `Canvas` class as a
    _brush_. The method is then rebound to to the extended Cairo context that
    is passed to the `on_draw` callback. The first argument should then be
    called `ctx` or `cr` instead of `self`, but this is not enforced so that
    any keyword can be chosen.

    Example:
        class BrushExample(blighty.x11.Canvas):
            @brush
            def brush_method(ctx, data):
                ctx.save()
                # Draw something on the Cairo context
                ctx.restore()

            def on_draw(self, ctx):
                ctx.brush_method(42)

    In the above example, the `brush_method` has been decorated with the
    `brush` decorator. Therefore it will be callable as a method of `ctx`
    rather than `self`. An attempt to call it from `self` will cause a
    `RuntimeError` since the method is now bound to `ctx`.

    The use of the `brush` decorator is not restricted to X11 canvases.
    """
    BrushSets.add_brush(*f.__qualname__.rsplit('.', 1), method = f)

    @wraps(f)
    def wrapper(*args, **kwargs):
        return not_callable_from_instance(*args, **kwargs)

    return wrapper


## Basic brushes ##############################################################

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
