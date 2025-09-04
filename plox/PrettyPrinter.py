from functools import singledispatchmethod
from typing import Callable
from .Token import Token, TokenType
from .Expr import (
    Expr,
    AssignmentExpr,
    BinaryExpr,
    CallExpr,
    GroupingExpr,
    LiteralExpr,
    LogicExpr,
    PostfixExpr,
    UnaryExpr,
    VariableExpr,
)


class PrettyPrinter:
    def __init__(self, expr: Expr):
        self._root = expr
        self._path = []

    def _make_padding(self) -> str:
        padding = []

        if self._path:
            for x in self._path[:-1]:
                if x == 1:
                    padding.append("│   ")
                else:
                    padding.append("    ")

            last = self._path[-1]
            if last == 1:
                padding.append("├── ")
            else:
                padding.append("└── ")

        return "".join(padding)

    def _pretty_token(self, token: Token) -> str:
        match token.token_type:
            case TokenType.MINUS:
                return "-"
            case TokenType.STAR:
                return "*"
            case TokenType.SLASH:
                return "/"
            case TokenType.PLUS:
                return "+"
            case TokenType.PLUS_PLUS:
                return "++"
            case TokenType.BANG:
                return "!"
            case TokenType.BANG_EQUAL:
                return "!="
            case TokenType.EQUAL_EQUAL:
                return "=="
            case TokenType.GREATER:
                return ">"
            case TokenType.GREATER_EQUAL:
                return ">="
            case TokenType.LESS:
                return "<"
            case TokenType.LESS_EQUAL:
                return "<="
            case TokenType.IDENTIFIER:
                return token.lexeme
            case TokenType.STRING:
                return token.lexeme
            case TokenType.NUMBER:
                return token.lexeme
            case TokenType.AND:
                return "and"
            case TokenType.FALSE:
                return "false"
            case TokenType.NIL:
                return "nil"
            case TokenType.OR:
                return "or"
            case TokenType.TRUE:
                return "true"

        raise RuntimeError(f"Unknown token type: `{token.token_type}`")

    @singledispatchmethod
    def _accept(self, expression: Expr) -> str:
        raise RuntimeError(f"Unknown expression type: `{type(expression)}`")

    @_accept.register
    def _(self, expression: BinaryExpr | LogicExpr) -> str:
        padding = self._make_padding()
        line = f"{padding}{self._pretty_token(expression._operator)}\n"

        self._path.append(1)
        r = self._accept(expression._right)
        self._path.pop()

        self._path.append(0)
        l = self._accept(expression._left)
        self._path.pop()

        return line + r + l

    @_accept.register
    def _(self, expression: GroupingExpr) -> str:
        return self._accept(expression._expression)

    @_accept.register
    def _(self, expression: LiteralExpr) -> str:
        padding = self._make_padding()
        return f"{padding}{expression._value}\n"

    @_accept.register
    def _(self, expression: UnaryExpr) -> str:
        padding = self._make_padding()
        line = f"{padding}{self._pretty_token(expression._operator)}\n"

        self._path.append(0)
        r = self._accept(expression._right)
        self._path.pop()

        return line + r

    @_accept.register
    def _(self, expression: CallExpr) -> str:
        padding = self._make_padding()
        name = self._accept(expression._callee)
        line = f"{padding}{name}"

        self._path.append(0)
        rest = "".join(self._accept(arg) for arg in expression._arguments)
        self._path.pop()

        return line + rest

    @_accept.register
    def _(self, expression: VariableExpr) -> str:
        padding = self._make_padding()
        return f"{padding}{self._pretty_token(expression._name)}\n"

    @_accept.register
    def _(self, expression: AssignmentExpr) -> str:
        padding = self._make_padding()
        line = f"{padding}{self._pretty_token(expression._name)}\n"

        self._path.append(0)
        rest = self._accept(expression._value)
        self._path.pop()

        return line + rest

    @_accept.register
    def _(self, expression: PostfixExpr) -> str:
        padding = self._make_padding()
        line = f"{padding}{self._pretty_token(expression._operator)}\n"

        self._path.append(0)
        l = self._accept(expression._left)
        self._path.pop()

        return line + l

    def print(self, f: Callable[[str], str] = lambda x: x):
        print(f(self._accept(self._root)))
