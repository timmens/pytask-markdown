from __future__ import annotations

import textwrap

import pytest
from conftest import needs_marp
from pytask import ExitCode
from pytask import main


@needs_marp
@pytest.mark.end_to_end
def test_parametrized_rendering_of_markdown_documents_w_parametrize(tmp_path):
    task_source = """
    import pytask

    @pytask.mark.parametrize("marp", [
        {"script": "document_1.md", "document": "document_1.pdf"},
        {"script": "document_2.md", "document": "document_2.pdf"},
    ])
    def task_compile_marp_document():
        pass
    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))

    for name, content in [
        ("document_1.md", "Like a worn out recording"),
        ("document_2.md", "Of a favorite song"),
    ]:
        markdown_source = rf"""
        ---
        marp: true
        ---
        ## Test
        {content}
        """
        tmp_path.joinpath(name).write_text(textwrap.dedent(markdown_source))

    session = main({"paths": tmp_path})

    assert session.exit_code == ExitCode.OK
    assert tmp_path.joinpath("document_1.pdf").exists()
    assert tmp_path.joinpath("document_2.pdf").exists()


@needs_marp
@pytest.mark.end_to_end
def test_parametrized_compilation_of_marp_documents_w_loop(tmp_path):
    source = """
    import pytask

    for i in range(1, 3):

        @pytask.mark.task
        @pytask.mark.marp(script=f"document_{i}.md", document=f"document_{i}.pdf")
        def task_compile_marp_document():
            pass
    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(source))

    for name, content in [
        ("document_1.md", "Like a worn out recording"),
        ("document_2.md", "Of a favorite song"),
    ]:
        markdown_source = rf"""
        ---
        marp: true
        ---
        ## Test
        {content}
        """
        tmp_path.joinpath(name).write_text(textwrap.dedent(markdown_source))

    session = main({"paths": tmp_path})

    assert session.exit_code == ExitCode.OK
    assert tmp_path.joinpath("document_1.pdf").exists()
    assert tmp_path.joinpath("document_2.pdf").exists()


@needs_marp
@pytest.mark.end_to_end
def test_parametrizing_marp_options_w_parametrize(tmp_path):
    task_source = """
    import pytask
    from pytask_marp import compilation_steps as cs

    @pytask.mark.parametrize(
        "marp",
        [
            {
                "script": "document.md",
                "document": "document.pdf",
                "compilation_steps": cs.marp_cli(
                    ("--html")
                ),
            },
            {
                "script": "document.md",
                "document": "document.html",
                "compilation_steps": cs.marp_cli(
                    ("--html")
                ),
            }
        ]
    )
    def task_compile_marp_document():
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

    session = main({"paths": tmp_path})

    assert session.exit_code == ExitCode.OK
    assert tmp_path.joinpath("document.pdf").exists()
    assert tmp_path.joinpath("document.html").exists()


@needs_marp
@pytest.mark.end_to_end
def test_parametrizing_marp_options_w_loop(tmp_path):
    for theme in ("gaia", "uncover"):
        scss_source = rf"""
        /* @theme custom */
        @import '{theme}';
        """
        tmp_path.joinpath(f"{theme}.scss").write_text(textwrap.dedent(scss_source))
    source = """
    import pytask
    from pytask_marp import compilation_steps as cs

    for theme in ("gaia", "uncover"):

        for format in ("pdf", "html"):

            @pytask.mark.task
            @pytask.mark.marp(
                script="document.md",
                document=f"document_{theme}.{format}",
                compilation_steps=cs.marp_cli(f"--theme-set {theme}.scss")
            )
            def render_markdown_document():
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

    session = main({"paths": tmp_path})

    assert session.exit_code == ExitCode.OK
    assert tmp_path.joinpath("document_gaia.pdf").exists()
    assert tmp_path.joinpath("document_uncover.pdf").exists()
    assert tmp_path.joinpath("document_gaia.html").exists()
    assert tmp_path.joinpath("document_uncover.html").exists()
