from .Expr import Expr
from .Token import Token


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


# blockStmt       → "{" statement* "}" ;
class BlockStmt(Stmt):
    def __init__(self, statements: list[Stmt]):
        self._statements = statements

    def __repr__(self) -> str:
        return f"Block Statement: {self._statements};"


# varDecl        → "var" IDENTIFIER ( "=" expression )? ";" ;
class VarDecl(Stmt):
    def __init__(self, name: Token, initializer: Expr | None):
        self._name = name
        self._initializer = initializer

    def __repr__(self) -> str:
        return f"Variable Declaration: {self._name.lexeme} = {self._initializer};"
