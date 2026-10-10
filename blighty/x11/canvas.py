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

"""X11 backend for blighty widgets.

Provides the X11 canvas adapter that wraps a Widget and creates a
native X11 window via the C extension.
"""

from blighty import CanvasGravity, CanvasType
from blighty._extended_context import ExtendedContext
from blighty._x11 import BaseCanvas

import cairo


class Canvas(BaseCanvas):
    """X11 canvas adapter.

    Wraps a :class:`~blighty.Widget` subclass, creating a native X11
    window and driving the widget's ``update()``/``draw()`` lifecycle.

    Users should not instantiate this directly.  The CLI or
    :func:`blighty.run` handles canvas creation.
    """

    def __new__(cls, widget, *args, **kwargs):
        instance = super().__new__(cls, *args, **kwargs)
        instance._widget = widget
        instance._widget._canvas = instance
        instance._extended_context = None
        return instance

    def __init__(self, widget, *args, **kwargs):
        pass

    def show(self):
        """Map the canvas to screen and register with the async event loop."""
        super().show()
        from blighty._async_loop import _canvas_map
        _canvas_map[self.win_id] = self
        self._widget._running = True
        return self

    def destroy(self):
        """Destroy the canvas and unregister from the async event loop."""
        from blighty._async_loop import _canvas_map
        _canvas_map.pop(self.win_id, None)
        self._widget._running = False
        super().destroy()

    def dispose(self):
        """Dispose of the canvas (thread-safe in the async model)."""
        self.destroy()

    async def _dispatch_draw(self):
        """Internal: create context wrapper and call widget's draw()."""
        if not self._widget._running:
            return

        ctx = self._get_pycairo_context()
        if self._extended_context is None:
            self._extended_context = ExtendedContext(ctx, self._widget)

        ctx.push_group()
        try:
            await self._widget.draw(self._extended_context)
        finally:
            if self._widget._running:
                group = ctx.pop_group()
                ctx.set_source(group)
                ctx.save()
                ctx.set_operator(cairo.OPERATOR_SOURCE)
                ctx.paint()
                ctx.restore()

    def get_size(self):
        return (self._widget.__width__, self._widget.__height__)

    # --- Event routing to widget ---

    async def on_button_pressed(self, button, state, x, y):
        await self._widget.on_button_pressed(button, state, x, y)

    async def on_key_pressed(self, keysym, state):
        await self._widget.on_key_pressed(keysym, state)


def create_canvas(widget):
    """Create and return an X11 Canvas wrapping the given Widget."""
    w = widget.__width__
    h = widget.__height__
    canvas = Canvas(
        widget,
        widget.__x__, widget.__y__, w, h,
        interval=widget.__interval__,
        screen=widget.__screen__,
        window_type=widget.__window_type__,
        gravity=widget.__gravity__,
        sticky=widget.__sticky__,
        keep_below=widget.__keep_below__,
        skip_taskbar=widget.__skip_taskbar__,
        skip_pager=widget.__skip_pager__,
    )
    return canvas
