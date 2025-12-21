from .Token import Token, TokenLiteralType


class Expr(object):
    pass


# binary         → expression operator expression ;
# operator       → "==" | "!=" | "<" | "<=" | ">" | ">=" | "+"  | "-"  | "*" | "/" | "%" | "**";
class BinaryExpr(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left = left
        self.operator = operator
        self.right = right

    def __repr__(self) -> str:
        return f"({self.left} {self.operator} {self.right})"


# grouping       → "(" expression ")" ;
class GroupingExpr(Expr):
    def __init__(self, expression: Expr):
        self.expression = expression

    def __repr__(self) -> str:
        return f"({self.expression})"


# literal        → NUMBER | STRING | "true" | "false" | "nil" ;
class LiteralExpr(Expr):
    def __init__(self, value: TokenLiteralType):
        self.value = value

    def __repr__(self) -> str:
        if isinstance(self.value, str):
            return f'<"{self.value}">'
        elif isinstance(self.value, float):
            return f"<{self.value}>"
        elif isinstance(self.value, bool):
            return f"<TRUE>" if self.value else "<FALSE>"
        elif self.value is None:
            return "<NIL>"

        return self.value


# unary          → ( "-" | "!" ) expression ;
class UnaryExpr(Expr):
    def __init__(self, operator: Token, right: Expr):
        self.operator = operator
        self.right = right

    def __repr__(self) -> str:
        return f"({self.operator} {self.right})"


# call          → primary "(" arguments? ")" ;
# arguments     → expression ("," expression)* ;
class CallExpr(Expr):
    def __init__(self, callee: Expr, arguments: list[Expr]):
        self.callee = callee
        self.arguments = arguments

    def __repr__(self) -> str:
        args = ", ".join(str(arg) for arg in self.arguments)
        return f"fn<{self.callee}({args})>"


# variable       → IDENTIFIER ;
class VariableExpr(Expr):
    def __init__(self, name: Token):
        self.name = name

    def __repr__(self) -> str:
        return f"<{self.name.lexeme}>"


# assignment    → IDENTIFIER "=" expression ;
class AssignmentExpr(Expr):
    def __init__(self, name: Token, value: Expr):
        self.name = name
        self.value = value

    def __repr__(self) -> str:
        return f"{self.name.lexeme} = {self.value}"


# logic         → expression (("and" | "or") expression )* ;
class LogicExpr(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left = left
        self.operator = operator
        self.right = right

    def __repr__(self) -> str:
        return f"({self.left} {self.operator} {self.right})"


# postfix         → expression "++" ;
class PostfixExpr(Expr):
    def __init__(self, left: Expr, operator: Token):
        self.left = left
        self.operator = operator

    def __repr__(self) -> str:
        return f"Postfix: [{self.left} {self.operator.lexeme}]"


# ternary        → expresion "?" expression ":" expression ;
class TernaryExpr(Expr):
    def __init__(self, condition: Expr, true_branch: Expr, false_branch: Expr):
        self.condition = condition
        self.true_branch = true_branch
        self.false_branch = false_branch

    def __repr__(self) -> str:
        return f"Ternary: [{self.condition} ? {self.true_branch} : {self.false_branch}]"
