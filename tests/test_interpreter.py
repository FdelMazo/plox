import pytest
from plox.Expr import BinaryExpr, GroupingExpr, LiteralExpr, UnaryExpr
from plox.Interpreter import Interpreter
from plox.Scanner import Scanner
from plox.Parser import Parser
from plox.Token import TokenType


def test_hello_world():
    tokens = Scanner("2+2").scan()
    expr = Parser(tokens).expression()
    value = Interpreter().evaluate(expr)
    assert value == 4.0


def test_calc():
    tokens = Scanner("1 + 2 * 3 - 4").scan()
    expr = Parser(tokens).expression()
    value = Interpreter().evaluate(expr)
    assert value == 3

    tokens = Scanner("6 / 3 - 1").scan()
    expr = Parser(tokens).expression()
    value = Interpreter().evaluate(expr)
    assert value == 1


def test_various_expressions():
    tests = [
        ('"aaa"', "aaa"),
        ("123", 123.0),
        ('"a" + "b"', "ab"),
        ("2 + 2", 4.0),
        ("4 - 2", 2.0),
        ("5 * 5", 25.0),
        ("3 > 2", True),
        ("3 >= 3", True),
        ("3 == 3", True),
        ('"aa" == "aa"', True),
        ("3 > 4", False),
        ("3 >= 4", False),
        ("3 == 4", False),
        ('"ab" == "aa"', False),
        ("42", 42),
        ("-42", -42),
        ("-(--1)", -1),
        ("((((0))))", 0),
        ("0 + 1", 1),
        ("4 - 2", 2),
        ("1.5 * 2", 3),
        ("8 / 2", 4),
        ("1 + 2 * 3 - 4 + 2", 5),
        ("3 * (3 - 1)", 6),
        ("((1 + 2) * (3 + 4)) / 3", 7),
        ("1 * 0", 0),
        ("5 % 2", 1),
        ("5 % 5", 0),
        ("0 % 2", 0),
        ("2 ** 3", 8),
        ("0 ** 2", 0),
        ("2 ** 0", 1),
        ("1 + 2 ** 3", 9),
        ("2 ** 2 ** 3", 256),
    ]

    for expr, expected in tests:
        tokens = Scanner(expr).scan()
        expr = Parser(tokens).expression()
        value = Interpreter().evaluate(expr)
        assert value == expected


def test_errors():
    tokens = Scanner('"aaa" + 5').scan()
    expr = Parser(tokens).expression()
    with pytest.raises(RuntimeError) as excinfo:
        Interpreter().evaluate(expr)

    assert "Operands of + must be either numbers or strings" in str(excinfo.value)

    tokens = Scanner('-"aaa"').scan()
    expr = Parser(tokens).expression()
    with pytest.raises(RuntimeError) as excinfo:
        Interpreter().evaluate(expr)

    assert "Operand of - must be a number" in str(excinfo.value)

    tokens = Scanner('-"aaa"').scan()
    expr = Parser(tokens).expression()
    with pytest.raises(RuntimeError) as excinfo:
        Interpreter().evaluate(expr)

    tokens = Scanner('"aaa" - "bbb"').scan()
    expr = Parser(tokens).expression()
    with pytest.raises(RuntimeError) as excinfo:
        Interpreter().evaluate(expr)

    assert "Operands of - must be numbers" in str(excinfo.value)

    tokens = Scanner("5 / 0").scan()
    expr = Parser(tokens).expression()
    with pytest.raises(RuntimeError) as excinfo:
        Interpreter().evaluate(expr)

    assert "Division by 0" in str(excinfo.value)

    tokens = Scanner("5 % 0").scan()
    expr = Parser(tokens).expression()
    with pytest.raises(RuntimeError) as excinfo:
        Interpreter().evaluate(expr)

    assert "Modulo by 0" in str(excinfo.value)


def test_logic():
    tests = [
        ("true and true", True),
        ("true and false", False),
        ("false and true", False),
        ("false and false", False),
        ("true or true", True),
        ("true or false", True),
        ("false or true", True),
        ("false or false", False),
    ]

    for src, expected in tests:
        tokens = Scanner(src).scan()
        expr = Parser(tokens).expression()
        value = Interpreter().evaluate(expr)
        assert value == expected


def test_ternary():
    tests = [
        ("true ? 1 : 2", 1),
        ("false ? 1 : 2", 2),
        ("true ? true ? 1 : 2 : 3", 1),
        ("true ? false ? 1 : 2 : 3", 2),
        ("false ? true ? 1 : 2 : 3", 3),
        ("false ? 1 : true ? 2 : 3", 2),
        ("false ? 1 : false ? 2 : 3", 3),
    ]

    for src, expected in tests:
        tokens = Scanner(src).scan()
        expr = Parser(tokens).expression()
        value = Interpreter().evaluate(expr)
        assert value == expected


def test_casting():
    tests = [
        # number casting
        ("number true", 1.0),
        ("number false", 0.0),
        ('number "42"', 42.0),
        ('number "3.14"', 3.14),
        # bool casting (en Lox: solo false y nil son falsy, todo lo demás es truthy)
        ("bool true", True),
        ("bool 0", True),
        ("bool 42", True),
        ('bool ""', True),
        ('bool "hello"', True),
        ("bool false", False),
        ("bool nil", False),
        # string casting
        ("string true", "true"),
        ("string false", "false"),
        ("string nil", "nil"),
        ("string 42", "42.0"),
        ("string 5.0", "5.0"),
        # nested casting
        ('string(number "42")', "42.0"),
        ('bool(number "0")', True),
        ("bool(bool false)", False),
        ("number(string 3.19)", 3.19),
        ("number(string 4.1) + 1", 5.1),
        ('number number number "123"', 123.0),
    ]

    for src, expected in tests:
        tokens = Scanner(src).scan()
        expr = Parser(tokens).expression()
        value = Interpreter().evaluate(expr)
        assert value == expected


def test_casting_errors():
    # Casting string no numérico a number
    tokens = Scanner('number "abc"').scan()
    expr = Parser(tokens).expression()
    with pytest.raises(RuntimeError) as excinfo:
        Interpreter().evaluate(expr)
    assert "Cannot cast string" in str(excinfo.value)

    # Casting nil a number
    tokens = Scanner("number nil").scan()
    expr = Parser(tokens).expression()
    with pytest.raises(RuntimeError) as excinfo:
        Interpreter().evaluate(expr)
    assert "Cannot cast nil to number" in str(excinfo.value)


def test_type_function():
    """Test the built-in type() function"""
    tests = [
        ("type(42)", "number"),
        ("type(3.8)", "number"),
        ("type(0)", "number"),
        ('type("hola")', "string"),
        ('type("")', "string"),
        ("type(true)", "bool"),
        ("type(false)", "bool"),
        ("type(nil)", "nil"),
        # type() es una función
        ("type(type)", "builtin function"),
    ]

    for src, expected in tests:
        tokens = Scanner(src).scan()
        expr = Parser(tokens).expression()
        value = Interpreter().evaluate(expr)
        assert value == expected, f"type({src}) returned {value}, expected {expected}"


def test_type_function_with_casting():
    tests = [
        ('type(number "42")', "number"),
        ("type(string 42)", "string"),
        ("type(bool 0)", "bool"),
        ("type(bool nil)", "bool"),
    ]

    for src, expected in tests:
        tokens = Scanner(src).scan()
        expr = Parser(tokens).expression()
        value = Interpreter().evaluate(expr)
        assert value == expected, f"type({src}) returned {value}, expected {expected}"


def test_index():
    tests = [
        ('"string"[0]', "s"),
        ('"string"[5]', "g"),
        ('"plox"[2]', "o"),
        ('"plox"[2.00]', "o"),
        ('"plox"[1.5 - (1.5 % 1)]', "l"),
        ('"plox"[2][0]', "o"),
        ('"test"[0] + "test"[1]', "te"),
    ]

    for src, expected in tests:
        tokens = Scanner(src).scan()
        expr = Parser(tokens).expression()
        value = Interpreter().evaluate(expr)
        assert value == expected

    tokens = Scanner('"test"[1.5]').scan()
    expr = Parser(tokens).expression()
    with pytest.raises(RuntimeError) as excinfo:
        Interpreter().evaluate(expr)

    assert "Index must be a positive whole number" in str(excinfo.value)

    tokens = Scanner('"test"["error"]').scan()
    expr = Parser(tokens).expression()
    with pytest.raises(RuntimeError) as excinfo:
        Interpreter().evaluate(expr)

    assert "Index must be a positive whole number" in str(excinfo.value)

    tokens = Scanner('"test"[-1]').scan()
    expr = Parser(tokens).expression()
    with pytest.raises(RuntimeError) as excinfo:
        Interpreter().evaluate(expr)

    assert "Index must be a positive whole number" in str(excinfo.value)

    tokens = Scanner('"test"[12]').scan()
    expr = Parser(tokens).expression()
    with pytest.raises(RuntimeError) as excinfo:
        Interpreter().evaluate(expr)

    assert "Index out of range" in str(excinfo.value)


def test_len_function():
    tests = [('len("")', 0), ('len("hola")', 4), ('len("con espacios")', 12)]

    for src, expected in tests:
        tokens = Scanner(src).scan()
        expr = Parser(tokens).expression()
        value = Interpreter().evaluate(expr)
        assert value == expected

    tokens = Scanner("len(1)").scan()
    expr = Parser(tokens).expression()
    with pytest.raises(RuntimeError) as excinfo:
        Interpreter().evaluate(expr)

    assert "Argument of `len` must be a string" in str(excinfo.value)

    tokens = Scanner("len(true)").scan()
    expr = Parser(tokens).expression()
    with pytest.raises(RuntimeError) as excinfo:
        Interpreter().evaluate(expr)

    assert "Argument of `len` must be a string" in str(excinfo.value)

    tokens = Scanner("len(nil)").scan()
    expr = Parser(tokens).expression()
    with pytest.raises(RuntimeError) as excinfo:
        Interpreter().evaluate(expr)

    assert "Argument of `len` must be a string" in str(excinfo.value)

def test_switch(capsys):
    tokens = Scanner("switch (1) { case 1: print 'one'; case 2: print 'two'; }").scan()
    Interpreter().interpret(Parser(tokens).parse())
    assert capsys.readouterr().out == "one\n"

    tokens = Scanner("switch (2) { case 1: print 'one'; case 2: print 'two'; }").scan()
    Interpreter().interpret(Parser(tokens).parse())
    assert capsys.readouterr().out == "two\n"

    tokens = Scanner("switch ('hello') { case 'hello': print 'matched'; }").scan()
    Interpreter().interpret(Parser(tokens).parse())
    assert capsys.readouterr().out == "matched\n"

    # no match and no default — no output
    tokens = Scanner("switch (99) { case 1: print 'one'; }").scan()
    Interpreter().interpret(Parser(tokens).parse())
    assert capsys.readouterr().out == ""

    # no match falls through to default
    tokens = Scanner("switch (99) { case 1: print 'one'; default: print 'other'; }").scan()
    Interpreter().interpret(Parser(tokens).parse())
    assert capsys.readouterr().out == "other\n"

    # default only
    tokens = Scanner("switch (99) { default: print 'default'; }").scan()
    Interpreter().interpret(Parser(tokens).parse())
    assert capsys.readouterr().out == "default\n"

    # no fallthrough — only the matching case runs
    tokens = Scanner("switch (1) { case 1: print 'a'; case 1: print 'b'; }").scan()
    Interpreter().interpret(Parser(tokens).parse())
    assert capsys.readouterr().out == "a\n"

    # multiple statements in a case body
    tokens = Scanner("switch (1) { case 1: print 'x'; print 'y'; }").scan()
    Interpreter().interpret(Parser(tokens).parse())
    assert capsys.readouterr().out == "x\ny\n"

    # subject is an expression, not just a literal
    tokens = Scanner("switch (1 + 1) { case 1: print 'one'; case 2: print 'two'; }").scan()
    Interpreter().interpret(Parser(tokens).parse())
    assert capsys.readouterr().out == "two\n"

    # switch on a variable
    tokens = Scanner("var x = 3; switch (x) { case 3: print 'three'; default: print 'other'; }").scan()
    Interpreter().interpret(Parser(tokens).parse())
    assert capsys.readouterr().out == "three\n"


def test_const():
    tokens = Scanner("const x = 42;").scan()
    stmts = Parser(tokens).parse()
    Interpreter().interpret(stmts)

    tokens = Scanner("const x = 1; x = 2;").scan()
    stmts = Parser(tokens).parse()
    with pytest.raises(RuntimeError) as excinfo:
        Interpreter().interpret(stmts)
    assert "Cannot assign to constant 'x'" in str(excinfo.value)

    tokens = Scanner("const x = 1; x++;").scan()
    stmts = Parser(tokens).parse()
    with pytest.raises(RuntimeError) as excinfo:
        Interpreter().interpret(stmts)
    assert "Cannot assign to constant 'x'" in str(excinfo.value)

    tokens = Scanner("var x = 1; { const x = 2; } x = 99;").scan()
    stmts = Parser(tokens).parse()
    Interpreter().interpret(stmts)

    tokens = Scanner("var x = 1; x = 2;").scan()
    stmts = Parser(tokens).parse()
    Interpreter().interpret(stmts)

    tokens = Scanner("const x = 1; var x = 2;").scan()
    stmts = Parser(tokens).parse()
    with pytest.raises(RuntimeError) as excinfo:
        Interpreter().interpret(stmts)
    assert "Cannot re-declare constant 'x'" in str(excinfo.value)

    tokens = Scanner("const x = 1; const x = 2;").scan()
    stmts = Parser(tokens).parse()
    with pytest.raises(RuntimeError) as excinfo:
        Interpreter().interpret(stmts)
    assert "Cannot re-declare constant 'x'" in str(excinfo.value)


def _run(src: str, capsys) -> str:
    """Helper: interpreta src y devuelve lo impreso."""
    tokens = Scanner(src).scan()
    stmts = Parser(tokens).parse()
    Interpreter().interpret(stmts)
    return capsys.readouterr().out


def _run_with_resolver(src: str, capsys) -> str:
    """Helper: interpreta src con Resolver (necesario cuando hay variables en scope anidado)."""
    from plox.Resolver import Resolver
    tokens = Scanner(src).scan()
    stmts = Parser(tokens).parse()
    interp = Interpreter()
    resolver = Resolver(interp)
    for stmt in stmts:
        resolver.resolve(stmt)
    interp.interpret(stmts)
    return capsys.readouterr().out


def test_break_in_while(capsys):
    result = _run("var i = 0; while (true) { if (i == 3) break; print i; i = i + 1; }", capsys)
    assert result == "0.0\n1.0\n2.0\n"


def test_break_in_while_never_entered(capsys):
    result = _run("var i = 0; while (false) { break; print i; }", capsys)
    assert result == ""



def test_continue_in_while(capsys):
    result = _run("var i = 0; while (i < 5) { i = i + 1; if (i == 3) continue; print i; }", capsys)
    assert result == "1.0\n2.0\n4.0\n5.0\n"


def test_break_in_for(capsys):
    result = _run_with_resolver(
        "for (var i = 0; i < 5; i = i + 1) { if (i == 3) break; print i; }",
        capsys,
    )
    assert result == "0.0\n1.0\n2.0\n"


def test_continue_in_for(capsys):
    # continue en for: el incremento (i = i + 1) debe ejecutarse igual
    result = _run_with_resolver(
        "for (var i = 0; i < 5; i = i + 1) { if (i == 2) continue; print i; }",
        capsys,
    )
    assert result == "0.0\n1.0\n3.0\n4.0\n"


def test_break_only_innermost_loop(capsys):
    result = _run_with_resolver(
        "for (var i = 0; i < 3; i = i + 1) {"
        "  for (var j = 0; j < 3; j = j + 1) { if (j == 1) break; print j; }"
        "  print i;"
        "}",
        capsys,
    )
    assert result == "0.0\n0.0\n0.0\n1.0\n0.0\n2.0\n"


def test_continue_only_innermost_loop(capsys):
    result = _run_with_resolver(
        "for (var i = 0; i < 2; i = i + 1) {"
        "  for (var j = 0; j < 3; j = j + 1) { if (j == 1) continue; print j; }"
        "  print i;"
        "}",
        capsys,
    )
    assert result == "0.0\n2.0\n0.0\n0.0\n2.0\n1.0\n"


def test_break_outside_loop_raises():
    with pytest.raises(SyntaxError) as excinfo:
        Parser(Scanner("break;").scan()).parse()
    assert "outside of a loop" in str(excinfo.value)


def test_continue_outside_loop_raises():
    with pytest.raises(SyntaxError) as excinfo:
        Parser(Scanner("continue;").scan()).parse()
    assert "outside of a loop" in str(excinfo.value)


def test_break_outside_loop_inside_function_raises():
    with pytest.raises(SyntaxError) as excinfo:
        Parser(Scanner("fun f() { break; }").scan()).parse()
    assert "outside of a loop" in str(excinfo.value)


def test_continue_outside_loop_inside_function_raises():
    with pytest.raises(SyntaxError) as excinfo:
        Parser(Scanner("fun f() { continue; }").scan()).parse()
    assert "outside of a loop" in str(excinfo.value)


def test_break_for_infinite_loop(capsys):
    result = _run_with_resolver(
        "var count = 0;"
        "for (;;) { if (count == 3) break; count = count + 1; }"
        "print count;",
        capsys,
    )
    assert result == "3.0\n"
