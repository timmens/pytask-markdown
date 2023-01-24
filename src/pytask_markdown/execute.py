"""Execute tasks."""
from __future__ import annotations

import shutil

from pytask import has_mark
from pytask import hookimpl
from pytask import Task


download_link = {
    "marp": "https://github.com/marp-team/marp-cli",
    "quarto": "https://quarto.org/",
}


@hookimpl
def pytask_execute_task_setup(task: Task) -> None:
    """Check that renderer is found in PATH if a markdown task shall be executed."""
    if has_mark(task, "markdown"):
        renderer = task.attributes["renderer"]
        if shutil.which(renderer) is None:
            raise RuntimeError(
                f"{renderer} is needed to render markdown documents, but it is not "
                f"found on your PATH. Install from {download_link[renderer]}."
            )
