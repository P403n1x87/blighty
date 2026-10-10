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


#include "atelier.h"
#include <stdio.h>

static Display            * display = NULL;
static XineramaScreenInfo * info    = NULL;
static int                  n_scr   = 0;


// ----------------------------------------------------------------------------
Display *
Atelier_get_display(void) {
  if (display == NULL)
    Atelier_set_display(XOpenDisplay(NULL));

  return display;
}


// ----------------------------------------------------------------------------
void
Atelier_set_display(Display * d) {
  if (d == NULL) {
    if (display != NULL) {
      if (info != NULL) {
        XFree(info);
        info = NULL;
        n_scr = 0;
      }

      XCloseDisplay(display);
      display = NULL;
    }
    return;
  }

  display = d;

  // Xinerama support
  int event, error;

  if (!XineramaQueryExtension(d, &event, &error))
    return;

  if (!XineramaIsActive(d))
    return;

  info = XineramaQueryScreens(d, &n_scr);
}


// ----------------------------------------------------------------------------
XineramaScreenInfo *
Atelier_get_screen_info(int screen) {
  if (screen < n_scr) {
    for (register int i = 0; i < n_scr; i++)
      if (screen == info[i].screen_number)
        return &(info[i]);
  }

  return NULL;
}


// ----------------------------------------------------------------------------
void
Atelier_init(void) {
  XInitThreads();
  PyEval_InitThreads();
}


// ----------------------------------------------------------------------------
// ASYNC SUPPORT: expose display fd and non-blocking event polling
// ----------------------------------------------------------------------------

PyObject *
Atelier_get_display_fd(PyObject * self, PyObject * args) {
  Display * d = Atelier_get_display();
  if (d == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "No X11 display connection.");
    return NULL;
  }
  return PyLong_FromLong(ConnectionNumber(d));
}


// X11 event type constants for Python
#define X11_BUTTON_PRESS    4
#define X11_KEY_PRESS       2
#define X11_EXPOSE         12
#define X11_CLIENT_MESSAGE 33

PyObject *
Atelier_poll_events(PyObject * self, PyObject * args) {
  Display * d = Atelier_get_display();
  if (d == NULL) {
    Py_INCREF(Py_None); return Py_None;
  }

  PyObject * events = PyList_New(0);
  XEvent e;

  for (;;) {
    int pending;
    Py_BEGIN_ALLOW_THREADS
    pending = XPending(d);
    Py_END_ALLOW_THREADS

    if (!pending) break;

    Py_BEGIN_ALLOW_THREADS
    XNextEvent(d, &e);
    Py_END_ALLOW_THREADS

    if (e.type >= LASTEvent) continue;

    PyObject * dict = PyDict_New();
    PyDict_SetItemString(dict, "type",   PyLong_FromLong(e.type));
    PyDict_SetItemString(dict, "window", PyLong_FromUnsignedLong(e.xany.window));

    switch (e.type) {
    case ButtonPress:
      PyDict_SetItemString(dict, "button", PyLong_FromLong(e.xbutton.button));
      PyDict_SetItemString(dict, "state",  PyLong_FromLong(e.xbutton.state));
      PyDict_SetItemString(dict, "x",      PyLong_FromLong(e.xbutton.x));
      PyDict_SetItemString(dict, "y",      PyLong_FromLong(e.xbutton.y));
      break;

    case KeyPress: {
      char keybuf[8];
      KeySym keysym;
      Py_BEGIN_ALLOW_THREADS
      XLookupString(&(e.xkey), keybuf, sizeof(keybuf), &keysym, NULL);
      Py_END_ALLOW_THREADS
      PyDict_SetItemString(dict, "keysym", PyLong_FromLong(keysym));
      PyDict_SetItemString(dict, "state",  PyLong_FromLong(e.xkey.state));
      break;
    }

    case ClientMessage:
      PyDict_SetItemString(dict, "atom", PyLong_FromUnsignedLong(e.xclient.data.l[0]));
      break;
    }

    PyList_Append(events, dict);
    Py_DECREF(dict);
  }

  return events;
}
