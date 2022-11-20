"""This module contains compilation steps for rendering a markdown document using Marp.

Each compilation step must have the following signature:

.. code-block::

    def compilation_step(path_to_md: Path, path_to_document: Path):
        ...

A compilation step constructor must yield a function with this signature.

"""
from __future__ import annotations

import subprocess

from pytask_marp.utils import to_list


def marp_cli(options=()):
    """Compilation step that calls marp."""
    options = [str(i) for i in to_list(options)]

    def run_marp(path_to_md, path_to_document):
        cmd = (
            ["marp", path_to_md.as_posix(), *options]
            + ["--output"]
            + [path_to_document.as_posix()]
        )
        subprocess.run(cmd, check=True)

    return run_marp


_valid_options = [
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
    "--theme-set",
]
