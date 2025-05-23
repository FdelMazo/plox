from .Token import Token, TokenLiteralType


class Expr(object):
    pass


# binary         → expression operator expression ;
# operator       → "==" | "!=" | "<" | "<=" | ">" | ">=" | "+"  | "-"  | "*" | "/" ;
class BinaryExpr(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr):
        self._left = left
        self._operator = operator
        self._right = right

    def __repr__(self) -> str:
        return f"Binary: [{self._left}  {self._operator.lexeme} {self._right}]"


# grouping       → "(" expression ")" ;
class GroupingExpr(Expr):
    def __init__(self, expression: Expr):
        self._expression = expression

    def __repr__(self) -> str:
        return f"Grouping: ({self._expression})"


# literal        → NUMBER | STRING | "true" | "false" | "nil" ;
class LiteralExpr(Expr):
    def __init__(self, value: TokenLiteralType):
        self._value = value

    def __repr__(self) -> str:
        if isinstance(self._value, str):
            return f'Literal: "{self._value}"'
        return f"Literal: {self._value}"


# unary          → ( "-" | "!" ) expression ;
class UnaryExpr(Expr):
    def __init__(self, operator: Token, right: Expr):
        self._operator = operator
        self._right = right

    def __repr__(self) -> str:
        return f"Unary: [{self._operator.lexeme} {self._right}]"


# variable       → IDENTIFIER ;
class VariableExpr(Expr):
    def __init__(self, name: Token):
        self._name = name

    def __repr__(self) -> str:
        return f"Variable: {self._name.lexeme}"


# assignment    → IDENTIFIER "=" expression ;
class AssignmentExpr(Expr):
    def __init__(self, name: Token, value: Expr):
        self._name = name
        self._value = value

    def __repr__(self) -> str:
        return f"Assignment: {self._name.lexeme} = {self._value}"
