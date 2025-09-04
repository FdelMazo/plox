from functools import singledispatchmethod

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
        self.root = expr
        self.path = []

    def make_padding(self) -> str:
        padding = []

        if self.path:
            for x in self.path[:-1]:
                if x == 1:
                    padding.append("│   ")
                else:
                    padding.append("    ")

            last = self.path[-1]
            if last == 1:
                padding.append("├── ")
            else:
                padding.append("└── ")

        return "".join(padding)

    @singledispatchmethod
    def accept(self, expression: Expr) -> str:
        raise RuntimeError(f"Unknown expression type: `{type(expression)}`")

    @accept.register
    def _(self, expression: BinaryExpr) -> str:
        padding = self.make_padding()
        line = f"{padding}{expression._operator}"

        self.path.append(1)
        r = self.accept(expression._right)
        self.path.pop()

        self.path.append(0)
        l = self.accept(expression._left)
        self.path.pop()

        return line + r + l

    @accept.register
    def _(self, expression: GroupingExpr) -> str:
        return self.accept(expression._expression)

    @accept.register
    def _(self, expression: LiteralExpr) -> str:
        padding = self.make_padding()
        return f"{padding}{expression._value}"

    @accept.register
    def _(self, expression: UnaryExpr) -> str:
        padding = self.make_padding()
        line = f"{padding}{expression._operator}"

        self.path.append(0)
        r = self.accept(expression._right)
        self.path.pop()

        return line + r

    @accept.register
    def _(self, expression: CallExpr) -> str:
        padding = self.make_padding()

        line = f"{padding}{expression._callee}"

        self.path.append(0)
        rest = "".join(self.accept(arg) for arg in expression._arguments)
        self.path.pop()

        return line + rest

    @accept.register
    def _(self, expression: VariableExpr) -> str:
        padding = self.make_padding()
        return f"{padding}{expression._name}"

    @accept.register
    def _(self, expression: AssignmentExpr) -> str:
        padding = self.make_padding()
        line = f"{padding}{expression._name}"

        self.path.append(0)
        rest = self.accept(expression._value)
        self.path.pop()

        return line + rest

    @accept.register
    def _(self, expression: LogicExpr) -> str:
        padding = self.make_padding()
        line = f"{padding}{expression._operator}"

        self.path.append(1)
        r = self.accept(expression._right)
        self.path.pop()

        self.path.append(0)
        l = self.accept(expression._left)
        self.path.pop()

        return line + r + l

    @accept.register
    def _(self, expression: PostfixExpr) -> str:
        padding = self.make_padding()
        line = f"{padding}{expression._operator}"

        self.path.append(0)
        l = self.accept(expression._left)
        self.path.pop()

        return line + l

    def print(self):
        print(self.accept(self.root))
