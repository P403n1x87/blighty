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

"""Shared async event loop for blighty canvases.

Each canvas runs as an independent asyncio task.  The X11 display fd is
watched for incoming events, and each canvas has a periodic refresh task
that drives the widget's update/draw cycle.
"""

import asyncio
import logging

logger = logging.getLogger(__name__)

# X11 event type constants
Expose = 12
ButtonPress = 4
KeyPress = 2
ClientMessage = 33

# Registry: win_id -> canvas
_canvas_map = {}


def _on_x11_fd_readable():
    """Called by the event loop when the X11 display fd has data."""
    from blighty._x11 import poll_events

    events = poll_events()
    for ev in events:
        try:
            _dispatch_x11_event(ev)
        except Exception:
            logger.exception("Error dispatching X11 event: %s", ev)


def _dispatch_x11_event(event):
    """Dispatch a single X11 event dict to the appropriate canvas callback."""
    win_id = event["window"]
    canvas = _canvas_map.get(win_id)
    if canvas is None:
        return

    etype = event["type"]

    if etype == ButtonPress:
        asyncio.ensure_future(canvas.on_button_pressed(
            event["button"], event["state"], event["x"], event["y"]
        ))

    elif etype == KeyPress:
        asyncio.ensure_future(canvas.on_key_pressed(
            event["keysym"], event["state"]
        ))

    elif etype == ClientMessage:
        canvas.destroy()


async def _canvas_tick_task(canvas):
    """Periodically tick a canvas: call update(), compare hash, draw if changed."""
    interval = canvas._widget.__interval__ / 1000.0
    while canvas._widget._running:
        await asyncio.sleep(interval)
        try:
            await canvas._widget._tick()
        except Exception:
            logger.exception("Error in tick for %s", canvas._widget)


async def _watchdog():
    """Stop the event loop when no canvases remain."""
    loop = asyncio.get_event_loop()
    while _canvas_map:
        await asyncio.sleep(0.5)
    loop.call_soon(loop.stop)


def start_event_loop():
    """Start the async event loop for all registered canvases.

    Each canvas is managed as an independent asyncio task.  The loop
    exits when all canvases have been destroyed.
    """
    from blighty._x11 import get_display_fd

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Watch the X11 display fd for incoming events
    fd = get_display_fd()
    loop.add_reader(fd, _on_x11_fd_readable)

    # Start a tick task for each registered canvas
    for canvas in list(_canvas_map.values()):
        canvas._widget._running = True
        loop.create_task(_canvas_tick_task(canvas))

    # Watch for all canvases being destroyed
    loop.create_task(_watchdog())

    try:
        loop.run_forever()
    finally:
        loop.remove_reader(fd)
        loop.close()
