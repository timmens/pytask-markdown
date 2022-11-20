"""Parametrize tasks."""
from __future__ import annotations

import pytask
from pytask import hookimpl


@hookimpl
def pytask_parametrize_kwarg_to_marker(obj, kwargs):
    """Register kwargs as marp marker."""
    if callable(obj):
        if "marp" in kwargs:
            pytask.mark.marp(**kwargs.pop("marp"))(obj)
