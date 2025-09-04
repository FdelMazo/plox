from ast import Expr
from plox.Expr import (
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

    def accept_binary(self, expr: BinaryExpr) -> str:
        padding = self.make_padding()
        s = f"{padding}{expr._operator}"

        self.path.append(1)
        l = expr._right.accept(self)

        return ""

    def accept_grouping(self, expr: GroupingExpr) -> str:
        return ""

    def accept_literal(self, expr: LiteralExpr):
        return ""

    def accept_unary(self, expr: UnaryExpr):
        return ""

    def accept_call(self, expr: CallExpr):
        return ""

    def accept_variable(self, expr: VariableExpr):
        return ""

    def accept_assignment(self, expr: AssignmentExpr):
        return ""

    def accept_logic(self, expr: LogicExpr):
        return ""

    def accept_postfix(self, expr: PostfixExpr):
        return ""

    def print(self):
        print(a := self.root.accept(self))
