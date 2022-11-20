from __future__ import annotations

from contextlib import ExitStack as does_not_raise  # noqa: N813

import pytest
from pytask_markdown.collect import markdown


@pytest.mark.unit
@pytest.mark.parametrize(
    "kwargs, expectation, expected",
    [
        ({}, pytest.raises(RuntimeError), None),
        (
            {"document": "document.pdf"},
            pytest.raises(RuntimeError),
            None,
        ),
        (
            {"script": "script.md"},
            pytest.raises(RuntimeError),
            None,
        ),
        (
            {"script": "script.md", "document": "document.pdf"},
            does_not_raise(),
            ("script.md", "document.pdf", None),
        ),
        (
            {
                "script": "script.md",
                "document": "document.pdf",
                "compilation_steps": "quarto",
            },
            does_not_raise(),
            ("script.md", "document.pdf", "quarto"),
        ),
        (
            {
                "script": "script.md",
                "document": "document.pdf",
                "compilation_steps": "invalid_compilation_steps",
            },
            does_not_raise(),
            ("script.md", "document.pdf", "invalid_compilation_steps"),
        ),
    ],
)
def test_marp(kwargs, expectation, expected):
    with expectation:
        result = markdown(**kwargs)
        assert result == expected
