import pytest
from plox.Expr import BinaryExpr, GroupingExpr, LiteralExpr, UnaryExpr, AssignmentExpr
from plox.Scanner import Scanner
from plox.Parser import Parser
from plox.Token import TokenType
from plox.Stmt import (
    ExpressionStmt,
    PrintStmt,
    BlockStmt,
    VarDecl,
    FunDecl,
    ReturnStmt,
    IfStmt,
    WhileStmt,
)
from plox.Expr import VariableExpr


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


def test_expression_stmt():
    tokens = Scanner("123; 456;").scan()
    stmts = Parser(tokens).parse()
    assert len(stmts) == 2
    assert isinstance(stmts[0], ExpressionStmt)
    assert isinstance(stmts[0]._expression, LiteralExpr)
    assert stmts[0]._expression._value == 123.0
    assert isinstance(stmts[1], ExpressionStmt)
    assert isinstance(stmts[1]._expression, LiteralExpr)
    assert stmts[1]._expression._value == 456.0


def test_print_stmt():
    tokens = Scanner('print "hola";').scan()
    stmts = Parser(tokens).parse()
    assert len(stmts) == 1
    stmt = stmts[0]
    assert isinstance(stmt, PrintStmt)
    assert isinstance(stmt._expression, LiteralExpr)
    assert stmt._expression._value == "hola"


def test_block_stmt():
    tokens = Scanner("{ 1; 2; }").scan()
    stmts = Parser(tokens).parse()
    assert len(stmts) == 1
    stmt = stmts[0]
    assert isinstance(stmt, BlockStmt)
    assert len(stmt._statements) == 2
    assert isinstance(stmt._statements[0], ExpressionStmt)
    assert isinstance(stmt._statements[1], ExpressionStmt)


def test_var_decl():
    tokens = Scanner("var x = 5;").scan()
    stmts = Parser(tokens).parse()
    assert len(stmts) == 1
    stmt = stmts[0]
    assert isinstance(stmt, VarDecl)
    assert stmt._name.lexeme == "x"
    assert isinstance(stmt._initializer, LiteralExpr)
    assert stmt._initializer._value == 5.0


def test_function_decl_and_return():
    src = "fun add(a, b) { return a; }"
    tokens = Scanner(src).scan()
    stmts = Parser(tokens).parse()
    assert len(stmts) == 1
    fn = stmts[0]
    assert isinstance(fn, FunDecl)
    assert fn._name.lexeme == "add"
    assert [p.lexeme for p in fn._parameters] == ["a", "b"]
    assert len(fn._body) == 1
    ret = fn._body[0]
    assert isinstance(ret, ReturnStmt)
    assert isinstance(ret._value, VariableExpr)
    assert ret._value._name.lexeme == "a"


def test_return_stmt():
    tokens = Scanner("return 3;").scan()
    stmts = Parser(tokens).parse()
    assert isinstance(stmts[0], ReturnStmt)
    assert isinstance(stmts[0]._value, LiteralExpr)
    assert stmts[0]._value._value == 3.0

    tokens = Scanner("return;").scan()
    stmts = Parser(tokens).parse()
    assert isinstance(stmts[0], ReturnStmt)
    assert stmts[0]._value is None


def test_control_flow():
    tokens = Scanner("if (true) 1; else 2;").scan()
    stmts = Parser(tokens).parse()
    assert isinstance(stmts[0], IfStmt)
    ifs = stmts[0]
    assert isinstance(ifs._condition, LiteralExpr)
    assert ifs._condition._value is True
    assert isinstance(ifs._thenBranch, ExpressionStmt)
    assert isinstance(ifs._elseBranch, ExpressionStmt)

    tokens = Scanner("while (false) 3;").scan()
    stmts = Parser(tokens).parse()
    assert isinstance(stmts[0], WhileStmt)
    w = stmts[0]
    assert isinstance(w._condition, LiteralExpr)
    assert w._condition._value is False
    assert isinstance(w._body, ExpressionStmt)


def test_for():
    tokens = Scanner("for (var i = 0 ; i < 3 ; i = i + 1) { print 0; }").scan()
    stmts = Parser(tokens).parse()
    assert len(stmts) == 1
    stmt = stmts[0]

    assert isinstance(stmt, BlockStmt)
    assert isinstance(stmt._statements[0], VarDecl)
    assert stmt._statements[0]._name.lexeme == "i"
    assert isinstance(stmt._statements[1], WhileStmt)
    ws = stmt._statements[1]
    assert isinstance(ws._condition, BinaryExpr)
    assert ws._condition._operator.token_type == TokenType.LESS

    assert isinstance(ws._body, BlockStmt)
    assert isinstance(ws._body._statements[0], BlockStmt)
    assert isinstance(ws._body._statements[0]._statements[0], PrintStmt)
    assert isinstance(ws._body._statements[1], ExpressionStmt)
    assert isinstance(ws._body._statements[1]._expression, AssignmentExpr)

    tokens = Scanner("for ( ; i < 3 ; i = i + 1) { print 0; }").scan()
    stmts = Parser(tokens).parse()
    assert len(stmts) == 1
    assert isinstance(stmts[0], WhileStmt)

    tokens = Scanner("for (var i = 0 ;  ; i = i + 1) { print 0; }").scan()
    stmts = Parser(tokens).parse()
    assert isinstance(stmts[0], BlockStmt)
    stmt = stmts[0]
    assert isinstance(stmt._statements[0], VarDecl)
    assert isinstance(stmt._statements[1], WhileStmt)
    assert isinstance(stmt._statements[1]._condition, LiteralExpr)
    assert stmt._statements[1]._condition._value is True

    tokens = Scanner("for (var i = 0 ; i < 3 ; ) { print 0; }").scan()
    stmts = Parser(tokens).parse()
    assert isinstance(stmts[0], BlockStmt)
    stmt = stmts[0]
    assert isinstance(stmt._statements[1], WhileStmt)
    inner_body = stmt._statements[1]._body
    assert isinstance(inner_body, BlockStmt)
    assert len(inner_body._statements) == 1
    assert isinstance(inner_body._statements[0], PrintStmt)
