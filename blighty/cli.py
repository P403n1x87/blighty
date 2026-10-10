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

"""CLI entry point for blighty.

Usage::

    blighty [-b x11|gtk] script.py

Loads the user script, discovers all Widget subclasses, instantiates them,
and starts the event loop.
"""

import argparse
import importlib.util
import inspect
import sys

from blighty import Widget


def _load_script(path):
    """Load a Python script and return its module namespace."""
    module_name = path.rsplit("/", 1)[-1].rsplit(".", 1)[0]
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _discover_widgets(module):
    """Find all concrete Widget subclasses defined in the module."""
    widgets = []
    for name, obj in inspect.getmembers(module, inspect.isclass):
        if issubclass(obj, Widget) and obj is not Widget:
            widgets.append(obj)
    return widgets


def _create_canvases(widget_classes, backend):
    """Instantiate widgets and wrap them in backend canvases."""
    if backend == "x11":
        from blighty.x11 import create_canvas
    elif backend == "gtk":
        from blighty.gtk import create_canvas
    else:
        raise ValueError("Unknown backend: %s (use 'x11' or 'gtk')" % backend)

    canvases = []
    for cls in widget_classes:
        widget = cls()
        canvas = create_canvas(widget)
        canvas.show()
        canvases.append(canvas)
    return canvases


def main():
    parser = argparse.ArgumentParser(
        prog="blighty",
        description="Blighty — Desktop Widget Manager",
    )
    parser.add_argument(
        "-b", "--backend",
        choices=["x11", "gtk"],
        default="x11",
        help="Backend to use (default: x11)",
    )
    parser.add_argument(
        "script",
        help="Python script containing Widget subclasses",
    )

    args = parser.parse_args()

    module = _load_script(args.script)
    widget_classes = _discover_widgets(module)

    if not widget_classes:
        print("No Widget subclasses found in %s" % args.script, file=sys.stderr)
        sys.exit(1)

    canvases = _create_canvases(widget_classes, args.backend)

    if args.backend == "x11":
        from blighty._async_loop import start_event_loop
        start_event_loop()
    elif args.backend == "gtk":
        from blighty.gtk import start_event_loop
        start_event_loop()


if __name__ == "__main__":
    main()
