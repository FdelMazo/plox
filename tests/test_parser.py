import pytest
from plox.Expr import (
    BinaryExpr,
    GroupingExpr,
    JoinedStringExpr,
    LiteralExpr,
    UnaryExpr,
    AssignmentExpr,
    PostfixExpr,
    TernaryExpr,
    IndexExpr,
    IndexAssignExpr,
    DictExpr,
    ArrayExpr,
    CallExpr,
)
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
    SwitchStmt,
    ForStmt,
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


def test_index_expr_parsing():
    tokens = Scanner("a[2]").scan()
    expr = Parser(tokens).expression()
    assert isinstance(expr, IndexExpr)
    assert isinstance(expr.target, VariableExpr)
    assert expr.target.name.lexeme == "a"
    assert isinstance(expr.index, LiteralExpr)
    assert expr.index.value == 2.0


def test_index_assign_expr_parsing():
    tokens = Scanner("a[2] = 5").scan()
    expr = Parser(tokens).expression()
    assert isinstance(expr, IndexAssignExpr)
    assert isinstance(expr.target, VariableExpr)
    assert expr.target.name.lexeme == "a"
    assert isinstance(expr.index, LiteralExpr)
    assert expr.index.value == 2.0
    assert isinstance(expr.value, LiteralExpr)
    assert expr.value.value == 5.0


def test_dict_expr_parsing():
    tokens = Scanner('["x": 1, "y": 2]').scan()
    expr = Parser(tokens).expression()
    assert isinstance(expr, DictExpr)
    assert len(expr.entries) == 2
    k0, v0 = expr.entries[0]
    assert isinstance(k0, LiteralExpr) and k0.value == "x"
    assert isinstance(v0, LiteralExpr) and v0.value == 1.0
    k1, v1 = expr.entries[1]
    assert isinstance(k1, LiteralExpr) and k1.value == "y"
    assert isinstance(v1, LiteralExpr) and v1.value == 2.0


def test_array_expr_parsing():
    tokens = Scanner('[1, "a", true]').scan()
    expr = Parser(tokens).expression()
    assert isinstance(expr, ArrayExpr)
    assert len(expr.elements) == 3
    assert isinstance(expr.elements[0], LiteralExpr) and expr.elements[0].value == 1.0
    assert isinstance(expr.elements[1], LiteralExpr) and expr.elements[1].value == "a"
    assert isinstance(expr.elements[2], LiteralExpr) and expr.elements[2].value is True


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


def test_dict_expression_statement_and_indexing():
    # dict used as a standalone expression followed by semicolon
    tokens = Scanner('["a": 1];').scan()
    stmts = Parser(tokens).parse()
    assert len(stmts) == 1
    stmt = stmts[0]
    assert isinstance(stmt, ExpressionStmt)
    assert isinstance(stmt.expression, DictExpr)
    k0, v0 = stmt.expression.entries[0]
    assert isinstance(k0, LiteralExpr) and k0.value == "a"
    assert isinstance(v0, LiteralExpr) and v0.value == 1.0

    # dict literal immediately indexed
    tokens = Scanner('["a": 1]["a"];').scan()
    stmts = Parser(tokens).parse()
    assert len(stmts) == 1
    stmt = stmts[0]
    assert isinstance(stmt, ExpressionStmt)
    # expression should be an IndexExpr with a DictExpr as target
    assert isinstance(stmt.expression, IndexExpr)
    assert isinstance(stmt.expression.target, DictExpr)
    assert isinstance(stmt.expression.index, LiteralExpr)
    assert stmt.expression.index.value == "a"


def test_array_expression_statement_and_indexing():
    # array used as a standalone expression followed by semicolon
    tokens = Scanner("[1, 2, 3];").scan()
    stmts = Parser(tokens).parse()
    assert len(stmts) == 1
    stmt = stmts[0]
    assert isinstance(stmt, ExpressionStmt)
    assert isinstance(stmt.expression, ArrayExpr)
    assert len(stmt.expression.elements) == 3

    # array literal immediately indexed
    tokens = Scanner("[1, 2, 3][1];").scan()
    stmts = Parser(tokens).parse()
    assert len(stmts) == 1
    stmt = stmts[0]
    assert isinstance(stmt, ExpressionStmt)
    # expression should be an IndexExpr with an ArrayExpr as target
    assert isinstance(stmt.expression, IndexExpr)
    assert isinstance(stmt.expression.target, ArrayExpr)
    assert isinstance(stmt.expression.index, LiteralExpr)
    assert stmt.expression.index.value == 1.0


def test_control_flow():
    tokens = Scanner("if (true) 1; else 2;").scan()
    stmts = Parser(tokens).parse()
    assert isinstance(stmts[0], IfStmt)
    ifs = stmts[0]
    assert isinstance(ifs.condition, LiteralExpr)
    assert ifs.condition.value is True
    assert isinstance(ifs.then_branch, ExpressionStmt)
    assert isinstance(ifs.else_branch, ExpressionStmt)

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

    # El for ahora es un ForStmt propio (no desugareado)
    assert isinstance(stmt, ForStmt)
    assert isinstance(stmt.initializer, VarDecl)
    assert stmt.initializer.name.lexeme == "i"
    assert isinstance(stmt.condition, BinaryExpr)
    assert stmt.condition.operator.token_type == TokenType.LESS
    assert isinstance(stmt.increment, AssignmentExpr)
    assert isinstance(stmt.body, BlockStmt)
    assert isinstance(stmt.body.statements[0], PrintStmt)

    # for sin inicializador: el campo initializer es None
    tokens = Scanner("for ( ; i < 3 ; i = i + 1) { print 0; }").scan()
    stmts = Parser(tokens).parse()
    assert len(stmts) == 1
    stmt = stmts[0]
    assert isinstance(stmt, ForStmt)
    assert stmt.initializer is None
    assert isinstance(stmt.condition, BinaryExpr)

    # for sin condición: condition es None (el intérprete lo trata como true)
    tokens = Scanner("for (var i = 0 ;  ; i = i + 1) { print 0; }").scan()
    stmts = Parser(tokens).parse()
    stmt = stmts[0]
    assert isinstance(stmt, ForStmt)
    assert stmt.condition is None
    assert isinstance(stmt.initializer, VarDecl)

    # for sin incremento: increment es None
    tokens = Scanner("for (var i = 0 ; i < 3 ; ) { print 0; }").scan()
    stmts = Parser(tokens).parse()
    stmt = stmts[0]
    assert isinstance(stmt, ForStmt)
    assert stmt.increment is None
    assert isinstance(stmt.body, BlockStmt)
    assert len(stmt.body.statements) == 1
    assert isinstance(stmt.body.statements[0], PrintStmt)


def test_postfix_inc():
    tokens = Scanner("x++").scan()
    expr = Parser(tokens).expression()

    assert isinstance(expr, PostfixExpr)
    assert expr.operator.token_type == TokenType.PLUS_PLUS
    assert isinstance(expr.left, VariableExpr)
    assert expr.left.name.lexeme == "x"

    tokens = Scanner("-x++").scan()
    expr = Parser(tokens).expression()
    assert isinstance(expr, UnaryExpr)
    assert isinstance(expr.right, PostfixExpr)

    tokens = Scanner("x++ + 1").scan()
    expr = Parser(tokens).expression()
    assert isinstance(expr, BinaryExpr)
    assert isinstance(expr.left, PostfixExpr)
    assert isinstance(expr.right, LiteralExpr)

    tokens = Scanner("1++").scan()
    with pytest.raises(Exception) as excinfo:
        Parser(tokens).parse()
    assert "Invalid postfix target" in str(excinfo.value)


def test_prefix_inc():
    tokens = Scanner("++x").scan()
    expr = Parser(tokens).expression()

    assert isinstance(expr, AssignmentExpr)
    assert expr.name.lexeme == "x"
    assert isinstance(expr.value, BinaryExpr)
    assert isinstance(expr.value.left, VariableExpr)
    assert expr.value.left.name.lexeme == "x"
    assert isinstance(expr.value.right, LiteralExpr)
    assert expr.value.right.value == 1.0

    tokens = Scanner("++1").scan()
    with pytest.raises(Exception) as excinfo:
        Parser(tokens).parse()
    assert "Invalid prefix target" in str(excinfo.value)


def test_ternary():
    tokens = Scanner("true ? 1 : 2").scan()
    expr = Parser(tokens).expression()

    assert isinstance(expr, TernaryExpr)
    assert isinstance(expr.condition, LiteralExpr)
    assert expr.condition.value == True
    assert isinstance(expr.true_branch, LiteralExpr)
    assert expr.true_branch.value == 1.0
    assert isinstance(expr.false_branch, LiteralExpr)
    assert expr.false_branch.value == 2.0

    tokens = Scanner("true ? true ? 1 : 2 : true ? 1 : 2").scan()
    expr = Parser(tokens).expression()

    assert isinstance(expr, TernaryExpr)
    assert isinstance(expr.true_branch, TernaryExpr)
    assert isinstance(expr.false_branch, TernaryExpr)

    tokens = Scanner("true ? 1").scan()
    with pytest.raises(Exception) as excinfo:
        Parser(tokens).parse()
    assert "Expected ':' after ternary" in str(excinfo.value)


def test_power():
    tokens = Scanner("2 ** 3").scan()
    expr = Parser(tokens).expression()

    assert isinstance(expr, BinaryExpr)
    assert expr.operator.token_type == TokenType.STAR_STAR
    assert isinstance(expr.left, LiteralExpr)
    assert expr.left.value == 2.0
    assert isinstance(expr.right, LiteralExpr)
    assert expr.right.value == 3.0

    tokens = Scanner("2 ** 3 ** 4").scan()
    expr = Parser(tokens).expression()

    assert isinstance(expr, BinaryExpr)
    assert expr.operator.token_type == TokenType.STAR_STAR
    assert isinstance(expr.left, LiteralExpr)
    assert expr.left.value == 2.0
    assert isinstance(expr.right, BinaryExpr)
    assert isinstance(expr.right.left, LiteralExpr)
    assert expr.right.left.value == 3.0
    assert isinstance(expr.right.right, LiteralExpr)
    assert expr.right.right.value == 4.0


def test_index():
    tokens = Scanner('"hola"[3]').scan()
    expr = Parser(tokens).expression()
    assert isinstance(expr, IndexExpr)

    assert isinstance(expr.target, LiteralExpr)
    assert expr.target.value == "hola"
    assert isinstance(expr.index, LiteralExpr)
    assert expr.index.value == 3.0

    tokens = Scanner("obtener_string()[1 + 1]").scan()
    expr = Parser(tokens).expression()
    assert isinstance(expr, IndexExpr)
    assert isinstance(expr.target, CallExpr)
    assert isinstance(expr.index, BinaryExpr)

    # Soporta encadenar llamados e indexing correctamente
    tokens = Scanner("funciones()[3]()").scan()
    expr = Parser(tokens).expression()
    assert isinstance(expr, CallExpr)
    assert isinstance(expr.callee, IndexExpr)
    assert isinstance(expr.callee.target, CallExpr)


def test_const_decl():
    tokens = Scanner("const x = 5;").scan()
    stmts = Parser(tokens).parse()
    assert len(stmts) == 1
    stmt = stmts[0]
    assert isinstance(stmt, VarDecl)
    assert stmt.is_constant is True
    assert stmt.name.lexeme == "x"
    assert isinstance(stmt.initializer, LiteralExpr)
    assert stmt.initializer.value == 5.0


def test_const_decl_error():
    tokens = Scanner("const x;").scan()
    with pytest.raises(SyntaxError) as excinfo:
        Parser(tokens).parse()
    assert str(excinfo.value) == "Constant `x` must be initialized at declaration"


def test_switch_basic():
    src = "switch (x) { case 1: print 1; }"
    tokens = Scanner(src).scan()
    stmts = Parser(tokens).parse()
    assert len(stmts) == 1
    stmt = stmts[0]
    assert isinstance(stmt, SwitchStmt)
    assert isinstance(stmt.subject, VariableExpr)
    assert stmt.subject.name.lexeme == "x"
    assert len(stmt.cases) == 1
    assert stmt.default is None

    case_val, case_body = stmt.cases[0]
    assert isinstance(case_val, BinaryExpr)
    assert len(case_body) == 1
    assert isinstance(case_body[0], PrintStmt)


def test_switch_multiple_cases():
    src = "switch (x) { case 1: print 1; case 2: print 2; case 3: print 3; }"
    tokens = Scanner(src).scan()
    stmts = Parser(tokens).parse()
    stmt = stmts[0]
    assert isinstance(stmt, SwitchStmt)
    assert len(stmt.cases) == 3
    assert stmt.default is None

    for i, (case_val, case_body) in enumerate(stmt.cases, start=1):
        assert len(case_body) == 1
        assert isinstance(case_body[0], PrintStmt)


def test_switch_with_default():
    src = "switch (x) { case 1: print 1; default: print 99; }"
    tokens = Scanner(src).scan()
    stmts = Parser(tokens).parse()
    stmt = stmts[0]
    assert isinstance(stmt, SwitchStmt)
    assert len(stmt.cases) == 1
    assert stmt.default is not None
    assert len(stmt.default) == 1
    assert isinstance(stmt.default[0], PrintStmt)


def test_switch_default_only():
    src = "switch (x) { default: print 0; }"
    tokens = Scanner(src).scan()
    stmts = Parser(tokens).parse()
    stmt = stmts[0]
    assert isinstance(stmt, SwitchStmt)
    assert len(stmt.cases) == 0
    assert stmt.default is not None
    assert isinstance(stmt.default[0], PrintStmt)


def test_switch_empty():
    src = "switch (x) {}"
    tokens = Scanner(src).scan()
    stmts = Parser(tokens).parse()
    stmt = stmts[0]
    assert isinstance(stmt, SwitchStmt)
    assert len(stmt.cases) == 0
    assert stmt.default is None


def test_switch_multiple_stmts_in_case():
    src = "switch (x) { case 1: var a = 1; print a; }"
    tokens = Scanner(src).scan()
    stmts = Parser(tokens).parse()
    stmt = stmts[0]
    assert isinstance(stmt, SwitchStmt)
    assert len(stmt.cases) == 1

    _case_val, case_body = stmt.cases[0]
    assert len(case_body) == 2
    assert isinstance(case_body[0], VarDecl)
    assert isinstance(case_body[1], PrintStmt)


def test_switch_case_block_body():
    src = "switch (x) { case 1: { var a = 1; print a; } }"
    tokens = Scanner(src).scan()
    stmts = Parser(tokens).parse()
    stmt = stmts[0]
    assert isinstance(stmt, SwitchStmt)
    _case_val, case_body = stmt.cases[0]
    assert len(case_body) == 1
    assert isinstance(case_body[0], BlockStmt)


def test_switch_errors():
    tokens = Scanner("switch x { }").scan()
    with pytest.raises(SyntaxError) as excinfo:
        Parser(tokens).parse()
    assert "Expected '('" in str(excinfo.value)

    tokens = Scanner("switch (x { }").scan()
    with pytest.raises(SyntaxError) as excinfo:
        Parser(tokens).parse()
    assert "Expected ')'" in str(excinfo.value)

    tokens = Scanner("switch (x) case 1: print 1;").scan()
    with pytest.raises(SyntaxError) as excinfo:
        Parser(tokens).parse()
    assert "Expected '{'" in str(excinfo.value)

    tokens = Scanner("switch (x) { case 1 print 1; }").scan()
    with pytest.raises(SyntaxError) as excinfo:
        Parser(tokens).parse()
    assert "Expected ':'" in str(excinfo.value)

    tokens = Scanner("switch (x) { default print 1; }").scan()
    with pytest.raises(SyntaxError) as excinfo:
        Parser(tokens).parse()
    assert "Expected ':'" in str(excinfo.value)


def test_string_interpolation_simple():
    tokens = Scanner('"hola, ${mundo}!";').scan()
    stmts = Parser(tokens).parse()
    assert len(stmts) == 1
    assert isinstance(stmts[0], ExpressionStmt)
    assert isinstance(stmts[0].expression, JoinedStringExpr)
    for part in stmts[0].expression.parts:
        if isinstance(part, LiteralExpr):
            assert part.value in ["hola, ", "!"]
        elif isinstance(part, VariableExpr):
            assert part.name.lexeme == "mundo"
        else:
            assert False, f"Unexpected part type: {type(part)}"


def test_string_interpolation_with_ternary():
    tokens = Scanner('"hola, ${condicion ? "amigo" : "desconocido"}!";').scan()
    stmts = Parser(tokens).parse()

    assert len(stmts) == 1
    assert isinstance(stmts[0], ExpressionStmt)
    assert isinstance(stmts[0].expression, JoinedStringExpr)
    for part in stmts[0].expression.parts:
        if isinstance(part, LiteralExpr):
            assert part.value in ["hola, ", "!"]
        elif isinstance(part, TernaryExpr):
            assert isinstance(part.condition, VariableExpr)
            assert part.condition.name.lexeme == "condicion"
            assert isinstance(part.true_branch, LiteralExpr)
            assert part.true_branch.value == "amigo"
            assert isinstance(part.false_branch, LiteralExpr)
            assert part.false_branch.value == "desconocido"
        else:
            assert False, f"Unexpected part type: {type(part)}"


def test_string_interpolation_double():
    tokens = Scanner('"hola, ${mundo} por parte de ${quien}!";').scan()
    stmts = Parser(tokens).parse()

    assert len(stmts) == 1
    assert isinstance(stmts[0], ExpressionStmt)
    assert isinstance(stmts[0].expression, JoinedStringExpr)
    for part in stmts[0].expression.parts:
        if isinstance(part, LiteralExpr):
            assert part.value in ["hola, ", " por parte de ", "!"]
        elif isinstance(part, VariableExpr):
            assert part.name.lexeme in ["mundo", "quien"]
        else:
            assert False, f"Unexpected part type: {type(part)}"


def test_string_interpolation_recursive():
    tokens = Scanner('"hola, ${"mundo ${quien}!"}";').scan()
    stmts = Parser(tokens).parse()

    assert len(stmts) == 1
    assert isinstance(stmts[0], ExpressionStmt)
    assert isinstance(stmts[0].expression, JoinedStringExpr)
    for part in stmts[0].expression.parts:
        if isinstance(part, LiteralExpr):
            assert part.value in ["hola, ", ""]
        elif isinstance(part, JoinedStringExpr):
            inner_parts = part.parts
            assert len(inner_parts) == 3
            assert isinstance(inner_parts[0], LiteralExpr)
            assert inner_parts[0].value == "mundo "
            assert isinstance(inner_parts[1], VariableExpr)
            assert inner_parts[1].name.lexeme == "quien"
            assert isinstance(inner_parts[2], LiteralExpr)
            assert inner_parts[2].value == "!"
        else:
            assert False, f"Unexpected part type: {type(part)}"


def test_string_interpolation_nested_100_deep():
    DEPTH = 10
    interpolation = '"${' * DEPTH + "x" + '}"' * DEPTH + ";"
    tokens = Scanner(interpolation).scan()
    stmts = Parser(tokens).parse()

    assert len(stmts) == 1
    assert isinstance(stmts[0], ExpressionStmt)
    assert isinstance(stmts[0].expression, JoinedStringExpr)
    ref = stmts[0].expression
    for _ in range(DEPTH - 1):
        part = ref.parts[1]
        assert isinstance(part, JoinedStringExpr)
        ref = part
    assert isinstance(ref.parts[1], VariableExpr)
    assert ref.parts[1].name.lexeme == "x"


def test_string_interpolation_only_allows_expressions():
    tokens = Scanner(
        '"hola, ${fun obtener_nombre() {return "plox";} obtener_nombre()}!";'
    ).scan()
    with pytest.raises(Exception) as excinfo:
        Parser(tokens).parse()
    assert "Expected expression, got `FUN` instead" in str(excinfo.value)

    tokens = Scanner('"hola, ${var x = 5;}!";').scan()
    with pytest.raises(Exception) as excinfo:
        Parser(tokens).parse()
    assert "Expected expression, got `VAR` instead" in str(excinfo.value)

    tokens = Scanner('"hola, ${if (cond) print 1;}!";').scan()
    with pytest.raises(Exception) as excinfo:
        Parser(tokens).parse()
    assert "Expected expression, got `IF` instead" in str(excinfo.value)

    tokens = Scanner('"hola, ${for (var i = 0; i < 3; i = i + 1) print i;}!";').scan()
    with pytest.raises(Exception) as excinfo:
        Parser(tokens).parse()
    assert "Expected expression, got `FOR` instead" in str(excinfo.value)

    tokens = Scanner('"hola, ${switch (x) { case 1: print 1; }}!";').scan()
    with pytest.raises(Exception) as excinfo:
        Parser(tokens).parse()
    assert "Expected expression, got `SWITCH` instead" in str(excinfo.value)

    tokens = Scanner('"hola, ${return 5;}!";').scan()
    with pytest.raises(Exception) as excinfo:
        Parser(tokens).parse()
    assert "Expected expression, got `RETURN` instead" in str(excinfo.value)

    tokens = Scanner('"hola, ${break;}!";').scan()
    with pytest.raises(Exception) as excinfo:
        Parser(tokens).parse()
    assert "Expected expression, got `BREAK` instead" in str(excinfo.value)

    tokens = Scanner('"hola, ${continue;}!";').scan()
    with pytest.raises(Exception) as excinfo:
        Parser(tokens).parse()
    assert "Expected expression, got `CONTINUE` instead" in str(excinfo.value)

    tokens = Scanner('"hola, ${while (cond) print 1;}!";').scan()
    with pytest.raises(Exception) as excinfo:
        Parser(tokens).parse()
    assert "Expected expression, got `WHILE` instead" in str(excinfo.value)

    tokens = Scanner('"hola, ${ { print 1; } }!";').scan()
    with pytest.raises(Exception) as excinfo:
        Parser(tokens).parse()
    assert "Expected expression, got `LEFT_BRACE` instead" in str(excinfo.value)


def test_string_interpolation_allow_only_one_expression():
    tokens = Scanner('"${1 2 3}"').scan()
    with pytest.raises(Exception) as excinfo:
        Parser(tokens).parse()
    assert (
        "Expected '}' after interpolated expression, got `NUMBER<2.0>` instead"
        in str(excinfo.value)
    )
