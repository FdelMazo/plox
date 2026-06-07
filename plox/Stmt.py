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


# varDecl        → ("var" | "const") IDENTIFIER ( "=" expression )? ";" ;
class VarDecl(Stmt):
    def __init__(self, name: Token, initializer: Expr | None, is_constant: bool = False):
        self.name = name
        self.initializer = initializer
        self.is_constant = is_constant

    def __repr__(self) -> str:
        keyword = "CONST" if self.is_constant else "VAR"
        return f"{keyword} {self.name.lexeme} = {self.initializer}"


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
    def __init__(self, condition: Expr, then_branch: Stmt, else_branch: Stmt | None):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def __repr__(self) -> str:
        if self.else_branch is None:
            return f"IF {self.condition} THEN {self.then_branch}"
        return f"IF {self.condition} THEN {self.then_branch} ELSE {self.else_branch}"


# whileStmt     → "while" "(" expression ")" statement ;
class WhileStmt(Stmt):
    def __init__(self, condition: Expr, body: Stmt):
        self.condition = condition
        self.body = body

    def __repr__(self) -> str:
        return f"WHILE {self.condition} {self.body}"


# switchStmt    → "switch" "(" expression ")" "{" switchCase* defaultCase? "}" ;
# switchCase    → "case" expression ":" statement* ;
# defaultCase   → "default" ":" statement* ;
class SwitchStmt(Stmt):
    def __init__(
        self,
        subject: Expr,
        cases: list[tuple[Expr, list[Stmt]]],
        default: list[Stmt] | None,
    ):
        self.subject = subject
        self.cases = cases  # list of (case_value_expr, case_body_stmts)
        self.default = default

    def __repr__(self) -> str:
        cases_str = "; ".join(
            f"CASE {val}: {stmts}" for val, stmts in self.cases
        )
        default_str = f" DEFAULT: {self.default}" if self.default is not None else ""
        return f"SWITCH {self.subject} {{ {cases_str}{default_str} }}"
