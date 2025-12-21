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
    assert expr.left.value == 2.0
    assert expr.operator.token_type == TokenType.PLUS
    assert expr.right.value == 2.0


def test_literals():
    tokens = Scanner('"hello"').scan()
    expr = Parser(tokens).expression()
    assert isinstance(expr, LiteralExpr)
    assert expr.value == "hello"

    tokens = Scanner("123").scan()
    expr = Parser(tokens).expression()
    assert isinstance(expr, LiteralExpr)
    assert expr.value == 123.0

    tokens = Scanner("true").scan()
    expr = Parser(tokens).expression()
    assert isinstance(expr, LiteralExpr)
    assert expr.value is True

    tokens = Scanner("false").scan()
    expr = Parser(tokens).expression()
    assert isinstance(expr, LiteralExpr)
    assert expr.value is False

    tokens = Scanner("nil").scan()
    expr = Parser(tokens).expression()
    assert isinstance(expr, LiteralExpr)
    assert expr.value is None


def test_groupings():
    tokens = Scanner("(2 + 2)").scan()
    expr = Parser(tokens).expression()

    assert isinstance(expr, GroupingExpr)
    assert isinstance(expr.expression, BinaryExpr)
    assert isinstance(expr.expression.left, LiteralExpr)
    assert expr.expression.left.value == 2.0
    assert expr.expression.operator.token_type == TokenType.PLUS
    assert isinstance(expr.expression.right, LiteralExpr)
    assert expr.expression.right.value == 2.0


def test_unary():
    tokens = Scanner("-123").scan()
    expr = Parser(tokens).expression()

    assert isinstance(expr, UnaryExpr)
    assert expr.operator.token_type == TokenType.MINUS
    assert isinstance(expr.right, LiteralExpr)
    assert expr.right.value == 123.0


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
    assert expr.operator.token_type == TokenType.MINUS

    left = expr.left
    right = expr.right

    assert isinstance(left, BinaryExpr)
    assert left.operator.token_type == TokenType.MINUS
    assert isinstance(left.left, LiteralExpr)
    assert left.left.value == 5.0
    assert isinstance(left.right, LiteralExpr)
    assert left.right.value == 3.0

    assert isinstance(right, LiteralExpr)
    assert right.value == 1.0


def test_precedence():
    tokens = Scanner("1 + 2 * 3 - 4").scan()
    expr = Parser(tokens).expression()

    assert isinstance(expr, BinaryExpr)
    assert expr.operator.token_type == TokenType.MINUS

    left = expr.left
    assert isinstance(left, BinaryExpr)
    assert left.operator.token_type == TokenType.PLUS
    assert isinstance(left.left, LiteralExpr)
    assert left.left.value == 1.0

    left_right = left.right
    assert isinstance(left_right, BinaryExpr)
    assert left_right.operator.token_type == TokenType.STAR
    assert isinstance(left_right.left, LiteralExpr)
    assert left_right.left.value == 2.0
    assert isinstance(left_right.right, LiteralExpr)
    assert left_right.right.value == 3.0

    right = expr.right
    assert isinstance(right, LiteralExpr)
    assert right.value == 4.0


def test_precedence_unary():
    tokens = Scanner("-1+2").scan()
    expr = Parser(tokens).expression()

    # Esto tiene que dar (-1) + 2, no -(1+2)
    assert isinstance(expr, BinaryExpr)
    assert expr.operator.token_type == TokenType.PLUS
    assert isinstance(expr.left, UnaryExpr)
    assert expr.left.operator.token_type == TokenType.MINUS
    assert isinstance(expr.left.right, LiteralExpr)
    assert expr.left.right.value == 1.0
    assert isinstance(expr.right, LiteralExpr)
    assert expr.right.value == 2.0


def test_big():
    tokens = Scanner("1 - (2 * 3) < 4 == false").scan()
    expr = Parser(tokens).expression()

    # Top-level == false
    assert isinstance(expr, BinaryExpr)
    assert expr.operator.token_type == TokenType.EQUAL_EQUAL

    left = expr.left
    right = expr.right

    # Right side is literal false
    assert isinstance(right, LiteralExpr)
    assert right.value is False

    # Left side is (1 - (2 * 3)) < 4
    assert isinstance(left, BinaryExpr)
    assert left.operator.token_type == TokenType.LESS

    # Right of < is 4
    assert isinstance(left.right, LiteralExpr)
    assert left.right.value == 4.0

    # Left of < is (1 - (2 * 3))
    assert isinstance(left.left, BinaryExpr)
    assert left.left.operator.token_type == TokenType.MINUS

    minus_left = left.left.left
    minus_right = left.left.right

    assert isinstance(minus_left, LiteralExpr)
    assert minus_left.value == 1.0

    # minus_right is a grouping with inner multiplication
    assert isinstance(minus_right, GroupingExpr)
    inner = minus_right.expression
    assert isinstance(inner, BinaryExpr)
    assert inner.operator.token_type == TokenType.STAR
    assert isinstance(inner.left, LiteralExpr)
    assert inner.left.value == 2.0
    assert isinstance(inner.right, LiteralExpr)
    assert inner.right.value == 3.0


def test_expression_stmt():
    tokens = Scanner("123; 456;").scan()
    stmts = Parser(tokens).parse()
    assert len(stmts) == 2
    assert isinstance(stmts[0], ExpressionStmt)
    assert isinstance(stmts[0].expression, LiteralExpr)
    assert stmts[0].expression.value == 123.0
    assert isinstance(stmts[1], ExpressionStmt)
    assert isinstance(stmts[1].expression, LiteralExpr)
    assert stmts[1].expression.value == 456.0


def test_print_stmt():
    tokens = Scanner('print "hola";').scan()
    stmts = Parser(tokens).parse()
    assert len(stmts) == 1
    stmt = stmts[0]
    assert isinstance(stmt, PrintStmt)
    assert isinstance(stmt.expression, LiteralExpr)
    assert stmt.expression.value == "hola"


def test_block_stmt():
    tokens = Scanner("{ 1; 2; }").scan()
    stmts = Parser(tokens).parse()
    assert len(stmts) == 1
    stmt = stmts[0]
    assert isinstance(stmt, BlockStmt)
    assert len(stmt.statements) == 2
    assert isinstance(stmt.statements[0], ExpressionStmt)
    assert isinstance(stmt.statements[1], ExpressionStmt)


def test_var_decl():
    tokens = Scanner("var x = 5;").scan()
    stmts = Parser(tokens).parse()
    assert len(stmts) == 1
    stmt = stmts[0]
    assert isinstance(stmt, VarDecl)
    assert stmt.name.lexeme == "x"
    assert isinstance(stmt.initializer, LiteralExpr)
    assert stmt.initializer.value == 5.0


def test_assignment():
    tokens = Scanner("x = 5;").scan()
    stmts = Parser(tokens).parse()
    assert len(stmts) == 1
    stmt = stmts[0]
    assert isinstance(stmt, ExpressionStmt)
    assert isinstance(stmt.expression, AssignmentExpr)
    assert stmt.expression.name.lexeme == "x"
    assert isinstance(stmt.expression.value, LiteralExpr)
    assert stmt.expression.value.value == 5.0

    tokens = Scanner("(x) = 5;").scan()
    with pytest.raises(Exception) as excinfo:
        Parser(tokens).parse()
    assert "Invalid assignment" in str(excinfo.value)

    tokens = Scanner("a + b = 5;").scan()
    with pytest.raises(Exception) as excinfo:
        Parser(tokens).parse()
    assert "Invalid assignment" in str(excinfo.value)


def test_function_decl_and_return():
    src = "fun add(a, b) { return a; }"
    tokens = Scanner(src).scan()
    stmts = Parser(tokens).parse()
    assert len(stmts) == 1
    fn = stmts[0]
    assert isinstance(fn, FunDecl)
    assert fn.name.lexeme == "add"
    assert [p.lexeme for p in fn.parameters] == ["a", "b"]
    assert len(fn.body) == 1
    ret = fn.body[0]
    assert isinstance(ret, ReturnStmt)
    assert isinstance(ret.value, VariableExpr)
    assert ret.value.name.lexeme == "a"


def test_return_stmt():
    tokens = Scanner("return 3;").scan()
    stmts = Parser(tokens).parse()
    assert isinstance(stmts[0], ReturnStmt)
    assert isinstance(stmts[0].value, LiteralExpr)
    assert stmts[0].value.value == 3.0

    tokens = Scanner("return;").scan()
    stmts = Parser(tokens).parse()
    assert isinstance(stmts[0], ReturnStmt)
    assert stmts[0].value is None


def test_block_stmts():
    tokens = Scanner("{ print a; }").scan()
    stmts = Parser(tokens).parse()
    assert isinstance(stmts[0], BlockStmt)
    assert len(stmts[0].statements) == 1
    assert isinstance(stmts[0].statements[0], PrintStmt)

    tokens = Scanner("{ print a; ").scan()
    with pytest.raises(Exception) as excinfo:
        Parser(tokens).parse()
    assert "Expected '}'" in str(excinfo.value)


def test_control_flow():
    tokens = Scanner("if (true) 1; else 2;").scan()
    stmts = Parser(tokens).parse()
    assert isinstance(stmts[0], IfStmt)
    ifs = stmts[0]
    assert isinstance(ifs.condition, LiteralExpr)
    assert ifs.condition.value is True
    assert isinstance(ifs.thenBranch, ExpressionStmt)
    assert isinstance(ifs.elseBranch, ExpressionStmt)

    tokens = Scanner("while (false) 3;").scan()
    stmts = Parser(tokens).parse()
    assert isinstance(stmts[0], WhileStmt)
    w = stmts[0]
    assert isinstance(w.condition, LiteralExpr)
    assert w.condition.value is False
    assert isinstance(w.body, ExpressionStmt)


def test_for():
    tokens = Scanner("for (var i = 0 ; i < 3 ; i = i + 1) { print 0; }").scan()
    stmts = Parser(tokens).parse()
    assert len(stmts) == 1
    stmt = stmts[0]

    assert isinstance(stmt, BlockStmt)
    assert isinstance(stmt.statements[0], VarDecl)
    assert stmt.statements[0].name.lexeme == "i"
    assert isinstance(stmt.statements[1], WhileStmt)
    ws = stmt.statements[1]
    assert isinstance(ws.condition, BinaryExpr)
    assert ws.condition.operator.token_type == TokenType.LESS

    assert isinstance(ws.body, BlockStmt)
    assert isinstance(ws.body.statements[0], BlockStmt)
    assert isinstance(ws.body.statements[0].statements[0], PrintStmt)
    assert isinstance(ws.body.statements[1], ExpressionStmt)
    assert isinstance(ws.body.statements[1].expression, AssignmentExpr)

    tokens = Scanner("for ( ; i < 3 ; i = i + 1) { print 0; }").scan()
    stmts = Parser(tokens).parse()
    assert len(stmts) == 1
    assert isinstance(stmts[0], WhileStmt)

    tokens = Scanner("for (var i = 0 ;  ; i = i + 1) { print 0; }").scan()
    stmts = Parser(tokens).parse()
    assert isinstance(stmts[0], BlockStmt)
    stmt = stmts[0]
    assert isinstance(stmt.statements[0], VarDecl)
    assert isinstance(stmt.statements[1], WhileStmt)
    assert isinstance(stmt.statements[1].condition, LiteralExpr)
    assert stmt.statements[1].condition.value is True

    tokens = Scanner("for (var i = 0 ; i < 3 ; ) { print 0; }").scan()
    stmts = Parser(tokens).parse()
    assert isinstance(stmts[0], BlockStmt)
    stmt = stmts[0]
    assert isinstance(stmt.statements[1], WhileStmt)
    inner_body = stmt.statements[1].body
    assert isinstance(inner_body, BlockStmt)
    assert len(inner_body.statements) == 1
    assert isinstance(inner_body.statements[0], PrintStmt)
