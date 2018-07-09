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

#ifndef BASE_CANVAS_H
#define BASE_CANVAS_H

#include <Python.h>
#include "structmember.h"

#include <X11/Xlib.h>
#include <X11/Xatom.h>
#include <X11/Xutil.h>
#include <cairo.h>
#include <cairo-xlib.h>


typedef struct {
  PyObject_HEAD
  // Geometry
  int               x;
  int               y;
  int               width;
  int               height;

  // X/Cairo data structures
  cairo_t         * context;
  PyObject        * context_arg;
  cairo_surface_t * surface;
  Display         * display;
  int               screen;
  Drawable          win_id;

  // Signals
  Atom              wm_delete_window;

  // Attributes
  unsigned int      interval;
  int               gravity;

  // Internal attributes
  int               _running;
  long              _expiry;
  int               _drawing;
  int               _needs_redraw;
} BaseCanvas;

void BaseCanvas__redraw(BaseCanvas * self);

#ifdef BASE_CANVAS_C
// ---- METHODS ----
static void       BaseCanvas_dealloc  (BaseCanvas *);
static PyObject * BaseCanvas_new      (PyTypeObject *, PyObject *, PyObject *);
static int        BaseCanvas_init     (BaseCanvas *, PyObject *, PyObject *);

static PyObject * BaseCanvas_move     (BaseCanvas *, PyObject *, PyObject *);
static PyObject * BaseCanvas_show     (BaseCanvas *);
static PyObject * BaseCanvas_get_size (BaseCanvas *);
static PyObject * BaseCanvas_dispose  (BaseCanvas *);
static PyObject * BaseCanvas_destroy  (BaseCanvas *);


static PyMethodDef BaseCanvas_methods[] = {
  {"move"     , (PyCFunction) BaseCanvas_move      , METH_VARARGS | METH_KEYWORDS,
      "Move the canvas to new coordinates.\n\n"

      "The *x* and *y* coordinates are relative to the canvas gravity."
  },
  {"show"     , (PyCFunction) BaseCanvas_show      , METH_NOARGS,
      "Map the canvas to screen and set it ready for drawing."
  },
  {"get_size" , (PyCFunction) BaseCanvas_get_size  , METH_NOARGS,
      "Get the canvas size.\n\n"

      "Returns:\n"
      "  tuple: the 2-tuple of width and height in pixels."
  },
  {"dispose"  , (PyCFunction) BaseCanvas_dispose   , METH_NOARGS,
      "Mark the canvas as ready to be destroyed to free up resources."
  },
  {"destroy"  , (PyCFunction) BaseCanvas_destroy   , METH_NOARGS,
      "Destroy the canvas.\n\n"

      "This method is not thread-safe. Use the :func:`dispose` method instead."
  },
  {NULL}  /* Sentinel */
};


// ---- ATTRIBUTES ----
static PyMemberDef BaseCanvas_members[] = {
  {"interval" , T_INT , offsetof(BaseCanvas, interval) , 0        , "The refresh interval, in milliseconds."},
  {"x"        , T_INT , offsetof(BaseCanvas, x)        , READONLY , "The canvas *x* coordinate. *Read-only*."},
  {"y"        , T_INT , offsetof(BaseCanvas, y)        , READONLY , "The canvas *y* coordinate. *Read-only*."},
  {"width"    , T_INT , offsetof(BaseCanvas, width)    , READONLY , "The canvas width. *Read-only*."},
  {"height"   , T_INT , offsetof(BaseCanvas, height)   , READONLY , "The canvas height. *Read-only*."},
  {NULL}  /* Sentinel */
};

// ---- OBJECT TYPE DECLARATION ----
PyTypeObject BaseCanvasType = {
  PyVarObject_HEAD_INIT(NULL, 0)
  "x11.BaseCanvas",                /* tp_name */
  sizeof(BaseCanvas),              /* tp_basicsize */
  0,                               /* tp_itemsize */
  (destructor)BaseCanvas_dealloc,  /* tp_dealloc */
  0,                               /* tp_print */
  0,                               /* tp_getattr */
  0,                               /* tp_setattr */
  0,                               /* tp_reserved */
  0,                               /* tp_repr */
  0,                               /* tp_as_number */
  0,                               /* tp_as_sequence */
  0,                               /* tp_as_mapping */
  0,                               /* tp_hash  */
  0,                               /* tp_call */
  0,                               /* tp_str */
  0,                               /* tp_getattro */
  0,                               /* tp_setattro */
  0,                               /* tp_as_buffer */
  Py_TPFLAGS_DEFAULT |
  Py_TPFLAGS_BASETYPE,             /* tp_flags */
  "BaseCanvas objects",            /* tp_doc */
  0,                               /* tp_traverse */
  0,                               /* tp_clear */
  0,                               /* tp_richcompare */
  0,                               /* tp_weaklistoffset */
  0,                               /* tp_iter */
  0,                               /* tp_iternext */
  BaseCanvas_methods,              /* tp_methods */
  BaseCanvas_members,              /* tp_members */
  0,                               /* tp_getset */
  0,                               /* tp_base */
  0,                               /* tp_dict */
  0,                               /* tp_descr_get */
  0,                               /* tp_descr_set */
  0,                               /* tp_dictoffset */
  (initproc)BaseCanvas_init,       /* tp_init */
  0,                               /* tp_alloc */
  BaseCanvas_new,                  /* tp_new */
};
#endif

#endif
