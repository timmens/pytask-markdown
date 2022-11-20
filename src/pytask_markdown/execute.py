"""Execute tasks."""
from __future__ import annotations

import shutil

from pytask import has_mark
from pytask import hookimpl


@hookimpl
def pytask_execute_task_setup(task):
    """Check that marp is found on the PATH if a marp task should be executed."""
    if has_mark(task, "marp"):
        if shutil.which("marp") is None:
            raise RuntimeError(
                "marp is needed to render markdown documents, but it is not found on "
                "your PATH."
            )
