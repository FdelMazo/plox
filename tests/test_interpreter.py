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
