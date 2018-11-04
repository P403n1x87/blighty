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

from random import random as r

import blighty.x11 as x11
from blighty import CanvasGravity


class MyCanvas(x11.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.r = 50.0
        self.d = 4.0

    def on_button_pressed(self, button, state, x, y):
        if button == 1 and state == 16:
            self.dispose()

    def on_key_pressed(self, keysym, state):
        if keysym == 65307:
            self.dispose()

    def on_draw(self, cr):
        cr.set_line_width(8)
        cr.set_source_rgba(*[r() for _ in range(4)])

        w, h = self.get_size()

        if self.r > 92 or self.r < 10:
            self.d *= -1
        self.r += self.d

        cr.arc(w >> 1, h >> 1, self.r, 0, 2 * 3.14159265)
        cr.stroke()

        if self.r == 10:
            self.dispose()


def test_canvas():
    canvases = [
        MyCanvas(
            200 * i, 200 * i,
            width=200, height=200,
            interval=42,
            gravity=CanvasGravity.CENTER
        ) for i in range(-1, 2)
    ]

    for canvas in canvases:
        assert canvas.interval == 42

        canvas.interval = 100
        assert canvas.show() is None

    assert x11.start_event_loop() is None


def test_canvas_xinerama():
    canvases = [
        MyCanvas(
            200 * i, 200 * i,
            width=200, height=200,
            interval=42,
            screen=1,
            gravity=CanvasGravity.CENTER
        ) for i in range(-1, 2)
    ]

    for canvas in canvases:
        assert canvas.interval == 42

        canvas.interval = 100
        assert canvas.show() is None

    assert x11.start_event_loop() is None


def test_draw_methods():

    class DrawMethodsCanvas(x11.Canvas):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self.c = 0

        def on_button_pressed(self, button, state, x, y):
            if button == 1:
                self.dispose()

        def draw_rect(ctx, width, height):
            ctx.set_source_rgb(*[r() for _ in range(3)])
            ctx.rectangle(0, 0, width, height)
            ctx.fill()

        def on_draw(self, ctx):
            if self.c > 2:
                self.dispose()
                return

            for i in range(4):
                ctx.draw_rect(self.width >> i, self.height >> i)

            self.c += 1

    canvas = DrawMethodsCanvas(40, 40, 128, 128, interval = 1500)
    canvas.show()
    x11.start_event_loop()


def test_draw_once():

    class DrawMethodsCanvas(x11.Canvas):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self.c = 0

        def on_button_pressed(self, button, state, x, y):
            if button == 1:
                self.dispose()

        def draw_rect(ctx, width, height):
            ctx.set_source_rgb(*[r() for _ in range(3)])
            ctx.rectangle(0, 0, width, height)
            ctx.fill()

        def on_draw(self, ctx):
            if self.c > 2:
                self.dispose()
                return

            self.c += 1

            if self.c > 1:
                return False

            for i in range(4):
                ctx.draw_rect(self.width >> i, self.height >> i)

    canvas = DrawMethodsCanvas(40, 40, 128, 128, interval = 1500)
    canvas.show()
    x11.start_event_loop()


if __name__ == "__main__":
    test_canvas()
    test_draw_methods()
