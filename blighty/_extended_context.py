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

"""Simplified cairo context wrapper.

Provides access to the containing widget via the ``canvas`` attribute,
and proxies all other attribute access to the underlying ``cairo.Context``.
"""


class ExtendedContext:
    """Thin wrapper around ``cairo.Context`` that exposes the owning widget.

    The ``canvas`` attribute gives access to the widget instance (for
    reading ``width``, ``height``, ``data``, etc.).  All other attribute
    lookups are forwarded to the underlying ``cairo.Context``.
    """

    def __init__(self, ctx, canvas):
        self._ctx = ctx
        self.canvas = canvas

    def __getattr__(self, name):
        return getattr(self._ctx, name)
