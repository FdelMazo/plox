from functools import singledispatchmethod

from .Interpreter import Interpreter
from .Stmt import (
    Stmt,
    ExpressionStmt,
    PrintStmt,
    VarDecl,
    FunDecl,
    BlockStmt,
    IfStmt,
    WhileStmt,
    ReturnStmt,
)
from .Expr import (
    Expr,
    BinaryExpr,
    GroupingExpr,
    LiteralExpr,
    UnaryExpr,
    VariableExpr,
    AssignmentExpr,
    LogicExpr,
    CallExpr,
    TernaryExpr,
)

class VarInformation:
    def __init__(self, defined: bool, used: bool):
        # Guardamos si la variable fue definida y si fue usada
        self.defined = defined
        self.used = used 


class Resolver(object):
    def __init__(self, interpreter: Interpreter):
        # Nos guardamos un stack de scopes, para saber cuan anidados estamos
        # En cada scope tenemos una tabla que nos dice si bajo un nombre tenemos
        # una variable declarada y usada (ver VarInformation)
        self.scopes: list[dict[str, VarInformation]] = []
        # Una referencia al intérprete, para poder resolver las variables
        self.interpreter = interpreter

    def begin_scope(self):
        # Empezar un scope es apilar una tabla
        self.scopes.append({})

    def end_scope(self):
        # Terminar un scope es desapilar la tabla
        self.scopes.pop()

    def declare(self, name: str):
        # Declarar una variable es guardarla bajo False en el tope del stack
        if not self.scopes:
            return
        self.scopes[-1][name] = VarInformation(defined=False, used=False)

    def define(self, name: str):
        # Definir una variable es guardarla bajo True en el tope del stack
        if not self.scopes:
            return
        self.scopes[-1][name] = VarInformation(defined=True, used=False)

    @singledispatchmethod
    def resolve(self, arg: Stmt | Expr):
        raise NameError(f"Unknown statement or expression type: `{type(arg)}`")

    # ---------- Resolver Statements  ---------- #

    @resolve.register
    def _(self, statement: BlockStmt):
        # Los bloques arrancan su propio scope
        self.begin_scope()
        for stmt in statement._statements:
            self.resolve(stmt)
        self.end_scope()

    @resolve.register
    def _(self, statement: VarDecl):
        # Las variables se declaran en el scope actual,
        # y después de resolver su inicializador, se definen
        # Esto esta desacoplado de esta manera para que podamos atajar
        # el error donde uno hace `var x = x;`, e intenta
        # referenciar una variable que todavía no fue definida
        self.declare(statement._name.lexeme)
        if statement._initializer is not None:
            self.resolve(statement._initializer)
        self.define(statement._name.lexeme)

    @resolve.register
    def _(self, statement: FunDecl):
        # Las funciones arrancan un scope nuevo después del nombre de la función
        # fun nombre() { <scope nuevo> }
        self.declare(statement._name.lexeme)
        self.define(statement._name.lexeme)
        self.begin_scope()
        for param in statement._parameters:
            self.declare(param.lexeme)
            self.define(param.lexeme)
        for stmt in statement._body:
            self.resolve(stmt)
        self.end_scope()

    ## El resto de los statements son triviales de resolver

    @resolve.register
    def _(self, statement: ExpressionStmt):
        self.resolve(statement._expression)

    @resolve.register
    def _(self, statement: PrintStmt):
        self.resolve(statement._expression)

    @resolve.register
    def _(self, statement: ReturnStmt):
        if statement._value is not None:
            self.resolve(statement._value)

    @resolve.register
    def _(self, statement: IfStmt):
        self.resolve(statement._condition)
        self.resolve(statement._thenBranch)
        if statement._elseBranch is not None:
            self.resolve(statement._elseBranch)

    @resolve.register
    def _(self, statement: WhileStmt):
        self.resolve(statement._condition)
        self.resolve(statement._body)

    # ---------- Resolver Expresiones ---------- #

    @resolve.register
    def _(self, expression: VariableExpr):
        # Si la variable esta declarada e intenta ser referenciada antes de ser definida,
        # es decir, si su valor en la tabla es False, en vez de ser True,
        # lanzamos un error
        # Básicamente, el error frente a `var x = x;`
        if self.scopes and self.scopes[-1].get(expression._name.lexeme, None) is False:
            raise NameError(
                f"Variable `{expression._name.lexeme}` was declared but not defined"
            )

        # Luego, agregamos al intérprete la profundidad del scope
        # en la que buscar la variable referenciada, partiendo
        # desde el top del stack
        for i, scope in enumerate(reversed(self.scopes)):
            if expression._name.lexeme in scope:
                self.interpreter.resolve_depth(expression, i)

    @resolve.register
    def _(self, expression: AssignmentExpr):
        value = self.resolve(expression._value)

        # Agregamos al intérprete la profundidad del scope en la que
        # se tiene que asignar el valor de la variable
        for i, scope in enumerate(reversed(self.scopes)):
            if expression._name.lexeme in scope:
                self.interpreter.resolve_depth(expression, i)

        return value

    @resolve.register
    def _(self, expression: LiteralExpr):
        # Los literales son lo más chico que hay en el lenguaje,
        # no queda nada por resolver!
        return

    ## El resto de las resoluciones son triviales de resolver

    @resolve.register
    def _(self, expression: GroupingExpr):
        self.resolve(expression._expression)

    @resolve.register
    def _(self, expression: UnaryExpr):
        self.resolve(expression._right)

    @resolve.register
    def _(self, expression: BinaryExpr):
        self.resolve(expression._left)
        self.resolve(expression._right)

    @resolve.register
    def _(self, expression: LogicExpr):
        self.resolve(expression._left)
        self.resolve(expression._right)

    @resolve.register
    def _(self, expression: CallExpr):
        self.resolve(expression._callee)
        for arg in expression._arguments:
            self.resolve(arg)

    @resolve.register
    def _(self, expression: TernaryExpr):
        self.resolve(expression._condition)
        self.resolve(expression._true_branch)
        self.resolve(expression._false_branch)
