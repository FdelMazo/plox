from enum import Enum, auto
from functools import singledispatchmethod
from typing import Callable
from .Stmt import (
    BlockStmt,
    ExpressionStmt,
    FunDecl,
    IfStmt,
    PrintStmt,
    ReturnStmt,
    Stmt,
    VarDecl,
    WhileStmt,
)
from .Expr import (
    Expr,
    AssignmentExpr,
    BinaryExpr,
    CallExpr,
    GroupingExpr,
    LiteralExpr,
    LogicExpr,
    PostfixExpr,
    UnaryExpr,
    VariableExpr,
)


# Indica una dirección, con una lista de ellas se puede reconstruir
# el camino que atraveso el printer para llegar a cada expresión.
class Dir(Enum):
    LEFT = auto()
    RIGHT = auto()


class PrettyPrinter:
    def __init__(self, stmts: list[Stmt]):
        self._stmts: list[Stmt] = stmts
        self._path: list[Dir] = []
        self._shift: int = 0

    # Printear por stdout el ast de forma más legible
    def print(self, f: Callable[[str], str] = lambda x: x):
        for stmt in self._stmts:
            print(f(self._accept(stmt)))

    @singledispatchmethod
    def _accept(self, obj: Expr | Stmt) -> str:
        raise RuntimeError(f"Unknown object type: `{type(obj)}`")

    # ---------- Printers de Statements ---------- #

    @_accept.register
    def _(self, stmt: ExpressionStmt) -> str:
        return self._accept(stmt._expression)

    @_accept.register
    def _(self, stmt: PrintStmt) -> str:
        return self._shifted("print", lambda: self._accept(stmt._expression))

    @_accept.register
    def _(self, stmt: BlockStmt) -> str:
        return "\n".join(self._accept(s) for s in stmt._statements)

    @_accept.register
    def _(self, stmt: VarDecl) -> str:
        if stmt._initializer is None:
            return ""

        tag = stmt._name.lexeme
        return self._shifted(tag, lambda: self._accept(stmt._initializer))

    @_accept.register
    def _(self, stmt: FunDecl) -> str:
        name = stmt._name.lexeme
        parameters = ",".join(p.lexeme for p in stmt._parameters)
        tag = f"{name}({parameters})"
        return self._shifted(
            tag, lambda: "\n".join(self._accept(s) for s in stmt._body)
        )

    @_accept.register
    def _(self, stmt: ReturnStmt) -> str:
        if stmt._value is None:
            return ""

        return self._shifted("return", lambda: self._accept(stmt._value))

    @_accept.register
    def _(self, stmt: IfStmt) -> str:
        condition = self._shifted("if", lambda: self._accept(stmt._condition))
        then_branch = self._shifted("then", lambda: self._accept(stmt._thenBranch))
        parts = condition + "\n" + then_branch

        if stmt._elseBranch:
            parts += "\n" + self._shifted(
                "else", lambda: self._accept(stmt._elseBranch)
            )

        return parts

    @_accept.register
    def _(self, stmt: WhileStmt) -> str:
        condition = self._shifted("while", lambda: self._accept(stmt._condition))
        body = self._shifted("do", lambda: self._accept(stmt._body))
        return condition + "\n" + body

    # ---------- Printers de Expresiones ---------- #

    @_accept.register
    def _(self, expr: BinaryExpr | LogicExpr) -> str:
        padding = self._make_padding()
        symbol = expr._operator.lexeme
        line = f"{padding}{symbol}\n"
        r = self._branch(Dir.RIGHT, lambda: self._accept(expr._right))
        l = self._branch(Dir.LEFT, lambda: self._accept(expr._left))
        return line + r + l

    @_accept.register
    def _(self, expr: GroupingExpr) -> str:
        return self._accept(expr._expression)

    @_accept.register
    def _(self, expr: LiteralExpr) -> str:
        padding = self._make_padding()

        if isinstance(expr._value, str):
            return f'{padding}"{expr._value}"\n'

        return f"{padding}{expr._value}\n"

    @_accept.register
    def _(self, expr: UnaryExpr) -> str:
        padding = self._make_padding()
        symbol = expr._operator.lexeme
        line = f"{padding}{symbol}\n"
        return line + self._branch(Dir.LEFT, lambda: self._accept(expr._right))

    @_accept.register
    def _(self, expr: CallExpr) -> str:
        line = self._accept(expr._callee)
        args = expr._arguments
        first = rest = ""

        if args:
            first = self._branch(Dir.LEFT, lambda: self._accept(args[0]))
            rest = self._branch(
                Dir.RIGHT,
                lambda: "".join(self._accept(arg) for arg in reversed(args[1:])),
            )

        return line + rest + first

    @_accept.register
    def _(self, expr: VariableExpr) -> str:
        padding = self._make_padding()
        symbol = expr._name.lexeme
        return f"{padding}{symbol}\n"

    @_accept.register
    def _(self, expr: AssignmentExpr) -> str:
        padding = self._make_padding()
        symbol = expr._name.lexeme
        line = f"{padding}{symbol}\n"
        return line + self._branch(Dir.LEFT, lambda: self._accept(expr._value))

    @_accept.register
    def _(self, expr: PostfixExpr) -> str:
        padding = self._make_padding()
        symbol = expr._operator.lexeme
        line = f"{padding}{symbol}\n"
        return line + self._branch(Dir.LEFT, lambda: self._accept(expr._left))

    # ---------- Helpers ---------- #

    # Mueve el subárbol hacia la derecha en una unidad de offset y devuelve
    # la concatenación entre `tag` y el subarbol generado
    def _shifted(self, tag: str, f: Callable[[], str]) -> str:
        self._shift += 1
        s = f()
        self._shift -= 1
        padding = self._make_padding()
        return f"{padding}{tag}:\n{s}"

    # Evalua la función pasada por parametro habiendose movido en cierta dirección
    def _branch(self, direction: Dir, f: Callable[[], str]) -> str:
        self._path.append(direction)
        s = f()
        self._path.pop()
        return s

    # Arma el padding para una cierta rama del ast
    def _make_padding(self) -> str:
        padding = []

        if self._path:
            for dir in self._path[:-1]:
                if dir == Dir.RIGHT:
                    padding.append("│   ")
                else:
                    padding.append("    ")

            last = self._path[-1]
            if last == Dir.RIGHT:
                padding.append("├── ")
            else:
                padding.append("└── ")

        return " " * (4 * self._shift) + "".join(padding)
