"""Entry-point for the plugin."""
from __future__ import annotations

from pluggy import PluginManager
from pytask import hookimpl
from pytask_markdown import collect
from pytask_markdown import config
from pytask_markdown import execute
from pytask_markdown import parametrize


@hookimpl
def pytask_add_hooks(pm: PluginManager) -> None:
    """Register some plugins."""
    pm.register(collect)
    pm.register(config)
    pm.register(execute)
    pm.register(parametrize)
