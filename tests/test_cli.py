import sys
from builtins import print as imprimir_original

import pytest

import plox.__main__ as cli


def interrumpir(self):
    raise KeyboardInterrupt


def test_ctrl_c_exits_with_130(monkeypatch, capsys):
    # Usar monkeypatch para reemplazar Plox.main solo durante este test.
    monkeypatch.setattr(cli.Plox, "main", interrumpir)

    # Debe transformar la interrupción en una salida.
    with pytest.raises(SystemExit) as salida:
        cli.main()

    assert salida.value.code == 130
    terminal = capsys.readouterr()
    assert terminal.out == "\n"
    assert terminal.err == ""


def ejecutar(self):
    print("Programa terminado")


def test_main_finishes_normally(monkeypatch, capsys):
    # Simulamos una ejecución que termina sin interrupciones.

    monkeypatch.setattr(cli.Plox, "main", ejecutar)

    # Si main lanzara SystemExit u otra excepción, el test fallaría acá.
    cli.main()

    terminal = capsys.readouterr()
    assert terminal.out == "Programa terminado\n"
    assert terminal.err == ""


# El manejo de Ctrl-C no debe ocultar errores de programación.
def fallar(self):
    raise RuntimeError("Error de prueba")


def test_other_errors_are_not_hidden(monkeypatch):
    monkeypatch.setattr(cli.Plox, "main", fallar)

    with pytest.raises(RuntimeError, match="Error de prueba"):
        cli.main()


def interrumpir_al_imprimir(*args, **kwargs):
    imprimir_original(*args, **kwargs)
    # Simulamos Ctrl-C después del primer "hello" del bucle.
    if args == ("hello",):
        raise KeyboardInterrupt


def comprobar_interrupcion_de_archivo(monkeypatch, tmp_path, capsys, opciones):
    archivo = tmp_path / "while.lox"
    archivo.write_text('while (true) { print "hello"; }\n', encoding="utf-8")

    monkeypatch.setattr(sys, "argv", ["plox", *opciones, str(archivo)])
    monkeypatch.setattr("builtins.print", interrumpir_al_imprimir)

    # Usamos el scanner, parser, resolver e interprete.
    with pytest.raises(SystemExit) as salida:
        cli.main()

    assert salida.value.code == 130
    terminal = capsys.readouterr()
    assert terminal.out.splitlines().count("hello") == 1
    assert "Traceback" not in terminal.out
    assert "KeyboardInterrupt" not in terminal.out
    assert "Runtime Error" not in terminal.out
    assert terminal.err == ""


def test_ctrl_c_in_while_from_issue(monkeypatch, tmp_path, capsys):
    comprobar_interrupcion_de_archivo(monkeypatch, tmp_path, capsys, [])


def test_ctrl_c_in_while_with_debug(monkeypatch, tmp_path, capsys):
    # Incluso con --debug, Ctrl-C no debe mostrar un traceback.
    comprobar_interrupcion_de_archivo(monkeypatch, tmp_path, capsys, ["--debug"])


def test_ctrl_c_in_while_line_by_line(monkeypatch, tmp_path, capsys):
    comprobar_interrupcion_de_archivo(
        monkeypatch, tmp_path, capsys, ["--line-by-line"]
    )
