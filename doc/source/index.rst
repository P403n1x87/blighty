.. blighty documentation master file, created by
   sphinx-quickstart on Wed Jun 27 21:19:50 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to blighty's documentation!
===================================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

The ``blighty`` project
***********************

This is the documentation for ``blighty``, a Python package for the creation
of widgets for the Linux desktop. The idea is to replicate the wonders of
`conky <https://github.com/brndnmtthws/conky>`_, but with Python support
instead of Lua.


Usage
=====

Using ``blighty`` is very simple and should come quite natural to you,
especially if you already have experience with Cairo from conky.

All the you need to do is extend one of the ``Canvas`` classes provided by the
package (e.g. :class:`blighty.x11.canvas.Canvas`) and implement the ``on_draw``
method.

Start by reading through the documentation of the :mod:`blighty.x11` module and
then make your way to the
`examples <https://github.com/P403n1x87/blighty/tree/master/examples>`_
folder from the GitHub repository.


A clock widget
==============

Here is the example of a simple clock widget::

    from blighty import CanvasGravity, brush
    from blighty.x11 import Canvas, start_event_loop

    import datetime

    from math import pi as PI


    class Clock(Canvas):
        def on_button_pressed(self, button, state, x, y):
            self.dispose()

        @brush
        def hand(ctx, angle, length, thickness):
            ctx.save()
            ctx.set_source_rgba(1, 1, 1, 1)
            ctx.set_line_width(thickness)
            ctx.rotate(angle)
            ctx.move_to(0, length * .2)
            ctx.line_to(0, -length)
            ctx.stroke()
            ctx.restore()

        def on_draw(self, ctx):
            now = datetime.datetime.now()

            ctx.translate(self.width >> 1, self.height >> 1)

            ctx.hand(
                angle = now.second / 30 * PI,
                length = (self.height >> 1) * .9,
                thickness = 1
            )

            mins = now.minute + now.second / 60
            ctx.hand(
                angle = mins / 30 * PI,
                length = (self.height >> 1) * .8,
                thickness = 3
            )

            hours = (now.hour % 12) + mins / 60
            ctx.hand(
                angle = hours / 6 * PI,
                length = (self.height >> 1) * .5,
                thickness = 6
            )


    if __name__ == "__main__":
        clock = Clock(0, 0, 400, 400, gravity = CanvasGravity.CENTER)
        clock.show()
        start_event_loop()


Issues
======

If you find any issues with ``blighty``, or for a list of all the currently
known and open issues, please visit
https://github.com/P403n1x87/blighty/issues.


The brag corner
===============

The ``blighty`` project was founded by Gabriele Tornetta in 2018.

.. toctree::
  :caption: Contents:

  blighty
