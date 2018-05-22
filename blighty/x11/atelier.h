#ifndef ATELIER_H
#define ATELIER_H

#include "canvas.h"

void
Atelier_init(void);

void
Atelier_add_canvas(Canvas * canvas);

int
Atelier_remove_canvas(Canvas * canvas);


/******************************************************************************
 ** EVENT LOOP
 ******************************************************************************/

PyObject *
Atelier_start_event_loop(PyObject *, PyObject *);

void
Atelier_stop_event_loop(void);

int
Atelier_is_running(void);

#endif
