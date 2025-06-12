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


# funDecl        → "fun" IDENTIFIER "(" parameters? ")" blockStmt ;
class FunDecl(Stmt):
    def __init__(self, name: Token, parameters: list[Token], body: list[Stmt]):
        self._name = name
        self._parameters = parameters
        self._body = body

    def __repr__(self) -> str:
        params = ", ".join(param.lexeme for param in self._parameters)
        return f"Function Declaration: {self._name.lexeme}({params}) {self._body};"


# returnStmt     → "return" expression? ";" ;
class ReturnStmt(Stmt):
    def __init__(self, value: Expr | None):
        self._value = value

    def __repr__(self) -> str:
        return f"Return Statement: return {self._value};"


# ifStmt        → "if" "(" expression ")" statement ( "else" statement )? ;
class IfStmt(Stmt):
    def __init__(self, condition: Expr, thenBranch: Stmt, elseBranch: Stmt | None):
        self._condition = condition
        self._thenBranch = thenBranch
        self._elseBranch = elseBranch

    def __repr__(self) -> str:
        return f"If Statement: if {self._condition} then {self._thenBranch} else {self._elseBranch};"


# whileStmt     → "while" "(" expression ")" statement ;
class WhileStmt(Stmt):
    def __init__(self, condition: Expr, body: Stmt):
        self._condition = condition
        self._body = body

    def __repr__(self) -> str:
        return f"While Statement: while {self._condition} do {self._body};"
