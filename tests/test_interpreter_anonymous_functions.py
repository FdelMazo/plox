from plox.Interpreter import Interpreter
from plox.Parser import Parser
from plox.Resolver import Resolver
from plox.Scanner import Scanner


# Corre un programa completo: scanner, parser, resolver e intérprete
def run(src: str):
    statements = Parser(Scanner(src).scan()).parse()
    interpreter = Interpreter()
    resolver = Resolver(interpreter)
    for stmt in statements:
        resolver.resolve(stmt)
    return interpreter.interpret(statements)


def test_lambda_as_argument(capsys):
    run("""
        fun thrice(fn) {
          for (var i = 1; i <= 3; i = i + 1) {
            fn(i);
          }
        }
        thrice(fun (a) { print a; });
    """)
    assert capsys.readouterr().out == "1\n2\n3\n"


def test_lambda_closure(capsys):
    # La lambda recuerda `n` aunque makeAdder ya haya terminado
    run("""
        fun makeAdder(n) {
          return fun (x) { return x + n; };
        }
        var add3 = makeAdder(3);
        print add3(4);
    """)
    assert capsys.readouterr().out == "7\n"


def test_lambda_repr(capsys):
    run("print fun (a, b) {};")
    assert capsys.readouterr().out == "<fn anonymous(a, b)>\n"


def test_lambda_immediate_call(capsys):
    run('(fun () { print "hola"; })();')
    assert capsys.readouterr().out == "hola\n"


def test_lambda_lexical_scope(capsys):
    # La función usa el entorno donde se declaró, no donde se llama
    run("""
        var x = "global";
        var show = fun () { print x; };
        fun f() {
          var x = "local";
          show();
        }
        f();
    """)
    assert capsys.readouterr().out == "global\n"
