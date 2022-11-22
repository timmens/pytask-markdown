from __future__ import annotations

import textwrap
from pathlib import Path

import pytest
from conftest import needs_marp
from conftest import needs_quarto
from conftest import TEST_RESOURCES
from pytask import cli
from pytask import ExitCode
from pytask import main
from pytask import Mark
from pytask import Task
from pytask_markdown.execute import pytask_execute_task_setup


@pytest.fixture()
def default_source():
    marp = r"""
    ---
    marp: true
    ---
    ## Test
    Text
    """
    quarto = r"""
    ---
    title: Test
    ---
    Text
    """
    return {"marp": marp, "quarto": quarto}


@pytest.mark.unit
def test_pytask_execute_task_setup(monkeypatch):
    """Make sure that the task setup raises errors."""
    monkeypatch.setattr(
        "pytask_markdown.execute.shutil.which", lambda x: None  # noqa: U100
    )
    task = Task(
        base_name="example",
        path=Path(),
        function=None,
        markers=[Mark("markdown", (), {})],
    )
    with pytest.raises(RuntimeError, match="marp is needed"):
        pytask_execute_task_setup(task)


@pytest.mark.end_to_end
def test_render_markdown_document_raise_error(runner, tmp_path, default_source):
    """Test that wrong syntax raises error."""
    task_source = """
    import pytask

    @pytask.mark.markdown
    @pytask.mark.depends_on("document.md")
    @pytask.mark.produces("document.html")
    def task_render_document():
        pass

    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))
    tmp_path.joinpath("document.md").write_text(textwrap.dedent(default_source["marp"]))

    result = runner.invoke(cli, [tmp_path.as_posix()])

    assert result.exit_code == ExitCode.COLLECTION_FAILED
    assert "Argument script and document have to specified." in result.output


@needs_marp
@pytest.mark.end_to_end
def test_render_markdown_document_default(runner, tmp_path, default_source):
    """Test simple rendering to html document with default backend."""
    task_source = """
    import pytask

    @pytask.mark.markdown(script="document.md", document="document.html")
    def task_render_document():
        pass

    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))
    tmp_path.joinpath("document.md").write_text(textwrap.dedent(default_source["marp"]))

    result = runner.invoke(cli, [tmp_path.as_posix()])
    assert result.exit_code == ExitCode.OK


@needs_marp
@needs_quarto
@pytest.mark.end_to_end
@pytest.mark.parametrize("backend", ["marp", "quarto"])
def test_render_markdown_document(runner, tmp_path, default_source, backend):
    """Test simple rendering to html document."""
    task_source = f"""
    import pytask

    @pytask.mark.markdown(
        script="document.md",
        document="document.html",
        compilation_steps="{backend}",
    )
    def task_render_document():
        pass

    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))
    tmp_path.joinpath("document.md").write_text(
        textwrap.dedent(default_source[backend])
    )

    result = runner.invoke(cli, [tmp_path.as_posix()])
    assert result.exit_code == ExitCode.OK


@needs_marp
@pytest.mark.skip
@pytest.mark.end_to_end
def test_render_marp_document_w_relative(runner, tmp_path):
    """Test simple compilation."""
    task_source = f"""
    import pytask

    @pytask.mark.markdown(
        script="document.md",
        document="{tmp_path.joinpath("bld", "document.html").as_posix()}"
    )
    def task_render_document():
        pass

    """
    tmp_path.joinpath("bld").mkdir()
    tmp_path.joinpath("src").mkdir()
    tmp_path.joinpath("src", "task_dummy.py").write_text(textwrap.dedent(task_source))

    markdown_source = r"""
    ---
    marp: true
    ---
    ## Test
    """
    tmp_path.joinpath("document.md").write_text(textwrap.dedent(markdown_source))

    result = runner.invoke(cli, [tmp_path.as_posix()])
    assert result.exit_code == ExitCode.OK


@needs_marp
@needs_quarto
@pytest.mark.end_to_end
@pytest.mark.parametrize("backend", ["marp", "quarto"])
def test_compile_markdown_document_to_different_name(
    runner, tmp_path, default_source, backend
):
    """Render a markdown document where source and output name differ."""
    task_source = f"""
    import pytask

    @pytask.mark.markdown(
        script="in.md",
        document="out.html",
        compilation_steps="{backend}"
    )
    def task_render_document():
        pass

    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))
    tmp_path.joinpath("in.md").write_text(textwrap.dedent(default_source[backend]))

    result = runner.invoke(cli, [tmp_path.as_posix()])
    assert result.exit_code == ExitCode.OK


@needs_marp
@pytest.mark.end_to_end
def test_raise_error_if_marp_is_not_found(tmp_path, monkeypatch, default_source):
    task_source = """
    import pytask

    @pytask.mark.markdown(script="document.md", document="document.html")
    def task_render_document():
        pass

    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))
    tmp_path.joinpath("document.md").write_text(textwrap.dedent(default_source["marp"]))

    # Hide marp if available.
    monkeypatch.setattr(
        "pytask_markdown.execute.shutil.which", lambda x: None  # noqa: U100
    )

    session = main({"paths": tmp_path})

    assert session.exit_code == ExitCode.FAILED
    assert isinstance(session.execution_reports[0].exc_info[1], RuntimeError)


@needs_marp
@needs_quarto
@pytest.mark.end_to_end
@pytest.mark.parametrize("backend", ["marp", "quarto"])
def test_render_marp_document_w_two_dependencies(
    runner, tmp_path, default_source, backend
):
    task_source = f"""
    import pytask

    @pytask.mark.markdown(
        script="document.md",
        document="document.html",
        compilation_steps="{backend}"
    )
    @pytask.mark.depends_on("in.txt")
    def task_render_document():
        pass

    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))
    tmp_path.joinpath("document.md").write_text(
        textwrap.dedent(default_source[backend])
    )
    tmp_path.joinpath("in.txt").touch()

    result = runner.invoke(cli, [tmp_path.as_posix()])
    assert result.exit_code == ExitCode.OK
    assert tmp_path.joinpath("document.html").exists()


@needs_marp
@needs_quarto
@pytest.mark.end_to_end
@pytest.mark.parametrize("backend", ["marp", "quarto"])
def test_fail_because_script_is_not_markdown(tmp_path, default_source, backend):
    task_source = f"""
    import pytask

    @pytask.mark.markdown(
        script="document.mdt",
        document="document.html",
        compilation_steps="{backend}"
    )
    @pytask.mark.depends_on("in.txt")
    def task_render_document():
        pass

    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))
    tmp_path.joinpath("document.mdt").write_text(
        textwrap.dedent(default_source[backend])
    )
    tmp_path.joinpath("in.txt").touch()

    session = main({"paths": tmp_path})
    assert session.exit_code == ExitCode.COLLECTION_FAILED
    assert isinstance(session.collection_reports[0].exc_info[1], ValueError)


@needs_marp
@needs_quarto
@pytest.mark.end_to_end
@pytest.mark.parametrize("backend", ["marp", "quarto"])
def test_render_document_to_out_if_document_has_relative_resources(
    tmp_path, default_source, backend
):
    """Test that motivates the ``"--cd"`` flag.

    If you have a document which includes other resources via relative paths and you
    compile the document to a different output folder, marp will not find the relative
    resources. Thus, use the ``"--cd"`` flag to enter the source directory before the
    compilation.

    """
    tmp_path.joinpath("sub", "resources").mkdir(parents=True)

    task_source = f"""
    import pytask

    @pytask.mark.markdown(
        script="document.md",
        document="out/document.html",
        compilation_steps="{backend}"
    )
    @pytask.mark.depends_on("resources/content.md")
    def task_render_document():
        pass

    """
    tmp_path.joinpath("sub", "task_dummy.py").write_text(textwrap.dedent(task_source))
    tmp_path.joinpath("sub", "document.md").write_text(
        textwrap.dedent(default_source[backend])
    )

    resources = r"""
    In Ottakring, in Ottakring, wo das Bitter so viel suesser schmeckt als irgendwo in
    Wien.
    """
    tmp_path.joinpath("sub", "resources", "content.md").write_text(resources)

    session = main({"paths": tmp_path})
    assert session.exit_code == ExitCode.OK
    assert len(session.tasks) == 1


@pytest.mark.skip
@needs_marp
@pytest.mark.end_to_end
def test_render_document_w_wrong_flag(tmp_path):
    """Test that wrong flags raise errors."""
    tmp_path.joinpath("sub").mkdir(parents=True)

    task_source = """
    import pytask
    from pytask_markdown import compilation_steps

    @pytask.mark.markdown(
        script="document.md",
        document="out/document.html",
        compilation_steps=compilation_steps.marp_cli("--wrong-flag"),
    )
    def task_render_document():
        pass

    """
    tmp_path.joinpath("sub", "task_dummy.py").write_text(textwrap.dedent(task_source))

    markdown_source = r"""
    ---
    marp: true
    ---
    ## Test
    """
    tmp_path.joinpath("sub", "document.md").write_text(textwrap.dedent(markdown_source))

    session = main({"paths": tmp_path})
    assert session.exit_code == ExitCode.FAILED
    assert len(session.tasks) == 1
    assert isinstance(session.execution_reports[0].exc_info[1], RuntimeError)


@needs_marp
@pytest.mark.end_to_end
def test_render_document_w_image(runner, tmp_path):
    task_source = f"""
    import pytask
    import shutil

    @pytask.mark.produces("image.png")
    def task_create_image():
        shutil.copy(
            "{TEST_RESOURCES.joinpath("image.png").as_posix()}",
            "{tmp_path.joinpath("image.png").as_posix()}"
        )

    @pytask.mark.markdown(script="document.md", document="document.html")
    def task_render_document():
        pass

    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))

    markdown_source = r"""
    ---
    marp: true
    ---
    ## Test
    """
    tmp_path.joinpath("document.md").write_text(textwrap.dedent(markdown_source))

    result = runner.invoke(cli, [tmp_path.as_posix()])
    assert result.exit_code == ExitCode.OK


@needs_marp
@pytest.mark.end_to_end
def test_render_marp_document_w_multiple_marks(runner, tmp_path):
    """Test simple compilation."""
    task_source = """
    import pytask

    @pytask.mark.markdown(script="document.mdt")
    @pytask.mark.markdown(script="document.md", document="document.html")
    def task_render_document():
        pass
    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))

    markdown_source = r"""
    ---
    marp: true
    ---
    ## Test
    """
    tmp_path.joinpath("document.md").write_text(textwrap.dedent(markdown_source))

    result = runner.invoke(cli, [tmp_path.as_posix()])
    assert result.exit_code == ExitCode.COLLECTION_FAILED
    assert "has multiple @pytask.mark.markdown" in result.output


@needs_marp
@pytest.mark.end_to_end
def test_render_marp_document_with_wrong_extension(runner, tmp_path):
    """Test simple compilation."""
    task_source = """
    import pytask

    @pytask.mark.markdown(script="document.md", document="document.file")
    def task_render_document():
        pass
    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))

    markdown_source = r"""
    ---
    marp: true
    ---
    ## Test
    """
    tmp_path.joinpath("document.md").write_text(textwrap.dedent(markdown_source))

    result = runner.invoke(cli, [tmp_path.as_posix()])
    assert result.exit_code == ExitCode.COLLECTION_FAILED
    assert "The 'document' keyword of the" in result.output


@needs_marp
@pytest.mark.end_to_end
@pytest.mark.parametrize(
    "step, message",
    [
        ("'unknown'", "Compilation step 'unknown' is unknown."),
        (1, "Compilation step 1 is not a valid step."),
    ],
)
def test_render_marp_document_w_unknown_compilation_step(
    runner, tmp_path, step, message
):
    """Test simple compilation."""
    task_source = f"""
    import pytask

    @pytask.mark.markdown(
        script="document.md",
        document="document.html",
        compilation_steps={step},
    )
    def task_render_document():
        pass
    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))

    markdown_source = r"""
    \documentclass{report}
    \begin{document}
    I was tired of my lady
    \end{document}
    """
    tmp_path.joinpath("document.md").write_text(textwrap.dedent(markdown_source))

    result = runner.invoke(cli, [tmp_path.as_posix()])
    assert result.exit_code == ExitCode.COLLECTION_FAILED
    assert message in result.output


@needs_marp
@pytest.mark.end_to_end
def test_render_marp_document_with_task_decorator(runner, tmp_path):
    """Test simple compilation."""
    task_source = """
    import pytask

    @pytask.mark.markdown(script="document.md", document="document.html")
    @pytask.mark.task
    def render_document():
        pass
    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))

    markdown_source = r"""
    \documentclass{report}
    \begin{document}
    I was tired of my lady
    \end{document}
    """
    tmp_path.joinpath("document.md").write_text(textwrap.dedent(markdown_source))

    result = runner.invoke(cli, [tmp_path.as_posix()])
    assert result.exit_code == ExitCode.OK
