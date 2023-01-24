"""Configure pytask."""
from __future__ import annotations

from typing import Any

from pytask import hookimpl


DEFAULT_RENDERER = "marp"


@hookimpl
def pytask_parse_config(config: dict[str, Any]) -> None:
    """Register the markdown marker in the configuration."""
    config["markers"]["markdown"] = "Tasks which render markdown documents."
    if "markdown_renderer" not in config:
        config["markdown_renderer"] = DEFAULT_RENDERER
    if "infer_markdown_dependencies" not in config:
        config["infer_markdown_dependencies"] = False
