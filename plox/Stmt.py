from .Expr import Expr
from .Token import Token


class Stmt(object):
    pass


# exprStmt       → expression ";" ;
class ExpressionStmt(Stmt):
    def __init__(self, expression: Expr):
        self.expression = expression

    def __repr__(self) -> str:
        return f"{self.expression}"


# printStmt      → "print" expression ";" ;
class PrintStmt(Stmt):
    def __init__(self, expression: Expr):
        self.expression = expression

    def __repr__(self) -> str:
        return f"PRINT {self.expression}"


# blockStmt       → "{" statement* "}" ;
class BlockStmt(Stmt):
    def __init__(self, statements: list[Stmt]):
        self.statements = statements

    def __repr__(self) -> str:
        return f"{{ {'; '.join(str(stmt) for stmt in self.statements)} }}"


# varDecl        → "var" IDENTIFIER ( "=" expression )? ";" ;
class VarDecl(Stmt):
    def __init__(self, name: Token, initializer: Expr | None):
        self.name = name
        self.initializer = initializer

    def __repr__(self) -> str:
        return f"VAR {self.name.lexeme} = {self.initializer}"


# funDecl        → "fun" IDENTIFIER "(" parameters? ")" blockStmt ;
class FunDecl(Stmt):
    def __init__(self, name: Token, parameters: list[Token], body: list[Stmt]):
        self.name = name
        self.parameters = parameters
        self.body = body

    def __repr__(self) -> str:
        params = ", ".join(param.lexeme for param in self.parameters)
        return f"FUN fn<{self.name.lexeme}({params})> {{ {('; '.join(str(stmt) for stmt in self.body))} }}"


# returnStmt     → "return" expression? ";" ;
class ReturnStmt(Stmt):
    def __init__(self, value: Expr | None):
        self.value = value

    def __repr__(self) -> str:
        return f"RETURN {self.value or 'NIL'}"


# ifStmt        → "if" "(" expression ")" statement ( "else" statement )? ;
class IfStmt(Stmt):
    def __init__(self, condition: Expr, thenBranch: Stmt, elseBranch: Stmt | None):
        self.condition = condition
        self.thenBranch = thenBranch
        self.elseBranch = elseBranch

    def __repr__(self) -> str:
        if self.elseBranch is None:
            return (
                f"IF {self.condition} THEN {self.thenBranch}"
            )
        return f"IF {self.condition} THEN {self.thenBranch} ELSE {self.elseBranch}"


# whileStmt     → "while" "(" expression ")" statement ;
class WhileStmt(Stmt):
    def __init__(self, condition: Expr, body: Stmt):
        self.condition = condition
        self.body = body

    def __repr__(self) -> str:
        return f"WHILE {self.condition} {self.body}"
