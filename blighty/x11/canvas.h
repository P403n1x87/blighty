#ifndef CANVAS_H
#define CANVAS_H

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
  cairo_surface_t * surface;
  Display         * display;
  Drawable          win_id;

  // Signals
  Atom              wm_delete_window;

  // Attributes
  unsigned int      interval;

  // Internal attributes
  int               _running;
  int               _dispose;
  int               _destroy;
} Canvas;

#ifdef CANVAS_C
// ---- METHODS ----
static void       Canvas_dealloc  (Canvas *);
static PyObject * Canvas_new      (PyTypeObject *, PyObject *, PyObject *);
static int        Canvas_init     (Canvas *, PyObject *, PyObject *);

static PyObject * Canvas_move     (Canvas *, PyObject *, PyObject *);
static PyObject * Canvas_show     (Canvas *);
static PyObject * Canvas_get_size (Canvas *);
static PyObject * Canvas_dispose  (Canvas *);
static PyObject * Canvas_destroy  (Canvas *);


static PyMethodDef Canvas_methods[] = {
  {"move"     , (PyCFunction) Canvas_move      , METH_VARARGS | METH_KEYWORDS,
      "Move the window to new coordinates relative to the current gravity."
  },
  {"show"     , (PyCFunction) Canvas_show      , METH_NOARGS,
      "Map the canvas to screen and set it ready for drawing."
  },
  {"get_size" , (PyCFunction) Canvas_get_size  , METH_NOARGS,
      "Get the canvas size."
  },
  {"dispose"  , (PyCFunction) Canvas_dispose   , METH_NOARGS,
      "Mark the canvas as ready to be destroyed to free up resources."
  },
  {"destroy"  , (PyCFunction) Canvas_destroy   , METH_NOARGS,
      "Destroy the canvas. This method is not thread-safe. Use the dispose method instead."
  },
  {NULL}  /* Sentinel */
};


// ---- ATTRIBUTES ----
static PyMemberDef Canvas_members[] = {
  {"interval", T_INT, offsetof(Canvas, interval), 0, "refresh interval in milliseconds"},
  {NULL}  /* Sentinel */
};

// ---- OBJECT TYPE DECLARATION ----
PyTypeObject CanvasType = {
  PyVarObject_HEAD_INIT(NULL, 0)
  "canvas.Canvas",             /* tp_name */
  sizeof(Canvas),              /* tp_basicsize */
  0,                           /* tp_itemsize */
  (destructor)Canvas_dealloc,  /* tp_dealloc */
  0,                           /* tp_print */
  0,                           /* tp_getattr */
  0,                           /* tp_setattr */
  0,                           /* tp_reserved */
  0,                           /* tp_repr */
  0,                           /* tp_as_number */
  0,                           /* tp_as_sequence */
  0,                           /* tp_as_mapping */
  0,                           /* tp_hash  */
  0,                           /* tp_call */
  0,                           /* tp_str */
  0,                           /* tp_getattro */
  0,                           /* tp_setattro */
  0,                           /* tp_as_buffer */
  Py_TPFLAGS_DEFAULT |
  Py_TPFLAGS_BASETYPE,         /* tp_flags */
  "Canvas objects",            /* tp_doc */
  0,                           /* tp_traverse */
  0,                           /* tp_clear */
  0,                           /* tp_richcompare */
  0,                           /* tp_weaklistoffset */
  0,                           /* tp_iter */
  0,                           /* tp_iternext */
  Canvas_methods,              /* tp_methods */
  Canvas_members,              /* tp_members */
  0,                           /* tp_getset */
  0,                           /* tp_base */
  0,                           /* tp_dict */
  0,                           /* tp_descr_get */
  0,                           /* tp_descr_set */
  0,                           /* tp_dictoffset */
  (initproc)Canvas_init,       /* tp_init */
  0,                           /* tp_alloc */
  Canvas_new,                  /* tp_new */
};
#endif

#endif
