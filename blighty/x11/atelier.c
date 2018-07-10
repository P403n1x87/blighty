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

#define LOOP_INTERVAL 2000

static PyObject * atelier = NULL;

static Display * display = NULL;

static PyObject *
get_callback(PyObject * object, char * method) {
  PyObject * py_method = PyUnicode_FromString(method);
  return PyObject_HasAttr(object, py_method) > 0 ? PyObject_GetAttr(object, py_method) : NULL;
}

void
Atelier_set_display(Display * d) {
  display = d;
}

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
      return PyList_Size(atelier);
    }
  }
  return -1;
}


/******************************************************************************
 ** EVENT LOOP
 ******************************************************************************/

static int main_loop_running = 0;


static void
thread_sleep(useconds_t usecs) {
  Py_BEGIN_ALLOW_THREADS
  usleep(usecs);
  Py_END_ALLOW_THREADS
}


static void
dispatch_event(BaseCanvas * canvas, XEvent * e) {
  char keybuf[8];
  KeySym key;
  PyObject * cb;

  switch (e->type) {
  case ClientMessage:
    // TODO: Extend
    if ((Atom) e->xclient.data.l[0] == canvas->wm_delete_window) {
      PyObject_CallMethod((PyObject *) canvas, "destroy", NULL);
    }
    return;

  case ButtonPress:
    cb = get_callback((PyObject *) canvas, "on_button_pressed");
    if (cb != NULL) {
      PyObject_CallObject(cb, Py_BuildValue("(iiii)",
        e->xbutton.button,
        e->xbutton.state,
        e->xbutton.x,
        e->xbutton.y
      ));
    }
    return;

  case KeyPress:
    cb = get_callback((PyObject *) canvas, "on_key_pressed");
    if (cb != NULL) {
      XLookupString(&(e->xkey), keybuf, sizeof(keybuf), &key, NULL);
      PyObject_CallObject(cb, Py_BuildValue("(ii)",
        key,
        e->xkey.state
      ));
    }
    return;

  case Expose:
    if (e->xexpose.count == 0) {
      if (canvas->_needs_redraw != 0) {
        BaseCanvas__on_draw(canvas, canvas->context_arg);
        canvas->_needs_redraw = 0;
      }

      // Only clear the window when we are sure we are ready to paint.
      BaseCanvas__redraw(canvas);

      if (PyErr_Occurred() != NULL) {
        PyErr_Print();
        PyObject_CallMethod((PyObject *) canvas, "dispose", NULL);
        break;
      }
    }
    return;

  default:
    fprintf(stderr, "Dropping unhandled XEevent.type = %d.\n", e->type);
  }
}

PyObject *
Atelier_start_event_loop(PyObject * args, PyObject * kwargs) {
  if (main_loop_running > 0 || atelier == NULL) {
    Py_INCREF(Py_None); return Py_None;
  }

  main_loop_running = 1;

  XEvent e;
  BaseCanvas * canvas;
  while (main_loop_running != 0 && PyList_Size(atelier) > 0 && display != NULL) {
    Py_BEGIN_ALLOW_THREADS
    XNextEvent(display, &e);
    Py_END_ALLOW_THREADS

    if (e.type >= LASTEvent) continue;
    // Find the canvas based on window ID
    int found = 0;
    for (int i = 0; i < PyList_Size(atelier); i++) {
      canvas = (BaseCanvas *) PyList_GetItem(atelier, i);
      if (canvas->win_id == e.xany.window) {
        found = 1;
        break;
      }
    }

    // TODO: Raise RuntimeError!
    if (!found) {
      fprintf(stderr, "Canvas not found!\n");
      return;
    }

    dispatch_event(canvas, &e);
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
