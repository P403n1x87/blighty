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
Description
===========

This module provides the ``Canvas`` class for the creation of X11 canvases.

We advise that you consider using the ``Canvas`` class provided by the
:mod:`blighty.x11` submodule instead, as it gives more portability
acrossdifferent display managers. The interface of
:class:`blighty.gtk.canvas.Canvas` is identical to that of
:class:`blighty.x11.canvas.Canvas`, so we refer you to the latter for more
details of how to deal with GTK canvases. The key difference is basically in
the class that your canvases have to extend. For example, if you have an
X11-based canvas and you have the following import in your source code::

    from blighty.x11 import Canvas, start_event_loop

all you have to do is replace ``blighty.x11`` with ``blighty.gtk``::

    from blighty.gtk import Canvas, start_event_loop

and the same code will work just fine and will produce the same result.

Here is the same simple example from the :mod:`blighty.x11` module, adapted
to the GTK case::

    from blighty import CanvasGravity
    from blighty.gtk import Canvas, start_event_loop

    class MyCanvas(Canvas):
        @staticmethod
        def build(x, y):
            return MyCanvas(x, y, 200, 200, gravity = CanvasGravity.NORTH)

        def on_button_pressed(self, button, state, x, y):
            if button == 1:  # Left mouse button pressed
                self.dispose()

        def on_draw(self, ctx):
            ctx.set_source_rgb(1, 0, 0)
            ctx.rectangle(0, 0, ctx.canvas.width >> 1, ctx.canvas.height >> 1)
            ctx.fill()

    if __name__ == "__main__":
        # Instantiate the canvas
        canvas = MyCanvas.build()

        # Map it on screen
        canvas.show()

        # Start the event loop
        start_event_loop()

The only difference is on the second line, where we reference the
:mod:`blighty.gtk` submodule instead of :mod:`blighty.x11`.


Extra features
==============

There are some features that are unique to GTK canvases only. This implies
that, if you have a GTK canvas and you use some of these features, you won't
be able to run the same code as an X11 canvas without changes.


Access the underlying GTK window
--------------------------------

GTK canvases are special GTK windows that have been configured to be used as
desktop widgets. Every instance of the :class:`blighty.gtk.canvas.Canvas` class
will expose the underlying :class:`GTKWindow` via ``self``.


Module API
==========
"""

try:
    import gi
except ImportError:
    raise ImportError("Unable to import PyGObject. See https://pygobject.readthedocs.io/ for more info.")

gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk

from time import sleep
from blighty import CanvasType, CanvasGravity, TextAlign, ExtendedContext, brush
from blighty._brush import BrushSets, draw_grid, write_text

WINDOW_TYPE_MAP = [
    Gdk.WindowTypeHint.NORMAL,
    Gdk.WindowTypeHint.DESKTOP,
    Gdk.WindowTypeHint.DOCK,
    Gdk.WindowTypeHint.TOOLBAR,
]


class Canvas(Gtk.Window):
    """GTK Canvas object.

    This class is meant to be used as a superclass and should not be
    instantiated directly. Subclasses should implement the ``on_draw``
    callback, which is invoked every time the canvas needs to be redrawn.
    Redraws happen at regular intervals in time, as specified by the
    ``interval`` attribute (also passed as an argument via the constructor).
    """

    def __init__(self, x, y, width, height,
                 interval = 1000,
                 window_type = CanvasType.DESKTOP,
                 gravity = CanvasGravity.NORTH_WEST,
                 sticky = True,
                 keep_below = True,
                 skip_taskbar = True,
                 skip_pager = True
                 ):
        """Initialise the Canvas object.

        If this method is overriden, keep in mind that the initialisation looks
        up for brushes inherited from all the superclasses. It is therefore
        important that the method from ``super()`` is called to ensure the
        correct functioning of the brushes.
        """
        super().__init__()

        self.interval = interval
        self.gravity = gravity

        self.set_type_hint(WINDOW_TYPE_MAP[window_type])

        if skip_taskbar:
            self.set_skip_taskbar_hint(True)

        if skip_pager:
            self.set_skip_pager_hint(True)

        if sticky:
            self.stick()

        if keep_below:
            self.set_keep_below(keep_below)

        self.screen = self.get_screen()

        self.width = width
        self.height = height
        self.set_size_request(width, height)
        self.move(x, y)

        # Handle gravity with respect to parent window manually
        self.set_gravity(gravity)

        # Make the window transparent
        visual = self.screen.get_rgba_visual()
        if visual is not None and self.screen.is_composited():
            self.set_visual(visual)

        self.set_app_paintable(True)

        # Connect signals
        self.connect("draw", self._on_draw)
        self.connect("delete-event", Gtk.main_quit)

        BrushSets.inherit(type(self))
        self._extended_context = None

    def _translate_coordinates(self, x, y):
        if (self.gravity - 1) % 3 == 0:
            tx = x
        elif (self.gravity - 2) % 3 == 0:
            tx = ((self.screen.get_width() - self.width) >> 1) + x
        else:
            tx = self.screen.get_width() - self.width - x

        if self.gravity <= 3:
            ty = y
        elif self.gravity <= 6:
            ty = ((self.screen.get_height() - self.height) >> 1) + y
        else:
            ty = self.screen.get_height() - self.height - y

        return tx, ty

    def _on_draw(self, widget, cr):
        self._extended_context = ExtendedContext(cr, self)

        self.on_draw(self._extended_context)

        widget.queue_draw()

        sleep(self.interval / 1000.)

    def on_draw(self, cr):
        """Draw callback.

        Once the :func:`show` method is called on a :class:`Canvas` object,
        this method gets called at regular intervals of time to perform the
        draw operation. Every subclass of :class:`Canvas` must implement this
        method.
        """
        raise NotImplementedError("on_draw method not implemented in subclass.")

    def show(self):
        """Map the canvas to screen and set it ready for drawing."""
        self.show_all()

    def move(self, x, y):
        """Move the canvas to new coordinates.

        The *x* and *y* coordinates are relative to the canvas gravity.
        """
        self.x = x
        self.y = y
        return super().move(*self._translate_coordinates(x, y))

    def dispose(self):
        """Dispose of the canvas.

        For GTK-based canvases, this is equivalent to calling the
        :func:`destroy` method.
        """
        self.destroy()

    # TODO: Remove duplicate docstrings

    def draw_grid(ctx, x = 50, y = 50):
        """Draw a grid on the canvas [**implicit brush**].

        This implicit brush method is intended to help with determining the
        location of points on the canvas during development.

        Args:
            x (int): The horizontal spacing between lines.
            y (int): The vertical spacing between lines.
        """
        draw_grid(ctx, x, y)

    @brush
    def write_text(cr, x, y, text, align = TextAlign.TOP_LEFT):
        """Write aligned text [**explicit brush**].

        This explicit brush method helps write aligned text on the canvas. The
        *x* and *y* coordinates are relative to the specified *alignment*. By
        default, this is ``blighty.TextAlign.TOP_LEFT``, meaning that the text
        will be left-aligned and on top of the horizontal line that passes
        through *y* on the vertical axis. In terms of the point *(x,y)* on the
        Canvas, the text will develop in the NE direction.

        The return value is the text extents, in case that some further draw
        operations depend on the space required by the text to be drawn on the
        canvas.

        Note that font face and size need to be set on the Cairo context prior
        to a call to this method.

        Args:
            x (int): The horizontal coordinate.
            y (int): The vertical coordinate.
            text (str): The text to write.
            align (int): The text alignment. Detaulf is ``TextAlign.TOP_LEFT``.

        Returns:
            tuple: The same return value as ``cairo.text_extents``.

        """
        return write_text(cr, x, y, text, align)
