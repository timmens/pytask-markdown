"""This module contains compilation steps for rendering a markdown document using Marp.

Each compilation step must have the following signature:

.. code-block::

    def compilation_step(
        path_to_md: Path, path_to_document: Path, path_to_css: Union[Path, None]
    ):
        ...

A compilation step constructor must yield a function with this signature.

"""
from __future__ import annotations

import shutil
import subprocess

from pytask_markdown.utils import to_list


def quarto(options: str | list[str] | tuple[str, ...] = ()):
    """Compilation step that calls quarto."""
    options = [str(i) for i in to_list(options)]

    _verify_options_validity(options, list_of_valid_quarto_options)

    def run_quarto(path_to_md, path_to_document, path_to_css):  # noqa: U100
        if path_to_document.suffix == ".pdf":
            raise NotImplementedError(
                "pytask-markdown does not support rendering to pdf with quarto yet. "
                "Please use the marp backend."
            )

        cmd = (
            ["quarto", "render", path_to_md.as_posix(), *options]
            + ["--no-cache"]
            + ["--output"]
            + [path_to_document.name]
        )
        subprocess.run(cmd, check=True)
        shutil.move(path_to_document.name, path_to_document.as_posix())

    return run_quarto


def marp(options: str | list[str] | tuple[str, ...] = ()):
    """Compilation step that calls marp."""
    options = [str(i) for i in to_list(options)]

    _verify_options_validity(options, list_of_valid_marp_options)

    def run_marp(path_to_md, path_to_document, path_to_css):
        cmd = ["marp", path_to_md.as_posix(), *options]
        if path_to_css is not None:
            cmd += ["--theme-set", path_to_css.as_posix()]
        cmd += ["--output", path_to_document.as_posix()]
        subprocess.run(cmd, check=True)

    return run_marp


def _verify_options_validity(options, list_of_valid_options):
    invalid = []
    for opt in options:
        valid = False
        for val_opt in list_of_valid_options:
            if val_opt in opt:
                valid = True
                break
        if not valid:
            invalid.append(opt)

    if invalid:
        msg = f"Options {invalid} are invalid. Please refer to the documentation."
        if "--theme-set" in invalid:
            msg += (
                "\nTo use a custom css or scss theme please provide the path to the "
                "pytask.mark.markdown decorator as css=/path/to/css."
            )
        raise ValueError(msg)


list_of_valid_marp_options = [
    # Basic options:
    "--config-file",
    # Converter Options:
    "--image",  # choices: "png", "jpeg"
    "--images",  # choices: "png", "jpeg"
    "--allow-local-files",
    # Template Options:
    "--template",  # choices: "bare", "bespoke"
    # PDF Options:
    "--pdf-notes",
    "--pdf-outlines",
    "--pdf-outline.pages",  # default: True
    "--pdf-outline.headings",  # default: True
    # Marp / Marpit Options:
    "--html",
    "--engine",
]

list_of_valid_quarto_options = []
