from .Expr import Expr
from .Token import Token


class Stmt(object):
    pass


# exprStmt       → expression ";" ;
class ExpressionStmt(Stmt):
    def __init__(self, expression: Expr):
        self.expression = expression

    def __repr__(self) -> str:
        return f"Expression Statement: {self.expression};"


# printStmt      → "print" expression ";" ;
class PrintStmt(Stmt):
    def __init__(self, expression: Expr):
        self.expression = expression

    def __repr__(self) -> str:
        return f"Print Statement: {self.expression};"


# blockStmt       → "{" statement* "}" ;
class BlockStmt(Stmt):
    def __init__(self, statements: list[Stmt]):
        self.statements = statements

    def __repr__(self) -> str:
        return f"Block Statement: {self.statements};"


# varDecl        → "var" IDENTIFIER ( "=" expression )? ";" ;
class VarDecl(Stmt):
    def __init__(self, name: Token, initializer: Expr | None):
        self.name = name
        self.initializer = initializer

    def __repr__(self) -> str:
        return f"Variable Declaration: {self.name.lexeme} = {self.initializer};"


# funDecl        → "fun" IDENTIFIER "(" parameters? ")" blockStmt ;
class FunDecl(Stmt):
    def __init__(self, name: Token, parameters: list[Token], body: list[Stmt]):
        self.name = name
        self.parameters = parameters
        self.body = body

    def __repr__(self) -> str:
        params = ", ".join(param.lexeme for param in self.parameters)
        return f"Function Declaration: {self.name.lexeme}({params}) {self.body};"


# returnStmt     → "return" expression? ";" ;
class ReturnStmt(Stmt):
    def __init__(self, value: Expr | None):
        self.value = value

    def __repr__(self) -> str:
        return f"Return Statement: return {self.value};"


# ifStmt        → "if" "(" expression ")" statement ( "else" statement )? ;
class IfStmt(Stmt):
    def __init__(self, condition: Expr, thenBranch: Stmt, elseBranch: Stmt | None):
        self.condition = condition
        self.thenBranch = thenBranch
        self.elseBranch = elseBranch

    def __repr__(self) -> str:
        return f"If Statement: if {self.condition} then {self.thenBranch} else {self.elseBranch};"


# whileStmt     → "while" "(" expression ")" statement ;
class WhileStmt(Stmt):
    def __init__(self, condition: Expr, body: Stmt):
        self.condition = condition
        self.body = body

    def __repr__(self) -> str:
        return f"While Statement: while {self.condition} do {self.body};"
