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
This module provides support for creating GTK canvases. If you are trying to
replicate conky's behaviour then consider using the :mod:`blighty.x11`
submodule instead.
"""

try:
    import gi
except ImportError:
    raise ImportError("Unable to import PyGObject. See https://pygobject.readthedocs.io/ for more info.")

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


from .canvas import Canvas


def start_event_loop():
    """Start the main GTK event loop."""
    Gtk.main()


def stop_event_loop():
    """Stop the main GTK event loop."""
    Gtk.main_quit()
