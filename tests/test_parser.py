import pytest
from plox.Expr import BinaryExpr, GroupingExpr, LiteralExpr, UnaryExpr
from plox.Scanner import Scanner
from plox.Parser import Parser
from plox.Token import TokenType


def test_hello_world():
    tokens = Scanner("2+2").scan()
    expr = Parser(tokens).expression()
    assert isinstance(expr, BinaryExpr)
    assert expr._left._value == 2.0
    assert expr._operator.token_type == TokenType.PLUS
    assert expr._right._value == 2.0


def test_literals():
    tokens = Scanner('"hello"').scan()
    expr = Parser(tokens).expression()
    assert isinstance(expr, LiteralExpr)
    assert expr._value == "hello"

    tokens = Scanner("123").scan()
    expr = Parser(tokens).expression()
    assert isinstance(expr, LiteralExpr)
    assert expr._value == 123.0

    tokens = Scanner("true").scan()
    expr = Parser(tokens).expression()
    assert isinstance(expr, LiteralExpr)
    assert expr._value is True

    tokens = Scanner("false").scan()
    expr = Parser(tokens).expression()
    assert isinstance(expr, LiteralExpr)
    assert expr._value is False

    tokens = Scanner("nil").scan()
    expr = Parser(tokens).expression()
    assert isinstance(expr, LiteralExpr)
    assert expr._value is None


def test_groupings():
    tokens = Scanner("(2 + 2)").scan()
    expr = Parser(tokens).expression()

    assert isinstance(expr, GroupingExpr)
    assert isinstance(expr._expression, BinaryExpr)
    assert isinstance(expr._expression._left, LiteralExpr)
    assert expr._expression._left._value == 2.0
    assert expr._expression._operator.token_type == TokenType.PLUS
    assert isinstance(expr._expression._right, LiteralExpr)
    assert expr._expression._right._value == 2.0


def test_unary():
    tokens = Scanner("-123").scan()
    expr = Parser(tokens).expression()

    assert isinstance(expr, UnaryExpr)
    assert expr._operator.token_type == TokenType.MINUS
    assert isinstance(expr._right, LiteralExpr)
    assert expr._right._value == 123.0


def test_error_parens():
    tokens = Scanner("(2 + 2").scan()
    parser = Parser(tokens)
    with pytest.raises(Exception) as excinfo:
        parser.expression()
    assert "Expected ')'" in str(excinfo.value)


def test_error_incomplete():
    tokens = Scanner("1 + ").scan()
    parser = Parser(tokens)
    with pytest.raises(Exception) as excinfo:
        parser.expression()
    assert "Expected expression" in str(excinfo.value)


def test_associativity():
    # This resolves to: (5 - 3) - 1
    tokens = Scanner("5 - 3 - 1").scan()
    expr = Parser(tokens).expression()

    assert isinstance(expr, BinaryExpr)
    assert expr._operator.token_type == TokenType.MINUS

    left = expr._left
    right = expr._right

    assert isinstance(left, BinaryExpr)
    assert left._operator.token_type == TokenType.MINUS
    assert isinstance(left._left, LiteralExpr)
    assert left._left._value == 5.0
    assert isinstance(left._right, LiteralExpr)
    assert left._right._value == 3.0

    assert isinstance(right, LiteralExpr)
    assert right._value == 1.0


def test_precedence():
    tokens = Scanner("1 + 2 * 3 - 4").scan()
    expr = Parser(tokens).expression()

    assert isinstance(expr, BinaryExpr)
    assert expr._operator.token_type == TokenType.MINUS

    left = expr._left
    assert isinstance(left, BinaryExpr)
    assert left._operator.token_type == TokenType.PLUS
    assert isinstance(left._left, LiteralExpr)
    assert left._left._value == 1.0

    left_right = left._right
    assert isinstance(left_right, BinaryExpr)
    assert left_right._operator.token_type == TokenType.STAR
    assert isinstance(left_right._left, LiteralExpr)
    assert left_right._left._value == 2.0
    assert isinstance(left_right._right, LiteralExpr)
    assert left_right._right._value == 3.0

    right = expr._right
    assert isinstance(right, LiteralExpr)
    assert right._value == 4.0


def test_big():
    tokens = Scanner("1 - (2 * 3) < 4 == false").scan()
    expr = Parser(tokens).expression()

    # Top-level == false
    assert isinstance(expr, BinaryExpr)
    assert expr._operator.token_type == TokenType.EQUAL_EQUAL

    left = expr._left
    right = expr._right

    # Right side is literal false
    assert isinstance(right, LiteralExpr)
    assert right._value is False

    # Left side is (1 - (2 * 3)) < 4
    assert isinstance(left, BinaryExpr)
    assert left._operator.token_type == TokenType.LESS

    # Right of < is 4
    assert isinstance(left._right, LiteralExpr)
    assert left._right._value == 4.0

    # Left of < is (1 - (2 * 3))
    assert isinstance(left._left, BinaryExpr)
    assert left._left._operator.token_type == TokenType.MINUS

    minus_left = left._left._left
    minus_right = left._left._right

    assert isinstance(minus_left, LiteralExpr)
    assert minus_left._value == 1.0

    # minus_right is a grouping with inner multiplication
    assert isinstance(minus_right, GroupingExpr)
    inner = minus_right._expression
    assert isinstance(inner, BinaryExpr)
    assert inner._operator.token_type == TokenType.STAR
    assert isinstance(inner._left, LiteralExpr)
    assert inner._left._value == 2.0
    assert isinstance(inner._right, LiteralExpr)
    assert inner._right._value == 3.0
