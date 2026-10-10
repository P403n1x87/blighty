// This file is part of "blighty" which is released under GPL.
//
// See file LICENCE or go to http://www.gnu.org/licenses/ for full license
// details.
//
// blighty is a desktop widget creation and management library for Python 3.
//
// Copyright (c) 2018 Gabriele N. Tornetta <phoenix1987@gmail.com>.
// All rights reserved.
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.

#include <Python.h>
#include "pycairo.h"

#include "atelier.h"

extern PyTypeObject BaseCanvasType;


static PyMethodDef x11methods[] = {
  {
    "get_display_fd",
    Atelier_get_display_fd,
    METH_NOARGS,
    "Returns the file descriptor of the X11 display connection for asyncio integration."
  },
  {
    "poll_events",
    Atelier_poll_events,
    METH_NOARGS,
    "Non-blocking poll of all pending X11 events. Returns a list of event dictionaries."
  },
  {NULL, NULL, 0, NULL}
};

static PyModuleDef x11module = {
  PyModuleDef_HEAD_INIT,
  "_x11",
  "C X11 support module for blighty.",
  -1,
  x11methods, // m_methods
  NULL, NULL, NULL, NULL
};

PyMODINIT_FUNC
PyInit__x11(void)
{
  PyObject* m;

  if (PyType_Ready(&BaseCanvasType) < 0)
    return NULL;

  m = PyModule_Create(&x11module);
  if (m == NULL)
    return NULL;

  if (import_cairo() < 0)
    return NULL;

  Py_INCREF(&BaseCanvasType);
  PyModule_AddObject(m, "BaseCanvas", (PyObject *)&BaseCanvasType);

  // Initialise Atelier (XInitThreads, etc.)
  Atelier_init();
  return m;
}
