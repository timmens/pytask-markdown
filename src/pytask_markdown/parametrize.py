"""Parametrize tasks."""
from __future__ import annotations

import pytask
from pytask import hookimpl


@hookimpl
def pytask_parametrize_kwarg_to_marker(obj, kwargs):
    """Register kwargs as markdown marker."""
    if callable(obj):
        if "markdown" in kwargs:
            pytask.mark.markdown(**kwargs.pop("markdown"))(obj)
