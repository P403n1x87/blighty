#include <Python.h>
#include "pycairo.h"

#include "atelier.h"

extern PyTypeObject CanvasType;

// TODO: Expose event loop starter method

static PyMethodDef x11methods[] = {
  {
    "start_event_loop",
    Atelier_start_event_loop,
    METH_NOARGS,
    "Starts the main event loop for all the Canvas objects."
  },
  {NULL, NULL, 0, NULL}
};

static PyModuleDef x11module = {
  PyModuleDef_HEAD_INIT,
  "x11", // TODO: Fix
  "X11 support module for blighty.",
  -1,
  x11methods, // m_methods
  NULL, NULL, NULL, NULL
};

PyMODINIT_FUNC
PyInit_x11(void)
{
  PyObject* m;

  if (PyType_Ready(&CanvasType) < 0)
    return NULL;

  m = PyModule_Create(&x11module);
  if (m == NULL)
    return NULL;

  if (import_cairo() < 0)
    return NULL;

  Py_INCREF(&CanvasType);
  PyModule_AddObject(m, "Canvas", (PyObject *)&CanvasType);

  // Initialise Atelier
  Atelier_init();
  return m;
}
