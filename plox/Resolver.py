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
)


class Resolver(object):
    def __init__(self, interpreter: Interpreter):
        # Nos guardamos un stack de scopes, para saber cuan anidados estamos
        # En cada scope tenemos una tabla que nos dice si bajo un nombre tenemos
        # una variable solo declarada (False) o ya definida (True)
        self.scopes: list[dict[str, bool]] = []
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
        self.scopes[-1][name] = False

    def define(self, name: str):
        # Definir una variable es guardarla bajo True en el tope del stack
        if not self.scopes:
            return
        self.scopes[-1][name] = True

    @singledispatchmethod
    def resolve(self, arg: Stmt | Expr):
        raise NameError(f"Unknown statement or expression type: `{type(arg)}`")

    # ---------- Resolver Statements  ---------- #

    @resolve.register
    def _(self, statement: BlockStmt):
        # Los bloques arrancan su propio scope
        self.begin_scope()
        for stmt in statement.statements:
            self.resolve(stmt)
        self.end_scope()

    @resolve.register
    def _(self, statement: VarDecl):
        # Las variables se declaran en el scope actual,
        # y después de resolver su inicializador, se definen
        # Esto esta desacoplado de esta manera para que podamos atajar
        # el error donde uno hace `var x = x;`, e intenta
        # referenciar una variable que todavía no fue definida
        self.declare(statement.name.lexeme)
        if statement.initializer is not None:
            self.resolve(statement.initializer)
        self.define(statement.name.lexeme)

    @resolve.register
    def _(self, statement: FunDecl):
        # Las funciones arrancan un scope nuevo después del nombre de la función
        # fun nombre() { <scope nuevo> }
        self.declare(statement.name.lexeme)
        self.define(statement.name.lexeme)
        self.begin_scope()
        for param in statement.parameters:
            self.declare(param.lexeme)
            self.define(param.lexeme)
        for stmt in statement.body:
            self.resolve(stmt)
        self.end_scope()

    ## El resto de los statements son triviales de resolver

    @resolve.register
    def _(self, statement: ExpressionStmt):
        self.resolve(statement.expression)

    @resolve.register
    def _(self, statement: PrintStmt):
        self.resolve(statement.expression)

    @resolve.register
    def _(self, statement: ReturnStmt):
        if statement.value is not None:
            self.resolve(statement.value)

    @resolve.register
    def _(self, statement: IfStmt):
        self.resolve(statement.condition)
        self.resolve(statement.thenBranch)
        if statement.elseBranch is not None:
            self.resolve(statement.elseBranch)

    @resolve.register
    def _(self, statement: WhileStmt):
        self.resolve(statement.condition)
        self.resolve(statement.body)

    # ---------- Resolver Expresiones ---------- #

    @resolve.register
    def _(self, expression: VariableExpr):
        # Si la variable esta declarada e intenta ser referenciada antes de ser definida,
        # es decir, si su valor en la tabla es False, en vez de ser True,
        # lanzamos un error
        # Básicamente, el error frente a `var x = x;`
        if self.scopes and self.scopes[-1].get(expression.name.lexeme, None) is False:
            raise NameError(
                f"Variable `{expression.name.lexeme}` was declared but not defined"
            )

        # Luego, agregamos al intérprete la profundidad del scope
        # en la que buscar la variable referenciada, partiendo
        # desde el top del stack
        for i, scope in enumerate(reversed(self.scopes)):
            if expression.name.lexeme in scope:
                self.interpreter.resolve_depth(expression, i)

    @resolve.register
    def _(self, expression: AssignmentExpr):
        value = self.resolve(expression.value)

        # Agregamos al intérprete la profundidad del scope en la que
        # se tiene que asignar el valor de la variable
        for i, scope in enumerate(reversed(self.scopes)):
            if expression.name.lexeme in scope:
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
        self.resolve(expression.expression)

    @resolve.register
    def _(self, expression: UnaryExpr):
        self.resolve(expression.right)

    @resolve.register
    def _(self, expression: BinaryExpr):
        self.resolve(expression.left)
        self.resolve(expression.right)

    @resolve.register
    def _(self, expression: LogicExpr):
        self.resolve(expression.left)
        self.resolve(expression.right)

    @resolve.register
    def _(self, expression: CallExpr):
        self.resolve(expression.callee)
        for arg in expression.arguments:
            self.resolve(arg)
