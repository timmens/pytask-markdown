"""Contains test which ensure that the plugin works with pytask-parallel."""
from __future__ import annotations

import os
import sys
import textwrap
import time

import pytest
from conftest import needs_marp
from pytask import cli
from pytask import ExitCode


try:
    import pytask_parallel  # noqa: F401
except ImportError:  # pragma: no cover
    _IS_PYTASK_PARALLEL_INSTALLED = False
else:
    _IS_PYTASK_PARALLEL_INSTALLED = True


pytestmark = pytest.mark.xfail(
    not _IS_PYTASK_PARALLEL_INSTALLED, reason="Tests require pytask-parallel."
)

skip_on_mac = pytest.mark.skipif(
    sys.platform == "darwin", reason="Does not succeed on Mac."
)

xfail_on_remote = pytest.mark.xfail(
    condition=os.environ.get("CI") == "true", reason="Does not succeed on CI."
)


@pytestmark
@skip_on_mac
@xfail_on_remote
@needs_marp
@pytest.mark.end_to_end
def test_parallel_parametrization_over_source_files_w_parametrize(runner, tmp_path):
    source = """
    import pytask

    @pytask.mark.parametrize(
        "marp",
        [
            {"script": "document_1.md", "document": "document_1.html"},
            {"script": "document_2.md", "document": "document_2.html"}
        ],
    )
    def task_compile_marp_document():
        pass
    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(source))

    markdown_source = r"""
    ---
    marp: true
    ---
    ## Test
    """
    tmp_path.joinpath("document_1.md").write_text(textwrap.dedent(markdown_source))
    tmp_path.joinpath("document_2.md").write_text(textwrap.dedent(markdown_source))

    start = time.time()
    result = runner.invoke(cli, [tmp_path.as_posix()])

    assert result.exit_code == ExitCode.OK
    duration_normal = time.time() - start

    for name in ["document_1.html", "document_2.html"]:
        tmp_path.joinpath(name).unlink()

    start = time.time()
    result = runner.invoke(cli, [tmp_path.as_posix(), "-n", 2])

    assert result.exit_code == ExitCode.OK
    duration_parallel = time.time() - start

    assert duration_parallel < duration_normal


@pytestmark
@skip_on_mac
@xfail_on_remote
@needs_marp
@pytest.mark.end_to_end
def test_parallel_parametrization_over_source_files_w_loop(runner, tmp_path):
    source = """
    import pytask

    for i in range(1, 3):

        @pytask.mark.task
        @pytask.mark.marp(script=f"document_{i}.md", document=f"document_{i}.html")
        def task_compile_marp_document():
            pass
    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(source))

    markdown_source = r"""
    ---
    marp: true
    ---
    ## Test
    """
    tmp_path.joinpath("document_1.md").write_text(textwrap.dedent(markdown_source))
    tmp_path.joinpath("document_2.md").write_text(textwrap.dedent(markdown_source))

    start = time.time()
    result = runner.invoke(cli, [tmp_path.as_posix()])

    assert result.exit_code == ExitCode.OK
    duration_normal = time.time() - start

    for name in ["document_1.html", "document_2.html"]:
        tmp_path.joinpath(name).unlink()

    start = time.time()
    result = runner.invoke(cli, [tmp_path.as_posix(), "-n", 2])

    assert result.exit_code == ExitCode.OK
    duration_parallel = time.time() - start

    assert duration_parallel < duration_normal


@pytestmark
@skip_on_mac
@xfail_on_remote
@needs_marp
@pytest.mark.end_to_end
def test_parallel_parametrization_over_source_file_w_parametrize(runner, tmp_path):
    source = """
    import pytask
    from pytask_markdown import compilation_steps as cs

    @pytask.mark.parametrize(
        "marp",
        [
            {
                "script": "document.md",
                "document": "document.pdf",
                "compilation_steps": cs.marp_cli("--html"),
            },
            {
                "script": "document.md",
                "document": "document.html",
                "compilation_steps": cs.marp_cli("--html"),
            }
        ]
    )
    def task_compile_marp_document():
        pass
    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(source))

    markdown_source = r"""
    ---
    marp: true
    ---
    ## Test
    """
    tmp_path.joinpath("document.md").write_text(textwrap.dedent(markdown_source))

    start = time.time()
    result = runner.invoke(cli, [tmp_path.as_posix()])

    assert result.exit_code == ExitCode.OK
    duration_normal = time.time() - start

    for name in ["document.pdf", "document.html"]:
        tmp_path.joinpath(name).unlink()

    start = time.time()
    result = runner.invoke(cli, [tmp_path.as_posix(), "-n", 2])

    assert result.exit_code == ExitCode.OK
    duration_parallel = time.time() - start

    assert duration_parallel < duration_normal


@pytestmark
@skip_on_mac
@xfail_on_remote
@needs_marp
@pytest.mark.end_to_end
def test_parallel_parametrization_over_source_file_w_loop(runner, tmp_path):
    source = """
    import pytask
    from pytask_markdown import compilation_steps as cs

    for ending in ("pdf", "html"):

        @pytask.mark.task
        @pytask.mark.marp(
            script="document.md",
            document=f"document.{ending}",
        )
        def task_compile_marp_document():
            pass
    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(source))

    markdown_source = r"""
    ---
    marp: true
    ---
    ## Test
    """
    tmp_path.joinpath("document.md").write_text(textwrap.dedent(markdown_source))

    start = time.time()
    result = runner.invoke(cli, [tmp_path.as_posix()])

    assert result.exit_code == ExitCode.OK
    duration_normal = time.time() - start

    for name in ["document.pdf", "document.html"]:
        tmp_path.joinpath(name).unlink()

    start = time.time()
    result = runner.invoke(cli, [tmp_path.as_posix(), "-n", 2])

    assert result.exit_code == ExitCode.OK
    duration_parallel = time.time() - start

    assert duration_parallel < duration_normal
