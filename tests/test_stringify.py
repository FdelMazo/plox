from plox.__main__ import Plox
from plox.Interpreter import Interpreter


def test_stringify_basic_values():
    interpreter = Interpreter()
    casos = [
        (None, "nil"),
        (True, "true"),
        (False, "false"),
        (0.0, "0"),
        (2.0, "2"),
        (-2.0, "-2"),
        (2.5, "2.5"),
        (2, "2"),
        ("hola", "hola"),
        ("", ""),
        ("True None 2.0", "True None 2.0"),
    ]
    for valor, esperado in casos:
        assert interpreter.stringify(valor) == esperado


def test_print_uses_lox_values(capsys):
    plox = Plox()
    plox.in_repl = False
    plox.run('''
        print nil;
        print true;
        print false;
        print 0;
        print -2;
        print 2.5;
        print "hola";
        print "";
        var numero = 1 + 1;
        print numero;
        print 1 < 2;
    ''')
    terminal = capsys.readouterr()
    assert terminal.out == "nil\ntrue\nfalse\n0\n-2\n2.5\nhola\n\n2\ntrue\n"
    assert terminal.err == ""


def test_repl_results_use_lox_values(capsys):
    # run() usa in_repl=True por defecto, sin necesidad de abrir el prompt.
    plox = Plox()
    casos = [("true;", "true"), ("false;", "false"), ("1 + 1;", "2"),
             ("2.5;", "2.5"), ('"hola";', "hola")]
    for codigo, esperado in casos:
        plox.run(codigo)
        terminal = capsys.readouterr()
        assert terminal.out == esperado + "\n", codigo
        assert terminal.err == ""


def test_errors_use_lox_values(capsys, monkeypatch):
    monkeypatch.setenv("NO_COLOR", "1")
    plox = Plox()
    casos = [
        ("-true;", "Operand of - must be a number, got: `-true`"),
        ("nil();", "Cannot call non-callable object: `nil`"),
        ("true + nil;", "Operands of + must be either numbers or strings, got: `true + nil`"),
    ]
    for codigo, mensaje in casos:
        plox.run(codigo)
        terminal = capsys.readouterr()
        assert terminal.out == "Runtime Error: " + mensaje + "\n", codigo
        assert terminal.err == ""
