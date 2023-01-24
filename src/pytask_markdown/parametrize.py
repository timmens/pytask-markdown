"""Parametrize tasks."""
from __future__ import annotations

from typing import Any

import pytask
from pytask import hookimpl


@hookimpl
def pytask_parametrize_kwarg_to_marker(obj: Any, kwargs: dict[str, Any]) -> None:
    """Register kwargs as markdown marker."""
    if callable(obj) and "markdown" in kwargs:  # noqa: PLR2004
        pytask.mark.markdown(**kwargs.pop("markdown"))(obj)
