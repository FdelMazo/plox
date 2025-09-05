from enum import Enum, auto
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


# Indica una dirección, con una lista de ellas se puede reconstruir
# el camino que atraveso el printer para llegar a cada expresión.
class Dir(Enum):
    LEFT = auto()
    RIGHT = auto()


class PrettyPrinter:
    def __init__(self, expr: Expr):
        self._path: list[Dir] = []
        self._root: Expr = expr

    # Printear por stdout el ast de forma más legible
    def print(self, f: Callable[[str], str] = lambda x: x):
        print(f(self._accept(self._root)))

    # ---------- Printers de Expresiones ---------- #

    @singledispatchmethod
    def _accept(self, expr: Expr) -> str:
        raise RuntimeError(f"Unknown expression type: `{type(expr)}`")

    @_accept.register
    def _(self, expr: BinaryExpr | LogicExpr) -> str:
        padding = self._make_padding()
        symbol = self._pretty_token(expr._operator)
        line = f"{padding}{symbol}\n"

        r = self._branch(Dir.RIGHT, lambda: self._accept(expr._right))
        l = self._branch(Dir.LEFT, lambda: self._accept(expr._left))
        return line + r + l

    @_accept.register
    def _(self, expr: GroupingExpr) -> str:
        return self._accept(expr._expression)

    @_accept.register
    def _(self, expr: LiteralExpr) -> str:
        padding = self._make_padding()
        return f"{padding}{expr._value}\n"

    @_accept.register
    def _(self, expr: UnaryExpr) -> str:
        padding = self._make_padding()
        symbol = self._pretty_token(expr._operator)
        line = f"{padding}{symbol}\n"
        return line + self._branch(Dir.LEFT, lambda: self._accept(expr._right))

    @_accept.register
    def _(self, expr: CallExpr) -> str:
        line = self._accept(expr._callee)
        args = expr._arguments
        first = rest = ""

        if args:
            first = self._branch(Dir.LEFT, lambda: self._accept(args[0]))
            rest = self._branch(
                Dir.RIGHT,
                lambda: "".join(self._accept(arg) for arg in reversed(args[1:])),
            )

        return line + rest + first

    @_accept.register
    def _(self, expr: VariableExpr) -> str:
        padding = self._make_padding()
        symbol = self._pretty_token(expr._name)
        return f"{padding}{symbol}\n"

    @_accept.register
    def _(self, expr: AssignmentExpr) -> str:
        padding = self._make_padding()
        symbol = self._pretty_token(expr._name)
        line = f"{padding}{symbol}\n"
        return line + self._branch(Dir.LEFT, lambda: self._accept(expr._value))

    @_accept.register
    def _(self, expr: PostfixExpr) -> str:
        padding = self._make_padding()
        symbol = self._pretty_token(expr._operator)
        line = f"{padding}{symbol}\n"
        return line + self._branch(Dir.LEFT, lambda: self._accept(expr._left))

    # ---------- Helpers ---------- #

    # Evalua la función pasada por parametro habiendose movido en cierta dirección
    def _branch(self, direction: Dir, f: Callable[[], str]) -> str:
        self._path.append(direction)
        s = f()
        self._path.pop()
        return s

    # Arma el padding para una cierta rama del ast
    def _make_padding(self) -> str:
        padding = []

        if self._path:
            for dir in self._path[:-1]:
                if dir == Dir.RIGHT:
                    padding.append("│   ")
                else:
                    padding.append("    ")

            last = self._path[-1]
            if last == Dir.RIGHT:
                padding.append("├── ")
            else:
                padding.append("└── ")

        return "".join(padding)

    # Devuelve una representación en string más compacta de los tokens
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
