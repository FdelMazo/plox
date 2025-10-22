from functools import singledispatchmethod

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
    PostfixExpr,
)
from .Function import Function, ReturnValue
from .Token import TokenType
from .Env import Env


class Interpreter(object):
    def __init__(self):
        self.globals = Env()
        self.env = self.globals

        # De mano del resolvedor (Resolver.py), ahora el intérprete sabe
        # a qué profundidad hay que buscar cada expresión
        # de variable o asignación.
        # Por ejemplo, saber si `print x;` tiene que buscar el x
        # en el entorno local actual (depth 0), en el entorno padre (depth 1),
        # o en el entorno global (directamente no esta en el dict).
        self.local_scope_depths: dict[VariableExpr | AssignmentExpr, int] = {}

    # Interpretar es ejecutar la lista de statements que tenemos
    def interpret(self, statements: list[Stmt]):
        for statement in statements:
            self.execute(statement)

    # Guarda la profundidad en la que buscar una variable o asignación
    # Es llamado por el resolvedor de scopes para poblar el diccionario
    # antes de la ejecución del programa
    def resolve_depth(self, expression: VariableExpr | AssignmentExpr, depth: int):
        self.local_scope_depths[expression] = depth

    # ---------- Ejecutadores de Statements ---------- #

    @singledispatchmethod
    def execute(self, statement: Stmt):
        raise RuntimeError(f"Unknown statement type: `{type(statement)}`")

    @execute.register
    def _(self, statement: ExpressionStmt):
        # Ejecutar un expression statement es solamente evaluar la expresión
        self.evaluate(statement._expression)

    @execute.register
    def _(self, statement: PrintStmt):
        # Ejecutar un print statement es evaluar la expresión e imprimir el resultado
        value = self.evaluate(statement._expression)
        print(value)

    @execute.register
    def _(self, statement: VarDecl):
        # Ejecutar una declaración de una variable es solamente agregar el binding al entorno
        if statement._initializer is not None:
            self.env.define(
                statement._name.lexeme, self.evaluate(statement._initializer)
            )
        else:
            self.env.define(statement._name.lexeme, statement._initializer)

    @execute.register
    def _(self, statement: FunDecl):
        # Ejecutar una declaración de una variable es solamente...
        # 1. Construir la función
        fun = Function(statement, self.env)
        # 2. Atarla a su nombre
        self.env.define(statement._name.lexeme, fun)

    @execute.register
    def _(self, statement: ReturnStmt):
        return_value = None
        if statement._value is not None:
            # Si hay un valor de retorno, lo evaluamos y lo lanzamos cual error
            return_value = self.evaluate(statement._value)

        raise ReturnValue(return_value)

    @execute.register
    def _(self, statement: IfStmt):
        # El if se implementa con... un if
        # Si la condición resuelve a verdadero, ejecuto el bloque del then
        # si no, ejecuto el bloque del else
        if self.is_truthy(self.evaluate(statement._condition)):
            self.execute(statement._thenBranch)
        elif statement._elseBranch is not None:
            # Si la condición es falsa y hay un bloque de else, lo ejecuto
            self.execute(statement._elseBranch)

    @execute.register
    def _(self, statement: WhileStmt):
        # El while se implementa con... un while
        while self.is_truthy(self.evaluate(statement._condition)):
            self.execute(statement._body)

    @execute.register
    def _(self, statement: BlockStmt):
        return self.execute_block(statement._statements, Env(enclosing=self.env))

    def execute_block(self, statements: list[Stmt], block_env: Env):
        # Para ejecutar un bloque de statements, tenemos que crear un nuevo entorno
        # y ejecutar los statements ahí
        # Tenemos que guardarnos el entorno del bloque, y después acordarnos de volver al previo
        previous_env = self.env
        self.env = block_env
        # Ojo con los returns! Hacemos un try/finally para asegurarnos de
        # recuperar el entorno previo pase lo que pase
        try:
            self.env = block_env
            for s in statements:
                self.execute(s)
        finally:
            self.env = previous_env

    # ---------- Evaluadores de Expresiones ---------- #

    # Evalua cualquier expresión y devuelve su valor
    @singledispatchmethod
    def evaluate(self, expression: Expr):
        raise RuntimeError(f"Unknown expression type: `{type(expression)}`")

    @evaluate.register
    def _(self, expression: VariableExpr):
        # Si la variable se encuentra en nuestro diccionario de scope local,
        # la buscamos con esa profundidad.
        if expression in self.local_scope_depths:
            depth = self.local_scope_depths[expression]
            return self.env.get(expression._name.lexeme, depth)

        # Si no, la buscamos dinámicamente en el entorno global
        return self.globals.get(expression._name.lexeme)

    @evaluate.register
    def _(self, expression: AssignmentExpr):
        value = self.evaluate(expression._value)

        # Si la variable se encuentra en nuestro diccionario de scope local,
        # la asignamos en esa profundidad.
        if expression in self.local_scope_depths:
            depth = self.local_scope_depths[expression]
            self.env.assign(expression._name.lexeme, value, depth)
            return value

        # Si no, la asignamos en el entorno global
        self.globals.assign(expression._name.lexeme, value)
        return value

    @evaluate.register
    def _(self, expression: LiteralExpr):
        # Evaluar expresiones literales es solamente devolver el valor  ya escaneado
        return expression._value

    @evaluate.register
    def _(self, expression: GroupingExpr):
        # Para evaluar expresiones agrupadas, solo hay que evaluar la expresión contenida
        return self.evaluate(expression._expression)

    @evaluate.register
    def _(self, expression: UnaryExpr):
        right = self.evaluate(expression._right)

        match expression._operator.token_type:
            case TokenType.MINUS:
                # El operador - solo funciona sobre números
                if not self.is_number(right):
                    raise RuntimeError(
                        f"Operand of - must be a number, got: `-{right}`"
                    )
                return -right
            case TokenType.BANG:
                # Negar un valor lo castea implicitamente a un booleano
                return not self.is_truthy(right)
            case _:
                raise RuntimeError(f"Unknown unary operator: `{expression._operator}`")

    @evaluate.register
    def _(self, expression: BinaryExpr):
        # En expresiones binarias, Lox evalua primero el operando
        # izquierdo, luego el derecho, y después aplicamos el operador

        # Lo mismo hacemos con el chequeo de tipos.
        # En vez de evaluar el primer operador y chequear su tipo,
        # y levantar un error antes de hacerlo con el segundo,
        # evaluamos y chequeamos todo y luego levantamos el error.
        left = self.evaluate(expression._left)
        right = self.evaluate(expression._right)

        # Es acá donde más ojo hay que poner en qué utilizamos del lenguaje de la implementación,
        # y sobre qué agregamos lógica propia.
        # Tenemos que asegurarnos de que lo que hagamos en Python sea parte de la semántica de Lox,
        # para mantenernos consistentes frente al diseño del lenguaje.
        # Si no, el riesgo es que una implementación de Lox en otro lenguaje de resultados distintos
        # frente a código de Lox.

        match expression._operator.token_type:
            # Por ejemplo, Lox no hace coerciones de tipos implicitas en la igualdad,
            # y Python tampoco. Es decir, "1" == 1 es False en ambos lenguajes.
            # Si este intérprete estuviese implementado en Ruby o JavaScript,
            # habría que estar atento a no cometer el error de utilizar el operador de igualdad
            # de ese lenguaje para el de Lox.

            # Un ejemplo donde esto no sucede. Si bien Python si nos permite comparar cadenas
            # con todos los operadores, Lox solo nos permite hacerlo con los de == y !=.
            # Es por eso que tenemos que levantar un error al intentar llamar < frente a cadenas,
            # mientras que eso en Python no sucederia.
            case TokenType.PLUS:
                # El operador + en Lox esta sobrecargado al igual que en Python.
                # Se permite sumar tanto cadenas como números.
                # Y, al igual que en Python, no hay conversión implicita entre los operandos.
                # Es decir, en Lox, "a" + 1 es un error. (en JavaScript, por ejemplo, sería "a1").
                if not self.is_number(left, right) and not self.is_string(left, right):
                    raise RuntimeError(
                        f"Operands of + must be either numbers or strings, got: `{left} + {right}`"
                    )
                return left + right
            case TokenType.MINUS:
                if not self.is_number(left, right):
                    raise RuntimeError(
                        f"Operands of - must be numbers, got: `{left} - {right}`"
                    )
                return left - right
            case TokenType.STAR:
                if not self.is_number(left, right):
                    raise RuntimeError(
                        f"Operands of * must be numbers, got: `{left} * {right}`"
                    )
                return left * right
            case TokenType.SLASH:
                if not self.is_number(left, right):
                    raise RuntimeError(
                        f"Operands of / must be numbers, got: `{left} / {right}`"
                    )
                return left / right
            case TokenType.STAR_STAR:
                if not self.is_number(left, right):
                    raise RuntimeError(
                        f"Operands of ** must be numbers, got: `{left} ** {right}`"
                    )
                return left ** right
            case TokenType.PERCENT:
                if not self.is_number(left, right):
                    raise RuntimeError(
                        f"Operands of % must be numbers, got: `{left} % {right}`"
                    )
                return left % right
            case TokenType.GREATER:
                if not self.is_number(left, right):
                    raise RuntimeError(
                        f"Operands of > must be numbers, got: `{left} > {right}`"
                    )
                return left > right
            case TokenType.GREATER_EQUAL:
                if not self.is_number(left, right):
                    raise RuntimeError(
                        f"Operands of >= must be numbers, got: `{left} >= {right}`"
                    )
                return left >= right
            case TokenType.LESS:
                if not self.is_number(left, right):
                    raise RuntimeError(
                        f"Operands of < must be numbers, got: `{left} < {right}`"
                    )
                return left < right
            case TokenType.LESS_EQUAL:
                if not self.is_number(left, right):
                    raise RuntimeError(
                        f"Operands of <= must be numbers, got: `{left} <= {right}`"
                    )
                return left <= right
            case TokenType.EQUAL_EQUAL:
                return left == right
            case TokenType.BANG_EQUAL:
                return left != right
            case _:
                raise RuntimeError(f"Unknown binary operator: `{expression._operator}`")

    @evaluate.register
    def _(self, expression: LogicExpr):
        # Tanto en el or como en el and, empezamos por evaluar el primer operando
        left = self.evaluate(expression._left)

        # En un or, si el primer operando es truthy, lo devolvemos
        # sin evaluar el segundo
        if expression._operator.token_type == TokenType.OR:
            if self.is_truthy(left):
                return left

        # En cambio, en los and, si el primer operando no es truthy,
        # ya debemos corto-circuitear y devolverlo
        if expression._operator.token_type == TokenType.AND:
            if not self.is_truthy(left):
                return left

        # En ambos casos, si no cortocircuitamos, evaluamos el segundo operando
        return self.evaluate(expression._right)

    @evaluate.register
    def _(self, expression: CallExpr):
        # Evaluamos al llamado a la función, que puede ser cualquier cosa
        callee = self.evaluate(expression._callee)

        # Evaluamos cada argumento de la llamada
        arguments = []
        for arg in expression._arguments:
            arguments.append(self.evaluate(arg))

        # Si el llamado no es una función, levantamos un error
        if not callable(callee):
            raise RuntimeError(f"Cannot call non-callable object: `{callee}`")

        # Si no se cumple la aridad, levantamos un error
        if len(arguments) != callee.arity:
            raise RuntimeError(
                f"Expected {callee.arity} arguments, got {len(arguments)}"
            )

        return callee(self, arguments)
    
    @evaluate.register
    def _(self, expression: TernaryExpr):
        condition = self.evaluate(expression._condition)
        if self.is_truthy(condition):
            # si condition es truthy, evaluamos la rama verdadera
            return self.evaluate(expression._true_branch)
        
        # si condition es falsy, evaluamos la rama falsa
        return self.evaluate(expression._false_branch)
    
    @evaluate.register
    def _(self, expression: PostfixExpr):
        left = expression._left

        # definimos funciones lambda para obtener el valor viejo y asignar el nuevo
        if left in self.local_scope_depths: # si la variable se encuentra en nuestro diccionario de scope local, la buscamos y asignamos con esa profundidad
            depth = self.local_scope_depths[left]
            get_value = lambda: self.env.get(left._name.lexeme, depth)
            assign_value = lambda new_value: self.env.assign(left._name.lexeme, new_value, depth)
        else: # en caso contrario, la buscamos y asignamos dinámicamente en el entorno global
            get_value = lambda: self.globals.get(left._name.lexeme)
            assign_value = lambda new_value: self.globals.assign(left._name.lexeme, new_value)

        old_value = get_value() # la funcion lambda para obtener el valor viejo depende de si la variable se encuentra en nuestro diccionario de scope local o no

        # el operador ++ solo funciona sobre números
        if not self.is_number(old_value):
            raise RuntimeError(f"Operand of ++ must be a number, got: `{old_value}++`")

        new_value = old_value + 1
        assign_value(new_value) # la funcion lambda para asignar el valor nuevo depende de si la variable se encuentra en nuestro diccionario de scope local o no

        # devolvemos el valor viejo
        return old_value

    # ---------- Helpers ---------- #

    # Devuelve si el valor es truthy (es decir, si evalua a verdadero)
    def is_truthy(self, value):
        # Lox mantiene la semántica de Ruby:
        # false y nil son falsy, el resto son truthy
        if value is None or value is False:
            return False
        return True

    # Devuelve si los valores recibidos son un número según Lox
    def is_number(self, *values):
        return all(isinstance(value, (int, float)) for value in values)

    # Devuelve si los valores recibidos son una cadena según Lox
    def is_string(self, *values):
        return all(isinstance(value, str) for value in values)
