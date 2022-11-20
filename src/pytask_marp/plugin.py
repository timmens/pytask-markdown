"""Entry-point for the plugin."""
from __future__ import annotations

from pytask import hookimpl
from pytask_marp import collect
from pytask_marp import config
from pytask_marp import execute
from pytask_marp import parametrize


@hookimpl
def pytask_add_hooks(pm):
    """Register some plugins."""
    pm.register(collect)
    pm.register(config)
    pm.register(execute)
    pm.register(parametrize)
