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
    def __init__(self, ctx, canvas):
        self._ctx = ctx
        self.canvas = canvas

        for m in [dm for dm in dir(canvas) if callable(getattr(canvas, dm)) and dm[:5] == "draw_"]:
            setattr(self, m, getattr(type(canvas), m).__get__(self, ExtendedContext))
            setattr(type(canvas), m, not_callable_from_instance)

        for n, m in BrushSets.get_brush_set(type(canvas).__qualname__).items():
            if n in dir(ctx):
                raise RuntimeError("Brush name '{}' clashes with attribute or method in {}".format(n, type(ctx).__qualname__))
            setattr(self, n, m.__get__(self, ExtendedContext))

    def __getattr__(self, name):
        """Access the underling context methods."""
        return getattr(self._ctx, name)