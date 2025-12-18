from enum import Enum, auto
from functools import singledispatchmethod
from typing import Callable, Iterable
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
class Branch(Enum):
    MID = auto()
    LAST = auto()


class PrettyPrinter:
    OFS_SIZE = 4

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
        self._ofs = 0
        self._path: list[Branch] = []
        self._branch_f = branch_f
        self._expr_f = expr_f
        self._stmt_f = stmt_f
        self._type_f = type_f

        # Necesita reset
        self._entries: list[tuple[str, str, str, Callable[[str], str]]] = []

    # Printear por stdout el ast de forma más legible
    def print(self, stmts: list[Stmt]):
        for stmt in stmts:
            self._accept(stmt)

        ast = self._prettify()
        self._reset()
        print(f"\n{ast}\n")

    @singledispatchmethod
    def _accept(self, obj: Expr | Stmt) -> None:
        raise RuntimeError(f"Unknown object type: `{type(obj)}`")

    # ---------- Handlers de Statements ---------- #

    @_accept.register
    def _(self, stmt: BlockStmt):
        self._store_stmt("block:", "BlockStmt")
        self._shift(stmt._statements)

    @_accept.register
    def _(self, stmt: ExpressionStmt):
        self._accept(stmt._expression)

    @_accept.register
    def _(self, stmt: FunDecl):
        name = stmt._name.lexeme
        parameters = ",".join(p.lexeme for p in stmt._parameters)
        tag = f"{name}({parameters}):"

        self._store_stmt(tag, "FunDecl")
        self._shift(stmt._body)

    @_accept.register
    def _(self, stmt: IfStmt):
        self._store_stmt("if:", "IfStmt(cond)")
        self._shift([stmt._condition])

        self._store_stmt("then:", "IfStmt(then)")
        self._shift([stmt._thenBranch])

        if else_branch := stmt._elseBranch:
            self._store_stmt("else:", "IfStmt(else)")
            self._shift([else_branch])

    @_accept.register
    def _(self, stmt: PrintStmt):
        self._store_stmt("print:", "PrintStmt")
        self._shift([stmt._expression])

    @_accept.register
    def _(self, stmt: ReturnStmt):
        self._store_stmt("return:", "ReturnStmt")

        if expr := stmt._value:
            self._shift([expr])

    @_accept.register
    def _(self, stmt: VarDecl):
        tag = stmt._name.lexeme
        self._store_stmt(f"{tag}:", "VarDecl")

        if init := stmt._initializer:
            self._shift([init])

    @_accept.register
    def _(self, stmt: WhileStmt):
        self._store_stmt("while:", "WhileStmt(cond)")
        self._shift([stmt._condition])

        self._store_stmt("body:", "WhileStmt(body)")
        self._shift([stmt._body])

    # ---------- Handlers de Expresiones ---------- #

    @_accept.register
    def _(self, expr: AssignmentExpr):
        self._store_expr(expr._name.lexeme, "AssignmentExpr")
        self._branch(Branch.LAST, [expr._value])

    @_accept.register
    def _(self, expr: BinaryExpr):
        self._store_expr(expr._operator.lexeme, "BinaryExpr")
        self._branch(Branch.MID, [expr._right])
        self._branch(Branch.LAST, [expr._left])

    @_accept.register
    def _(self, expr: CallExpr):
        self._store_expr("@", "CallExpr")
        self._branch(Branch.MID, reversed(expr._arguments))
        self._branch(Branch.LAST, [expr._callee])

    @_accept.register
    def _(self, expr: GroupingExpr):
        self._store_expr("()", "GroupingExpr")
        self._branch(Branch.LAST, [expr._expression])

    @_accept.register
    def _(self, expr: LiteralExpr):
        if isinstance(expr._value, str):
            tag = f'"{expr._value}"'
        else:
            tag = str(expr._value)

        self._store_expr(tag, "LiteralExpr")

    @_accept.register
    def _(self, expr: LogicExpr):
        self._store_expr(expr._operator.lexeme, "LogicExpr")
        self._branch(Branch.MID, [expr._right])
        self._branch(Branch.LAST, [expr._left])

    @_accept.register
    def _(self, expr: PostfixExpr):
        self._store_expr(expr._operator.lexeme, "PostfixExpr")
        self._branch(Branch.LAST, [expr._left])

    @_accept.register
    def _(self, expr: UnaryExpr):
        self._store_expr(expr._operator.lexeme, "UnaryExpr")
        self._branch(Branch.LAST, [expr._right])

    @_accept.register
    def _(self, expr: VariableExpr):
        self._store_expr(expr._name.lexeme, "VariableExpr")

    # ---------- Helpers ---------- #

    # Guarda una entrada de statement en el arreglo
    def _store_stmt(self, tag: str, name: str):
        padding = self._make_padding()
        self._entries.append((padding, tag, name, self._stmt_f))

    # Guarda una entrada de expresión en el arreglo
    def _store_expr(self, tag: str, name: str):
        padding = self._make_padding()
        self._entries.append((padding, tag, name, self._expr_f))

    # Guarda el nodo actual, mueve el arbol hacia la derecha en una unidad
    # de offset y evalua la función pasada como argumento
    def _shift(self, visits: Iterable[Stmt | Expr]):
        self._ofs += self.OFS_SIZE

        for visitable in visits:
            self._accept(visitable)

        self._ofs -= self.OFS_SIZE

    # Evalua la función pasada por parametro habiendose movido en cierta dirección
    def _branch(self, branch: Branch, visits: Iterable[Stmt | Expr]):
        self._path.append(branch)

        for visitable in visits:
            self._accept(visitable)

        self._path.pop()

    # Arma el padding para una cierta rama del ast
    def _make_padding(self) -> str:
        parts = []

        if self._path:
            for dir in self._path[:-1]:
                if dir == Branch.MID:
                    parts.append("│   ")
                else:
                    parts.append("    ")

            last = self._path[-1]
            if last == Branch.MID:
                parts.append("├── ")
            else:
                parts.append("└── ")

        return " " * self._ofs + "".join(parts)

    # Aplica las funciones provistas en el constructuor a un entry
    def _apply(
        self, padding: str, tag: str, cls_name: str, f: Callable[[str], str]
    ) -> tuple[str, str]:
        padding = self._branch_f(padding)
        tag = f(tag)
        cls_name = self._type_f(cls_name) if self._type_f else f(cls_name)
        return padding + tag, cls_name

    # Arma el string del ast usando las lineas
    # que guardó durante el recorrido por el árbol
    def _prettify(self) -> str:
        entries = []
        max_len_cls_name = 0

        for entry in self._entries:
            branch, cls_name = self._apply(*entry)
            max_len_cls_name = max(max_len_cls_name, len(cls_name))
            entries.append((branch, cls_name))

        ast = "\n".join(f"{c.ljust(max_len_cls_name)}  {b}" for b, c in entries)
        return ast

    # Limpia el arreglo de entries, esto se hace
    # por cada statement que devolvió el parser
    def _reset(self):
        self._entries.clear()
