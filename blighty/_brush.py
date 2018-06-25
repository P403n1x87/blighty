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


def not_callable_from_instance(*args, **kwargs):
    raise RuntimeError(
        "This method cannot be called on instances of type {}".format(
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
    BrushSets.add_brush(*f.__qualname__.rsplit('.', 1), method = f)
    return not_callable_from_instance
