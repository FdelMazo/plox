import pytest
from plox.Expr import CallExpr, FunctionExpr, GroupingExpr
from plox.Parser import Parser
from plox.Scanner import Scanner
from plox.Stmt import ExpressionStmt, PrintStmt, ReturnStmt


def test_anonymous_function_expr():
    tokens = Scanner("fun (a, b) { return a; }").scan()
    expr = Parser(tokens).expression()
    assert isinstance(expr, FunctionExpr)
    assert [p.lexeme for p in expr.parameters] == ["a", "b"]
    assert len(expr.body) == 1
    assert isinstance(expr.body[0], ReturnStmt)


def test_anonymous_function_as_argument():
    tokens = Scanner("thrice(fun (a) { print a; });").scan()
    stmts = Parser(tokens).parse()
    call = stmts[0].expression
    assert isinstance(call, CallExpr)
    assert len(call.arguments) == 1
    lam = call.arguments[0]
    assert isinstance(lam, FunctionExpr)
    assert [p.lexeme for p in lam.parameters] == ["a"]
    assert isinstance(lam.body[0], PrintStmt)


def test_anonymous_function_without_params():
    tokens = Scanner("fun () {}").scan()
    expr = Parser(tokens).expression()
    assert isinstance(expr, FunctionExpr)
    assert expr.parameters == []
    assert expr.body == []


def test_anonymous_function_statement_needs_parens():
    # Un statement que arranca con `fun` siempre es una declaración
    tokens = Scanner("fun () {};").scan()
    with pytest.raises(Exception) as excinfo:
        Parser(tokens).parse()
    assert "Expected function name" in str(excinfo.value)

    # Entre paréntesis sí es válido
    tokens = Scanner("(fun () {});").scan()
    stmts = Parser(tokens).parse()
    assert isinstance(stmts[0], ExpressionStmt)
    assert isinstance(stmts[0].expression, GroupingExpr)
    assert isinstance(stmts[0].expression.expression, FunctionExpr)


def test_anonymous_function_immediate_call():
    tokens = Scanner("(fun (x) { print x; })(1);").scan()
    stmts = Parser(tokens).parse()
    call = stmts[0].expression
    assert isinstance(call, CallExpr)
    assert isinstance(call.callee, GroupingExpr)
    assert isinstance(call.callee.expression, FunctionExpr)
