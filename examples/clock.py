"""Blighty clock widget example.

Run with: blighty clock.py
"""

import datetime
from math import pi as PI
from dataclasses import dataclass

from blighty import Widget, CanvasGravity


@dataclass(frozen=True)
class ClockData:
    hour: int
    minute: int
    second: int


class Clock(Widget):
    __interval__ = 1000
    __width__ = 400
    __height__ = 400
    __gravity__ = CanvasGravity.CENTER

    def update(self):
        now = datetime.datetime.now()
        return ClockData(now.hour, now.minute, now.second)

    def _hand(self, ctx, angle, length, thickness):
        ctx.save()
        ctx.set_source_rgba(1, 1, 1, 1)
        ctx.set_line_width(thickness)
        ctx.rotate(angle)
        ctx.move_to(0, length * .2)
        ctx.line_to(0, -length)
        ctx.stroke()
        ctx.restore()

    async def draw(self, ctx):
        ctx.translate(self.width >> 1, self.height >> 1)

        self._hand(ctx,
            angle=self.data.second / 30 * PI,
            length=(self.height >> 1) * .9,
            thickness=1
        )

        mins = self.data.minute + self.data.second / 60
        self._hand(ctx,
            angle=mins / 30 * PI,
            length=(self.height >> 1) * .8,
            thickness=3
        )

        hours = (self.data.hour % 12) + mins / 60
        self._hand(ctx,
            angle=hours / 6 * PI,
            length=(self.height >> 1) * .5,
            thickness=6
        )

    async def on_button_pressed(self, button, state, x, y):
        self.dispose()
