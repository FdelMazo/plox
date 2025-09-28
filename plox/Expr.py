from .Token import Token, TokenLiteralType


class Expr(object):
    pass


# binary         → expression operator expression ;
# operator       → "==" | "!=" | "<" | "<=" | ">" | ">=" | "+"  | "-"  | "*" | "/" | "%" ;
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


# call          → primary "(" arguments? ")" ;
# arguments     → expression ("," expression)* ;
class CallExpr(Expr):
    def __init__(self, callee: Expr, arguments: list[Expr]):
        self._callee = callee
        self._arguments = arguments

    def __repr__(self) -> str:
        args = ", ".join(str(arg) for arg in self._arguments)
        return f"Function Call: {self._callee}({args})"


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


# logic         → expression (("and" | "or") expression )* ;
class LogicExpr(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr):
        self._left = left
        self._operator = operator
        self._right = right

    def __repr__(self) -> str:
        return f"Logic: [{self._left}  {self._operator.lexeme} {self._right}]"


# postfix         → expression "++" ;
class PostfixExpr(Expr):
    def __init__(self, left: Expr, operator: Token):
        self._left = left
        self._operator = operator

    def __repr__(self) -> str:
        return f"Postfix: [{self._left} {self._operator.lexeme}]"

# ternary        → expresion "?" expression ":" expression ;
class TernaryExpr(Expr):
    def __init__(self, condition: Expr, true_branch: Expr, false_branch: Expr):
        self._condition = condition
        self._true_branch = true_branch
        self._false_branch = false_branch

    def __repr__(self) -> str:
        return f"Ternary: [{self._condition} ? {self._true_branch} : {self._false_branch}]"