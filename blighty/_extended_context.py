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

from . _brush import BrushSets, not_callable_from_instance


class ExtendedContext():
    """Extension of the standard `cairo.Context` class.

    This class is used to extend the vanilla `cairo.Context` with _brushes_.
    These are either methods of a subclass of `Canvas` that are prefixed with
    `draw_`, or those that are explicitly decorated with the `@brush`
    decorator.

    There shouldn't be any reasons why you'd want to use instantiate this class
    directly. The `ctx` argument that is passed to the `Canvas` `on_draw`
    callback is an instance of this class. This can be passed as an argument
    to any callable object that expects a `cairo.Context` instance. The
    underlying `Canvas` object can be accessed via the `canvas` attribute. This
    can be useful if one needs to refer to the parent canvas geometry (e.g.
    its size).
    """
    def __init__(self, ctx, canvas):
        self._ctx = ctx
        self.canvas = canvas

        collected_methods = []

        for dm in dir(canvas):
            try:
                if callable(getattr(canvas, dm)) and dm[:5] == "draw_":
                    collected_methods.append(dm)
            except RuntimeError:
                # In the GTK case, introspection breaks getattr so we ignore
                # the attributes we cannot retrieve.
                pass

        # for m in [dm for dm in dir(canvas) if callable(getattr(canvas, dm)) and dm[:5] == "draw_"]:
        for m in collected_methods:
            # Re-bind brush method and mark the original as non-callable
            setattr(self, m, getattr(type(canvas), m).__get__(self, ExtendedContext))
            setattr(canvas, m, not_callable_from_instance.__get__(canvas, type(canvas)))

        for n, m in BrushSets.get_brush_set(type(canvas).__qualname__).items():
            if n in dir(ctx):
                raise RuntimeError("Brush name '{}' clashes with attribute or method in {}".format(n, type(ctx).__qualname__))
            setattr(self, n, m.__get__(self, ExtendedContext))

    def __getattr__(self, name):
        """Access the underling context methods."""
        return getattr(self._ctx, name)
