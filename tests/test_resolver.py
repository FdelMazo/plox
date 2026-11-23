import pytest

from plox.Interpreter import Interpreter
from plox.Parser import Parser
from plox.Resolver import Resolver
from plox.Scanner import Scanner


def resolve_source(source, resolver):
    statements = Parser(Scanner(source).scan()).parse()
    for statement in statements:
        resolver.resolve(statement)
    return statements


@pytest.mark.parametrize(
    "source",
    [
        "return;",
        "return 1;",
        "{ return; }",
        "if (false) return 1;",
        "while (false) return;",
        "for (; false;) return;",
        "fun f(){ return 1; } return;",
    ],
)
def test_rejects_return_outside_function(source):
    resolver = Resolver(Interpreter())
    with pytest.raises(SyntaxError, match="return fuera de una función"):
        resolve_source(source, resolver)
    assert resolver.inside_function is False
    assert resolver.scopes == []


def test_nested_function_preserves_the_outer_function_context(capsys):
    interpreter = Interpreter()
    resolver = Resolver(interpreter)
    source = """
        fun outer() {
            fun inner() { return 2; }
            if (true) { return inner() + 1; }
        }
        print outer();
    """
    interpreter.interpret(resolve_source(source, resolver))
    assert capsys.readouterr().out == "3\n"
    assert resolver.inside_function is False
    assert resolver.scopes == []


@pytest.mark.parametrize("body", ["return;", "return nil;", ""])
def test_accepts_empty_and_implicit_returns(body, capsys):
    interpreter = Interpreter()
    resolver = Resolver(interpreter)
    interpreter.interpret(resolve_source(f"fun f(){{{body}}} print f();", resolver))
    assert capsys.readouterr().out == "nil\n"


def test_resolver_recovers_after_an_error_in_nested_function_blocks(capsys):
    interpreter = Interpreter()
    resolver = Resolver(interpreter)
    source = "fun outer(){ fun inner(){ { var a = a; } } }"
    with pytest.raises(NameError, match="declared but not defined"):
        resolve_source(source, resolver)
    assert resolver.inside_function is False
    assert resolver.scopes == []

    with pytest.raises(SyntaxError, match="return fuera de una función"):
        resolve_source("return;", resolver)
    interpreter.interpret(resolve_source("fun f(){ return 7; } print f();", resolver))
    assert capsys.readouterr().out == "7\n"


def test_resolver_restores_state_after_duplicate_parameters():
    resolver = Resolver(Interpreter())
    with pytest.raises(NameError, match="already exists"):
        resolve_source("fun f(a, a){return a;}", resolver)
    assert resolver.inside_function is False
    assert resolver.scopes == []
