from .Expr import Expr


class Stmt(object):
    pass


# exprStmt       → expression ";" ;
class ExpressionStmt(Stmt):
    def __init__(self, expression: Expr):
        self._expression = expression

    def __repr__(self) -> str:
        return f"Expression Statement: {self._expression};"


# printStmt      → "print" expression ";" ;
class PrintStmt(Stmt):
    def __init__(self, expression: Expr):
        self._expression = expression

    def __repr__(self) -> str:
        return f"Print Statement: {self._expression};"
