import os
from pathlib import Path
import subprocess
import sys

import pytest

from plox.__main__ import Plox


ROOT = Path(__file__).resolve().parents[1]
ERROR = "Resolve Error: No se puede usar return fuera de una función.\n"


def run_file(tmp_path, source):
    program = tmp_path / "program.lox"
    program.write_text(source)
    environment = os.environ.copy()
    environment["NO_COLOR"] = "1"
    return subprocess.run(
        [sys.executable, "-B", "-m", "plox", str(program)],
        cwd=ROOT,
        env=environment,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        timeout=10,
    )


@pytest.mark.parametrize("statement", ["return 1;", "if (false) { return; }"])
def test_cli_rejects_global_return_before_executing_the_file(tmp_path, statement):
    result = run_file(tmp_path, f'print "no debe ejecutarse"; {statement}')
    assert result.stdout == ERROR
    assert result.stderr == ""


def test_cli_accepts_returns_in_nested_functions(tmp_path):
    result = run_file(
        tmp_path,
        """
        fun outer() {
            fun inner() { return 2; }
            return inner() + 1;
        }
        print outer();
        """,
    )
    assert result.returncode == 0
    assert result.stdout == "3\n"
    assert result.stderr == ""


def test_repl_pipeline_preserves_globals_and_continues_after_invalid_return(
    capsys, monkeypatch
):
    monkeypatch.setenv("NO_COLOR", "1")
    app = Plox()
    app.run("var x=7;")
    app.run("x=99; { return 1; }")
    captured = capsys.readouterr()
    assert captured.out == ERROR
    assert captured.err == ""

    app.run("fun f(){return x;} print f();")
    captured = capsys.readouterr()
    assert captured.out == "7\n"
    assert captured.err == ""
