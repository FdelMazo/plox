from .Token import Token, TokenLiteralType


class Expr(object):
    pass


# binary         → expression operator expression ;
# operator       → "==" | "!=" | "<" | "<=" | ">" | ">=" | "+"  | "-"  | "*" | "/" ;
class BinaryExpr(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left = left
        self.operator = operator
        self.right = right

    def __repr__(self) -> str:
        return f"Binary: [{self.left}  {self.operator.lexeme} {self.right}]"


# grouping       → "(" expression ")" ;
class GroupingExpr(Expr):
    def __init__(self, expression: Expr):
        self.expression = expression

    def __repr__(self) -> str:
        return f"Grouping: ({self.expression})"


# literal        → NUMBER | STRING | "true" | "false" | "nil" ;
class LiteralExpr(Expr):
    def __init__(self, value: TokenLiteralType):
        self.value = value

    def __repr__(self) -> str:
        if isinstance(self.value, str):
            return f'Literal: "{self.value}"'
        return f"Literal: {self.value}"


# unary          → ( "-" | "!" ) expression ;
class UnaryExpr(Expr):
    def __init__(self, operator: Token, right: Expr):
        self.operator = operator
        self.right = right

    def __repr__(self) -> str:
        return f"Unary: [{self.operator.lexeme} {self.right}]"
