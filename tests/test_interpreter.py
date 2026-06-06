import pytest
from plox.Expr import BinaryExpr, GroupingExpr, LiteralExpr, UnaryExpr
from plox.Interpreter import Interpreter
from plox.Scanner import Scanner
from plox.Parser import Parser
from plox.Resolver import Resolver
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

    assert "Operands of + must be either numbers or strings" in str(
        excinfo.value)

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


def test_array_literal_and_indexing():
    tokens = Scanner("[1, 2, [3, 4]]").scan()
    expr = Parser(tokens).expression()
    value = Interpreter().evaluate(expr)
    assert isinstance(value, list)
    assert value[0] == 1
    assert value[2][1] == 4


def test_array_index_assignment_statement_and_expression_return():
    interp = Interpreter()
    stmts = Parser(Scanner("var a = [1, 2, 3]; a[1] = 20;").scan()).parse()
    interp.interpret(stmts)

    tokens = Scanner("a[1]").scan()
    expr = Parser(tokens).expression()
    val = interp.evaluate(expr)
    assert val == 20

    tokens = Scanner("a[2] = 99").scan()
    expr = Parser(tokens).expression()
    ret = interp.evaluate(expr)
    assert ret == 99
    tokens = Scanner("a[2]").scan()
    expr = Parser(tokens).expression()
    assert interp.evaluate(expr) == 99


def test_dict_literal_and_indexing_and_assignment():
    interp = Interpreter()
    stmts = Parser(Scanner(
        'var d = {"x": 1, "y": [0, 0]}; d["x"] = 42; d["y"][1] = 7;').scan()).parse()
    interp.interpret(stmts)

    tokens = Scanner('d["x"]').scan()
    expr = Parser(tokens).expression()
    assert interp.evaluate(expr) == 42

    tokens = Scanner('d["y"][1]').scan()
    expr = Parser(tokens).expression()
    assert interp.evaluate(expr) == 7


def test_index_assignment_errors():
    interp = Interpreter()

    stmts = Parser(Scanner("var n = 1; n[0] = 2;").scan()).parse()
    with pytest.raises(RuntimeError):
        interp.interpret(stmts)


def test_mutability_when_passing_array_to_function():
    interp = Interpreter()
    src = """
        fun setElementByReference(arr, index, value) {
            arr[index] = value;
        }
        
        var b = [1, 2, 3]; 
        setElementByReference(b, 0, 10);
    """

    stmts = Parser(Scanner(src).scan()).parse()

    resolver = Resolver(interp)
    for s in stmts:
        resolver.resolve(s)
    interp.interpret(stmts)

    tokens = Scanner("b[0]").scan()
    expr = Parser(tokens).expression()
    assert interp.evaluate(expr) == 10

    stmts = Parser(
        Scanner("var c = b; setElementByReference(c, 1, 20);").scan()).parse()
    interp.interpret(stmts)
    tokens = Scanner("b[1]").scan()
    expr = Parser(tokens).expression()
    assert interp.evaluate(expr) == 20


def test_mutability_when_passing_dict_to_function():
    interp = Interpreter()
    src = """
        fun setKeyByReference(dict, key, value) { 
            dict[key] = value; 
        } 
        var d = {"key": "value"}; 
        setKeyByReference(d, "key", "set value by dict reference");
    """

    stmts = Parser(Scanner(src).scan()).parse()
    resolver = Resolver(interp)
    for s in stmts:
        resolver.resolve(s)
    interp.interpret(stmts)

    tokens = Scanner('d["key"]').scan()
    expr = Parser(tokens).expression()
    assert interp.evaluate(expr) == "set value by dict reference"

    stmts = Parser(Scanner(
        'var c = d; setKeyByReference(c, "other", "other value");').scan()).parse()
    interp.interpret(stmts)
    tokens = Scanner('d["other"]').scan()
    expr = Parser(tokens).expression()
    assert interp.evaluate(expr) == "other value"

    stmts = Parser(
        Scanner('var d = {"a":1}; var k = [1]; d[k] = 2;').scan()).parse()
    with pytest.raises(RuntimeError):
        interp.interpret(stmts)


def test_keys_builtin():
    expr = Parser(Scanner('keys({"a":1, "b":2})').scan()).expression()
    assert Interpreter().evaluate(expr) == ["a", "b"]

    expr = Parser(Scanner('keys([1,2])').scan()).expression()
    with pytest.raises(RuntimeError):
        Interpreter().evaluate(expr)


def test_values_builtin():
    expr = Parser(Scanner('values({"a":1, "b":2})').scan()).expression()
    assert Interpreter().evaluate(expr) == [1, 2]

    expr = Parser(Scanner('values(1)').scan()).expression()
    with pytest.raises(RuntimeError):
        Interpreter().evaluate(expr)


def test_items_builtin():
    expr = Parser(Scanner('items({"a":1, "b":2})').scan()).expression()
    assert Interpreter().evaluate(expr) == [["a", 1], ["b", 2]]

    expr = Parser(Scanner('items(1)').scan()).expression()
    with pytest.raises(RuntimeError):
        Interpreter().evaluate(expr)


def test_append_builtin():
    expr = Parser(Scanner('append([1,2], 3)').scan()).expression()
    assert Interpreter().evaluate(expr) == [1, 2, 3]

    expr = Parser(Scanner('append(1, 2)').scan()).expression()
    with pytest.raises(RuntimeError):
        Interpreter().evaluate(expr)


def test_remove_builtin():
    expr = Parser(Scanner('remove([1,2,3], 2)').scan()).expression()
    assert Interpreter().evaluate(expr) == [1, 3]

    expr = Parser(Scanner('remove({"x":1, "y":2}, "x")').scan()).expression()
    assert Interpreter().evaluate(expr) == {"y": 2}

    expr = Parser(Scanner('remove(1, 2)').scan()).expression()
    with pytest.raises(RuntimeError):
        Interpreter().evaluate(expr)


def test_insert_builtin():
    expr = Parser(Scanner('insert([1,3], 1, 2)').scan()).expression()
    assert Interpreter().evaluate(expr) == [1, 2, 3]

    expr = Parser(Scanner('insert({"a":1}, "b", 2)').scan()).expression()
    assert Interpreter().evaluate(expr) == {"a": 1, "b": 2}

    expr = Parser(Scanner('insert([1,2], 10, 3)').scan()).expression()
    with pytest.raises(RuntimeError):
        Interpreter().evaluate(expr)


def test_search_builtin():
    expr = Parser(Scanner('search([1,2,3], 2)').scan()).expression()
    assert Interpreter().evaluate(expr) == 1

    expr = Parser(Scanner('search([1,2], 9)').scan()).expression()
    assert Interpreter().evaluate(expr) is None

    expr = Parser(Scanner('search(1, 2)').scan()).expression()
    with pytest.raises(RuntimeError):
        Interpreter().evaluate(expr)


def test_contains_builtin():
    expr = Parser(Scanner('contains([1,2,3], 2)').scan()).expression()
    assert Interpreter().evaluate(expr) is True

    expr = Parser(Scanner('contains({"k":1}, "k")').scan()).expression()
    assert Interpreter().evaluate(expr) is True

    expr = Parser(Scanner('contains(1, 2)').scan()).expression()
    with pytest.raises(RuntimeError):
        Interpreter().evaluate(expr)


def test_sort_array_builtin():
    expr = Parser(Scanner('sort([3,1,2])').scan()).expression()
    assert Interpreter().evaluate(expr) == [1, 2, 3]

    expr = Parser(Scanner('sort(1)').scan()).expression()
    with pytest.raises(RuntimeError):
        Interpreter().evaluate(expr)


def test_sort_dict_builtin():
    expr = Parser(Scanner('sort({"b":2, "a":1})').scan()).expression()
    assert Interpreter().evaluate(expr) == {"a": 1, "b": 2}

def test_const_array():
    interp = Interpreter()
    stmts = Parser(Scanner("const a = [1, 2, 3]; a[1] = 20;").scan()).parse()
    interp.interpret(stmts)

    tokens = Scanner("a[1]").scan()
    expr = Parser(tokens).expression()
    val = interp.evaluate(expr)
    assert val == 20

    tokens = Scanner("a[2] = 99").scan()
    expr = Parser(tokens).expression()
    ret = interp.evaluate(expr)
    assert ret == 99
    tokens = Scanner("a[2]").scan()
    expr = Parser(tokens).expression()
    assert interp.evaluate(expr) == 99
    
    tokens = Scanner("const b = [1, 2, 3]; b = [3, 2, 1];").scan()
    stmts = Parser(tokens).parse()
    with pytest.raises(RuntimeError) as excinfo:
        interp.interpret(stmts)
    assert "Cannot assign to constant 'b'" in str(excinfo.value)
    
def test_const_dict():
    interp = Interpreter()
    stmts = Parser(Scanner('const d = {"x": 1}; d["x"] = 42;').scan()).parse()
    interp.interpret(stmts)

    tokens = Scanner('d["x"]').scan()
    expr = Parser(tokens).expression()
    assert interp.evaluate(expr) == 42

    tokens = Scanner('const e = {"x": 1}; e = {"y": 2};').scan()
    stmts = Parser(tokens).parse()
    with pytest.raises(RuntimeError) as excinfo:
        interp.interpret(stmts)
    assert "Cannot assign to constant 'e'" in str(excinfo.value)