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
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.


#include "atelier.h"
#include <stdio.h>

#define GET_CALLBACK(object, method) PyObject_GetAttr((PyObject *) object, PyUnicode_FromString(method))

static PyObject * atelier = NULL;

static int list_updated = 0;

void
Atelier_init(void) {
  // Initialise Xlib and CPython for concurrent threads.
  XInitThreads();
  PyEval_InitThreads();

  // Initialise atelier to an empty list
  if (atelier != NULL) {
    Py_DECREF(atelier);
  }
  atelier = PyList_New(0);
  list_updated = 0;
}

void
Atelier_add_canvas(BaseCanvas * canvas) {
  // TODO: Check that the canvas is not registered already.
  PyList_Append(atelier, (PyObject*) canvas);
}


int
Atelier_remove_canvas(BaseCanvas * canvas) {
  BaseCanvas * c;
  for (int i = 0; i < PyList_Size(atelier); i++) {
    c = (BaseCanvas *) PyList_GetItem(atelier, i);
    if (c == canvas) {
      PyList_SetSlice(atelier, i, i + 1, NULL);
      list_updated = 1;
      return 1;
    }
  }
  return 0;
}


/******************************************************************************
 ** EVENT LOOP
 ******************************************************************************/

static const struct timespec POLL_SLEEP = {0, 1e6};

static int main_loop_running = 0;

static void
dispatch_event(BaseCanvas * canvas) {
  char keybuf[8];
  KeySym key;
  XEvent e;
  PyObject * cb;

  if (canvas->_destroy != 0) {
    PyObject_CallMethod((PyObject *) canvas, "destroy", NULL);
    return;
  }

  if (!XPending(canvas->display)) return;

  XNextEvent(canvas->display, &e);
  if (e.type >= LASTEvent) return;

  switch (e.type) {
  case ClientMessage:
    // TODO: Extend
    if ((Atom) e.xclient.data.l[0] == canvas->wm_delete_window) {
      PyObject_CallMethod((PyObject *) canvas, "destroy", NULL);
    }
    return;

  case ButtonPress:
    cb = GET_CALLBACK(canvas, "on_button_pressed");
    if (cb != NULL) {
      PyObject_CallObject(cb, Py_BuildValue("(iiii)",
        e.xbutton.button,
        e.xbutton.state,
        e.xbutton.x,
        e.xbutton.y
      ));
    }
    return;

  case KeyPress:
    cb = GET_CALLBACK(canvas, "on_key_pressed");
    if (cb != NULL) {
      XLookupString(&e.xkey, keybuf, sizeof(keybuf), &key, NULL);
      PyObject_CallObject(cb, Py_BuildValue("(ii)",
        key,
        e.xkey.state
      ));
    }
    return;

  case Expose:
    if (e.xexpose.count == 0) {
      BaseCanvas__redraw(canvas);
    }
    return;

  default:
    fprintf(stderr, "Dropping unhandled XEevent.type = %d.\n", e.type);
  }
}

PyObject *
Atelier_start_event_loop(PyObject * args, PyObject * kwargs) {
  if (main_loop_running > 0 || atelier == NULL) {
    Py_INCREF(Py_None); return Py_None;
  }

  main_loop_running = 1;

  while (main_loop_running != 0 && PyList_Size(atelier) > 0) {
    for (int i = 0; i < PyList_Size(atelier); i++) {
      dispatch_event((BaseCanvas *) PyList_GetItem(atelier, i));

      // Check if any of the dispatched events has deleted a canvas.
      if (list_updated > 0) {
        list_updated = 0;
        break;
      }

      Py_BEGIN_ALLOW_THREADS
      nanosleep(&POLL_SLEEP, NULL);
      Py_END_ALLOW_THREADS
    }
  }

  main_loop_running = 0;

  Py_INCREF(Py_None); return Py_None;
}

void
Atelier_stop_event_loop(void) {
  main_loop_running = 0;
}

int
Atelier_is_running(void) {
  return main_loop_running;
}
