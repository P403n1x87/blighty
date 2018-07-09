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

import blighty.x11 as x11
from blighty import brush

from random import random as r


def test_brush():

    class DrawMethodsCanvas(x11.Canvas):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self.c = False

        def on_button_pressed(self, button, state, x, y):
            if button == 1:
                self.dispose()

        @brush
        def rect(ctx, width, height):
            ctx.set_source_rgb(*[r() for _ in range(3)])
            ctx.rectangle(0, 0, width, height)
            ctx.fill()

        def on_draw(self, ctx):
            if self.c:
                self.dispose()
                return

            for i in range(4):
                ctx.rect(self.width >> i, self.height >> i)

            self.c = True

    canvas = DrawMethodsCanvas(40, 40, 128, 128, interval = 3000)
    canvas.show()
    x11.start_event_loop()


def test_grid():

    class DrawMethodsCanvas(x11.Canvas):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self.c = False

        def on_button_pressed(self, button, state, x, y):
            if button == 1:
                self.dispose()

        def on_draw(self, ctx):
            if self.c:
                self.dispose()
                return

            ctx.draw_grid()

            self.c = True

    canvas = DrawMethodsCanvas(40, 40, 512, 512, interval = 3000)
    canvas.show()
    x11.start_event_loop()


def test_text():

    from blighty.x11 import Canvas

    class DrawMethodsCanvas(Canvas):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self.c = False

        def on_button_pressed(self, button, state, x, y):
            if button == 1:
                self.dispose()

        def on_draw(self, ctx):
            if self.c:
                self.dispose()
                return

            for i in range(1, 10):
                ctx.write_text(self.width >> 1, self.height >> 1, str(i), align = i)

            self.c = True

    canvas = DrawMethodsCanvas(40, 40, 128, 128, interval = 3000)
    canvas.show()
    x11.start_event_loop()

# def test_invalid_brush():
#
#     class DrawMethodsCanvas(x11.Canvas):
#         def __init__(self, *args, **kwargs):
#             super().__init__(*args, **kwargs)
#
#             self.c = False
#
#         def on_button_pressed(self, button, state, x, y):
#             if button == 1:
#                 self.destroy()
#
#         @brush
#         def rectangle(ctx, width, height):
#             ctx.set_source_rgb(*[r() for _ in range(3)])
#             ctx.rectangle(0, 0, width, height)
#             ctx.fill()
#
#         def on_draw(self, ctx):
#             if self.c:
#                 self.dispose()
#                 return
#
#             for i in range(4):
#                 ctx.rectangle(self.width >> i, self.height >> i)
#
#             self.c = True
#
#     canvas = DrawMethodsCanvas(40, 40, 128, 128, interval = 3000)
#     canvas.show()
#     x11.start_event_loop()


if __name__ == "__main__":
    test_brush()
