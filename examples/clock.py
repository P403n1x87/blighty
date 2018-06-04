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
