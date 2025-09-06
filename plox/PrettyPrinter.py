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
    # Aplica funciones distintas a los distintos tipos de nodos. Aplica:
    #   - branch_f: Al padding que tiene las ramas de los arboles de expresiones
    #   - expr_f:   A los nodos de expresiones
    #   - stmt_f:   A los nodos de statements
    #   - type_f:   A la lista de tipos de nodo, en caso de ser None, utiliza su
    #               respectivo expr_f o stmt_f
    def __init__(
        self,
        branch_f: Callable[[str], str] = lambda x: x,
        expr_f: Callable[[str], str] = lambda x: x,
        stmt_f: Callable[[str], str] = lambda x: x,
        type_f: Callable[[str], str] | None = None,
    ):
        self._path = []
        self._shift = 0
        self._branch_f = branch_f
        self._expr_f = expr_f
        self._stmt_f = stmt_f
        self._type_f = type_f

        # Necesita reset
        self._entries: list[tuple[str, str, str, Callable[[str], str]]] = []

    # Printear por stdout el ast de forma más legible
    def print(self, stmts: list[Stmt]):
        for stmt in stmts:
            self._reset()
            self._accept(stmt)
            ast = self._build_tree()
            print(ast, end="\n\n")

    def _build_tree(self) -> str:
        entries = []
        max_len_branch, max_len_cls_name = 0, 0

        for entry in self._entries:
            branch, cls_name = self._apply(*entry)
            max_len_branch = max(max_len_branch, len(branch))
            max_len_cls_name = max(max_len_cls_name, len(cls_name))
            entries.append((branch, cls_name))

        ast = "\n".join(
            f"{c.ljust(max_len_cls_name)}  {b.ljust(max_len_branch)}"
            for b, c in entries
        )

        return ast

    def _reset(self):
        self._entries.clear()

    @singledispatchmethod
    def _accept(self, obj: Expr | Stmt) -> None:
        raise RuntimeError(f"Unknown object type: `{type(obj)}`")

    # ---------- Printers de Statements ---------- #

    @_accept.register
    def _(self, stmt: ExpressionStmt):
        self._accept(stmt._expression)

    @_accept.register
    def _(self, stmt: PrintStmt):
        self._shifted("print", stmt, lambda: self._accept(stmt._expression))

    @_accept.register
    def _(self, stmt: BlockStmt):
        for s in stmt._statements:
            self._accept(s)

    @_accept.register
    def _(self, stmt: VarDecl):
        tag = stmt._name.lexeme

        def shifted():
            if stmt._initializer:
                self._accept(stmt._initializer)

        self._shifted(tag, stmt, shifted)

    @_accept.register
    def _(self, stmt: FunDecl):
        name = stmt._name.lexeme
        parameters = ",".join(p.lexeme for p in stmt._parameters)
        tag = f"{name}({parameters})"

        def shifted():
            for s in stmt._body:
                self._accept(s)

        self._shifted(tag, stmt, shifted)

    @_accept.register
    def _(self, stmt: ReturnStmt):
        tag = "return"

        def shifted():
            if stmt._value:
                self._accept(stmt._value)

        self._shifted(tag, stmt, shifted)

    @_accept.register
    def _(self, stmt: IfStmt):
        self._shifted("if", stmt, lambda: self._accept(stmt._condition))
        self._shifted("then", stmt._thenBranch, lambda: self._accept(stmt._thenBranch))

        if stmt._elseBranch:
            self._shifted(
                "else",
                stmt._elseBranch,
                lambda: self._accept(stmt._elseBranch),
            )

    @_accept.register
    def _(self, stmt: WhileStmt):
        self._shifted("while", stmt, lambda: self._accept(stmt._condition))
        self._shifted("do", stmt._body, lambda: self._accept(stmt._body))

    # ---------- Printers de Expresiones ---------- #

    @_accept.register
    def _(self, expr: BinaryExpr | LogicExpr):
        self._store(expr._operator.lexeme, expr)
        self._branch(Dir.RIGHT, lambda: self._accept(expr._right))
        self._branch(Dir.LEFT, lambda: self._accept(expr._left))

    @_accept.register
    def _(self, expr: GroupingExpr):
        return self._accept(expr._expression)

    @_accept.register
    def _(self, expr: LiteralExpr):
        if isinstance(expr._value, str):
            tag = f'"{expr._value}"'
        else:
            tag = str(expr._value)

        self._store(tag, expr)

    @_accept.register
    def _(self, expr: UnaryExpr):
        self._store(expr._operator.lexeme, expr)
        self._branch(Dir.LEFT, lambda: self._accept(expr._right))

    @_accept.register
    def _(self, expr: CallExpr):
        self._accept(expr._callee)

        # Como el nombre de la función es una expresión le
        # cambio el tipo a callee de `VariableExpr` a `CallExpr`
        padding, tag, _, f = self._entries[-1]
        cls_name = expr.__class__.__name__
        self._entries[-1] = padding, tag, cls_name, f

        if args := expr._arguments:

            def shifted():
                for arg in reversed(args[1:]):
                    self._accept(arg)

            self._branch(Dir.RIGHT, shifted)
            self._branch(Dir.LEFT, lambda: self._accept(args[0]))

    @_accept.register
    def _(self, expr: VariableExpr):
        self._store(expr._name.lexeme, expr)

    @_accept.register
    def _(self, expr: AssignmentExpr):
        self._store(expr._name.lexeme, expr)
        self._branch(Dir.LEFT, lambda: self._accept(expr._value))

    @_accept.register
    def _(self, expr: PostfixExpr):
        self._store(expr._operator.lexeme, expr)
        self._branch(Dir.LEFT, lambda: self._accept(expr._left))

    # ---------- Helpers ---------- #

    # Guarda una entrada en el arreglo
    def _store(self, tag: str, obj: Expr | Stmt):
        padding = self._make_padding()
        cls_name = obj.__class__.__name__

        if isinstance(obj, Expr):
            f = self._expr_f
        else:
            tag = f"{tag}:"
            f = self._stmt_f

        self._entries.append((padding, tag, cls_name, f))

    # Mueve el subárbol hacia la derecha en una unidad de offset y devuelve
    # la concatenación entre `tag` y el subarbol generado
    def _shifted(self, tag: str, stmt: Stmt, f: Callable[[], None]):
        self._store(tag, stmt)
        self._shift += 1
        f()
        self._shift -= 1

    # Evalua la función pasada por parametro habiendose movido en cierta dirección
    def _branch(self, direction: Dir, f: Callable[[], None]):
        self._path.append(direction)
        f()
        self._path.pop()

    # Arma el padding para una cierta rama del ast
    def _make_padding(self) -> str:
        parts = []

        if self._path:
            for dir in self._path[:-1]:
                if dir == Dir.RIGHT:
                    parts.append("│   ")
                else:
                    parts.append("    ")

            last = self._path[-1]
            if last == Dir.RIGHT:
                parts.append("├── ")
            else:
                parts.append("└── ")

        return " " * (4 * self._shift) + "".join(parts)

    # Aplica las funciones provistas en el constructuor a un entry
    def _apply(
        self, padding: str, tag: str, cls_name: str, f: Callable[[str], str]
    ) -> tuple[str, str]:
        padding = self._branch_f(padding)
        tag = f(tag)
        cls_name = self._type_f(cls_name) if self._type_f else f(cls_name)
        return padding + tag, cls_name
