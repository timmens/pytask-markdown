"""Collect tasks."""
from __future__ import annotations

import functools
import warnings
from pathlib import Path
from subprocess import CalledProcessError
from types import FunctionType
from typing import Any
from typing import Callable
from typing import Sequence

from pytask import depends_on
from pytask import FilePathNode
from pytask import has_mark
from pytask import hookimpl
from pytask import parse_nodes
from pytask import produces
from pytask import remove_marks
from pytask import Task
from pytask_markdown import compilation_steps as cs
from pytask_markdown.utils import to_list


_ERROR_MSG = """The standard depends_on/produces syntax is not supported for \
@pytask.mark.marp. Please change the syntax from
    @pytask.mark.marp("--some-option")
    @pytask.mark.depends_on({"source": "source.md")
    @pytask.mark.produces("document.pdf")
    def task_marp():
        ...
to
    from pytask_markdown import compilation_steps as cs
    @pytask.mark.marp(
        script="source.md",
        document="document.pdf",
        compilation_steps=cs.marp_cli(options="--some-options"),
    )
    def task_marp():
        ...
"""


def marp(
    *,
    script: str | Path = None,
    document: str | Path = None,
    compilation_steps: str
    | Callable[..., Any]
    | Sequence[str | Callable[..., Any]] = None,
) -> tuple[str | Path | None, list[Callable[..., Any]]]:
    """Specify command line options for marp.

    Parameters
    ----------
    script
        ...
    document
        ...
    compilation_steps
        Compilation steps to compile the document.

    """
    if script is None or document is None:
        raise RuntimeError(_ERROR_MSG)
    return script, document, compilation_steps


def compile_marp_document(compilation_steps, path_to_md, path_to_document):
    """Replaces the dummy function provided by the user."""
    for step in compilation_steps:
        try:
            step(path_to_md=path_to_md, path_to_document=path_to_document)
        except CalledProcessError as e:
            raise RuntimeError(f"Compilation step {step.__name__} failed.") from e


@hookimpl
def pytask_collect_task(session, path, name, obj):
    """Perform some checks."""
    __tracebackhide__ = True

    if (
        (name.startswith("task_") or has_mark(obj, "task"))
        and callable(obj)
        and has_mark(obj, "marp")
    ):
        obj, marks = remove_marks(obj, "marp")

        if len(marks) > 1:
            raise ValueError(
                f"Task {name!r} has multiple @pytask.mark.marp marks, but only one is "
                "allowed."
            )
        marp_mark = marks[0]
        script, document, compilation_steps = marp(**marp_mark.kwargs)

        parsed_compilation_steps = _parse_compilation_steps(compilation_steps)

        obj.pytask_meta.markers.append(marp_mark)

        dependencies = parse_nodes(session, path, name, obj, depends_on)
        products = parse_nodes(session, path, name, obj, produces)

        markers = obj.pytask_meta.markers if hasattr(obj, "pytask_meta") else []
        kwargs = obj.pytask_meta.kwargs if hasattr(obj, "pytask_meta") else {}

        task = Task(
            base_name=name,
            path=path,
            function=_copy_func(compile_marp_document),
            depends_on=dependencies,
            produces=products,
            markers=markers,
            kwargs=kwargs,
        )

        script_node = session.hook.pytask_collect_node(
            session=session, path=path, node=script
        )
        document_node = session.hook.pytask_collect_node(
            session=session, path=path, node=document
        )

        if not (
            isinstance(script_node, FilePathNode) and script_node.value.suffix == ".md"
        ):
            raise ValueError(
                "The 'script' keyword of the @pytask.mark.marp decorator must point to "
                "a markdown file with the .md suffix."
            )

        if not (
            isinstance(document_node, FilePathNode)
            and document_node.value.suffix in [".pdf", ".html", ".png"]
        ):
            raise ValueError(
                "The 'document' keyword of the @pytask.mark.marp decorator must point "
                "to a .pdf, .html or .png file."
            )

        if isinstance(task.depends_on, dict):
            task.depends_on["__script"] = script_node
        else:
            task.depends_on = {0: task.depends_on, "__script": script_node}

        if isinstance(task.produces, dict):
            task.produces["__document"] = document_node
        else:
            task.produces = {0: task.produces, "__document": document_node}

        task.function = functools.partial(
            task.function,
            compilation_steps=parsed_compilation_steps,
            path_to_md=script_node.path,
            path_to_document=document_node.path,
        )

        if session.config["infer_marp_dependencies"]:
            warnings.warn(
                "Inferring of marp dependencies is not implemented yet. "
                "Will be ignored."
            )
            task = _add_marp_dependencies_retroactively(task, session)

        return task


def _add_marp_dependencies_retroactively(task, session):  # noqa: U100
    return task


def _copy_func(func: FunctionType) -> FunctionType:
    """Create a copy of a function.

    Based on https://stackoverflow.com/a/13503277/7523785.

    Example
    -------
    >>> def _func(): pass
    >>> copied_func = _copy_func(_func)
    >>> _func is copied_func
    False

    """
    new_func = FunctionType(
        func.__code__,
        func.__globals__,
        name=func.__name__,
        argdefs=func.__defaults__,
        closure=func.__closure__,
    )
    new_func = functools.update_wrapper(new_func, func)
    new_func.__kwdefaults__ = func.__kwdefaults__
    return new_func


def _parse_compilation_steps(compilation_steps):
    """Parse compilation steps."""
    __tracebackhide__ = True

    compilation_steps = ["marp_cli"] if compilation_steps is None else compilation_steps

    parsed_compilation_steps = []
    for step in to_list(compilation_steps):
        if isinstance(step, str):
            try:
                parsed_step = getattr(cs, step)
            except AttributeError:
                raise ValueError(f"Compilation step {step!r} is unknown.")
            parsed_compilation_steps.append(parsed_step())
        elif callable(step):
            parsed_compilation_steps.append(step)
        else:
            raise ValueError(f"Compilation step {step!r} is not a valid step.")

    return parsed_compilation_steps
