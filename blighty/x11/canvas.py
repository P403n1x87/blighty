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

This module provides the :class:`Canvas` class for the creation of X11
canvases.

The :class:`Canvas` class is, in Java terminoly, *abstract* and should not be
instantiated directly. Instead, applications should define their own subclasses
of the :class:`Canvas` and implement the :func:`on_draw` method, which gets called
periodically to perform the required draw operations using pycairo.

Once created, an instance of a subclass of :class:`Canvas` can be shown on
screen by calling the :func:`show` method. This starts drawing the canvas on
screen by calling the `on_draw` callback at regular intervals in time. Events
can be handled by starting the event loop with
:func:`blighty.x11.start_event_loop`, as described in more details in the
`Event handling`_ section.


Creating a canvas
-----------------

Canvases are created by simply subclassing the `Canvas` class and implementing
the :func:`on_draw` callback.

The :class:`Canvas` constructor (i.e. the :func:`__new__` magic method) takes
the following arguments:

+----------------+------------------------------------------------------------+
| Argument       | Description                                                |
+================+========================+===================================+
| *x*            | These arguments describe the basic geometry of the canvas. |
+----------------+ The *x* and *y* coordinates are relative to the ``gravity``|
| *y*            | argument (see below). The *width* and *height* arguments   |
+----------------+ give the canvas size in pixels.                            |
| *width*        |                                                            |
+----------------+                                                            |
| *height*       |                                                            |
+----------------+------------------------------------------------------------+
| *interval*     | The time interval between calls to the :func:`on_draw`     |
|                | callback, in `milliseconds`.                               |
|                |                                                            |
|                | **Default value**: 1000 (i.e. 1 second)                    |
+----------------+------------------------------------------------------------+
| *window_type*  | The type of window to create. The possible choices are     |
|                | enumerated in the ``blighty.CanvasType`` type and are      |
|                | named after the equivalent _NET_WM_WINDOW_TYPE hints for   |
|                | the window manager. This is analogous to conky's           |
|                | ``own_window_type`` configuration setting.                 |
|                |                                                            |
|                | **Default value**: ``CanvasType.DESKTOP``                  |
+----------------+------------------------------------------------------------+
| *gravity*      | Defines the coordinate system for the canvas relative to   |
|                | the screen. The allowed values are enumerated in the       |
|                | ``blighty.CanvasGravity`` type. This is the equivalent of  |
|                | the conky ``alignment`` configuration setting. For example,|
|                | the value ``CanvasGravity.SOUTH_EAST`` indicates that the  |
|                | canvas should be positioned relative to the bottom-right   |
|                | corner of the screen.                                      |
|                |                                                            |
|                | **Default value**: ``CanvasGravity.NORTH_WEST``            |
+----------------+------------------------------------------------------------+
| *sticky*       | Whether the window should *stick* to the desktop and hence |
|                | be visible in all workspaces.                              |
|                |                                                            |
|                | **Default value**: ``True``                                |
+----------------+------------------------------------------------------------+
| *keep_below*   | Whether the window should stay below any other window on   |
|                | the screen.                                                |
|                |                                                            |
|                | **Default value**: ``True``                                |
+----------------+------------------------------------------------------------+
| *skip_taskbar* | Whether the window should not have an entry in the taskbar.|
|                |                                                            |
|                | **Default value**: ``True``                                |
+----------------+------------------------------------------------------------+
| *skip_pager*   | Whether the window should not appear in the pager.         |
|                |                                                            |
|                | **Default value**: ``True``                                |
+----------------+------------------------------------------------------------+

Note that the interval can be changed dynamically by setting the ``interval``
attribute on the canvas object directly after it has been created.

If you want to distribute your subclasses of :class:`Canvas`, we recommend that
you create a static method ``build`` that returns an instance of the subclass,
with some of the argumets set to a predefined values. This is useful if you
want to distribute widgets with, e.g., a predefined size, as a Python module.

Showing the canvas
------------------

When a canvas is created, it is not immediately shown to screen. To map it to
screen and start the draw cycle one has to call the :func:`show` method
explicitly.

If you need to pass data to the canvas, you might want to do that before
calling this method, since presumably the :func:`on_draw` callback, which will
start to be called, makes use of it.

Finally, you must start the main event loop with
:func:`blighty.x11.start_event_loop` to start drawing on the canvases, and in
case that they should handle input events, like mouse button clicks or key
presses. Note however that execution in the current thread will halt at this
call, until it returns after a call to :func:`blighty.x11.stop_event_loop`.

For more details on how to handle events with your X11 canvases, see the
section `Event handling`_ below.


Disposing of a canvas
---------------------

If you want to programmatically dispose of a canvas, you can call the
:func:`dispose` method. This doesn't destroy the canvas immediately, but sends
a delete request to the main event loop instead. This is the preffered way of
getting rid of a canvas when you are running the event loop. You can also use
the :func:`destroy` method directly, which destroys the canvas immediately.
However this is not thread safe and should not be called in the :func:`on_draw`
callback when running the event loop.


Event handling
--------------

A feature that distinguishes blighty from conky is that it allows you to handle
simple user input on the canvases. Currently, X11 canvases support two events:
mouse button and key press events.

Mouse button events can be handled by implementing the
:func:`on_button_pressed` callback in the subclass of :class:`Canvas`. The
signature is the following::

    def on_button_pressed(self, button, state, x, y):

and the semantics of the arguments is the same as the ``XButtonEvent`` [1]_.

To handle key presses, implement the ``on_key_pressed`` callback with the
following signature::

    def on_key_pressed(self, keysym, state):

The ``state`` argument has the same semantics as in the
:func:`on_button_pressed` case, while the ``keysym`` is described, e,g, in the
`Keyboard Econding
<https://tronche.com/gui/x/xlib/input/keyboard-encoding.html>`_ section of the
Xlib guide.

A simple example
----------------

Here is a simple example that shows all the above concepts in action::

    from blighty import CanvasGravity
    from blighty.x11 import Canvas, start_event_loop

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


Extra features
==============

The :class:`Canvas` class comes with some handy extra features that can help
with common patterns, thus sparing you to have to type boilerplate code.

Brushes
-------

Brushes are a way to rebind methods from your subclass of :class:`Canvas` to
the Cairo context. Consider the following example::

    from random import random as r

    class RectCanvas(blighty.x11.Canvas):
        def rect(self, ctx, width, height):
            ctx.set_source_rgb(*[r() for _ in range(3)])
            ctx.rectangle(0, 0, width, height)
            ctx.fill()

        def on_draw(self, ctx):
            for i in range(4):
                self.rect(ctx, self.width >> i, self.height >> i)

The method ``rect`` is defined under the class ``RectCanvas`` for convenience.
However, from a logical point of view, it would make more sense for this method
to belong to ``ctx``, since the general pattern of these helper methods
requires that we pass ``ctx`` as one of the arguments.

If one prefixes the ``rect`` method with ``draw_`` then it turns into an
*implicit brush*. The :func:`on_draw` callback is called with the ``ctx``
argument being an instance of ``ExtendedContext``. The ``draw_rect`` brush is
then available from ``ctx`` as a bound method. The sample code above can then
be refactored as::

    from random import random as r

    class RectCanvas(blighty.x11.Canvas):
        def draw_rect(ctx, width, height):
            ctx.set_source_rgb(*[r() for _ in range(3)])
            ctx.rectangle(0, 0, width, height)
            ctx.fill()

        def on_draw(self, ctx):
            for i in range(4):
                ctx.rect(self.width >> i, self.height >> i)

Notice how ``draw_rect`` now takes less arguments, and how the first one is
``ctx``, the (extended) Cairo context.

If you do not wish to prefix your methods with ``draw_``, you can use the
:func:`blighty.brush` decorator instead to create an *explicit brush*. The code
would then look like this::

    from blighty import brush
    from random import random as r

    class RectCanvas(blighty.x11.Canvas):
        @brush
        def rect(ctx, width, height):
            ctx.set_source_rgb(*[r() for _ in range(3)])
            ctx.rectangle(0, 0, width, height)
            ctx.fill()

        def on_draw(self, ctx):
            for i in range(4):
                ctx.rect(self.width >> i, self.height >> i)


Text alignment
--------------

A common task is writing text on a canvas. With Cairo, text alignment usually
requires the same pattern: get the text extents and compute the new position.
To help with that, :class:`Canvas` objects come with a pre-defined
:func:`write_text` brush. Please refer to the API documentation below for usage
details.


Grid
----

When designing a canvas from scrach, it is hard to guess at positions without
any guiding lines. To help with precise placement, every :class:`Canvas` object
comes with a ``draw_grid`` brush that creates a rectangular grid on the canvas.
The spacing between the lines is set to 50 pixels by default (assuming that
the scale hasn't been changed before). This can be adjusted by passing the new
spacing along the two directions as arguments. Please refer to the API
documentation below for more details.


References
==========

.. [1] https://tronche.com/gui/x/xlib/events/keyboard-pointer/keyboard-pointer.html


Module API
==========
"""

from blighty import ExtendedContext, TextAlign, brush
from blighty._brush import BrushSets, draw_grid, write_text
from blighty._x11 import BaseCanvas


class Canvas(BaseCanvas):
    """X11 Canvas object.

    This class is meant to be used as a superclass and should not be
    instantiated directly. Subclasses should implement the :func:`on_draw`
    callback, which is invoked every time the canvas needs to be redrawn.
    Redraws happen at regular intervals in time, as specified by the
    ``interval`` attribute (also passed as an argument via the constructor).
    """

    def __init__(self, *args, **kwargs):
        """Initialise the Canvas object.

        If this method is overriden, keep in mind that the initialisation looks
        up for brushes inherited from all the superclasses. It is therefore
        important that the method from ``super()`` is called to ensure the
        correct functioning of the brushes.
        """
        BrushSets.inherit(type(self))
        self._extended_context = None

    def _on_draw(self, ctx):
        """Draw callback (internal).

        This is the callback that actually gets called from the BaseCanvas
        class. It ensures that an instance of ``ExtendedContext`` is created
        before going on to delegate the draw procedures to the user-defined
        :func:`on_draw` callback.

        If you want to skip some of the iterations and retain the current
        content of the canvas, you can return ``True``. This is useful to avoid
        performing the same drawing operations when not required because no
        data to display has changed.
        """
        if self._extended_context is None:
            self._extended_context = ExtendedContext(ctx, self)

        return self.on_draw(self._extended_context)

    def on_draw(self, ctx):
        """Draw callback.

        Once the :func:`show` method is called on a :class:`Canvas` object,
        this method gets called at regular intervals of time to perform the
        draw operation. Every subclass of :class:`Canvas` must implement this
        method.
        """
        raise NotImplementedError("on_draw method not implemented in subclass.")

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
