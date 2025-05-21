from .Expr import Expr, BinaryExpr, GroupingExpr, LiteralExpr, UnaryExpr
from .Token import TokenType


class Interpreter(object):
    def __init__(self):
        pass

    # Interpretar expresiones es evaluarlas e imprimir el resultado
    def interpret(self, expression: Expr):
        value = self.evaluate(expression)
        print(value)

    # ---------- Evaluadores de Expresiones ---------- #

    # Evalua cualquier expresión y devuelve su valor
    def evaluate(self, expression: Expr):
        if isinstance(expression, LiteralExpr):
            # Evaluar literales es tan sencillo que ni requiere su propio método
            return expression._value
        elif isinstance(expression, GroupingExpr):
            # Para evaluar expresiones agrupadas, solo hay que evaluar la expresión
            # que contiene
            return self.evaluate(expression._expression)
        elif isinstance(expression, UnaryExpr):
            return self.evaluate_unary(expression)
        elif isinstance(expression, BinaryExpr):
            return self.evaluate_binary(expression)
        else:
            raise RuntimeError(f"Unknown expression type: `{type(expression)}`")

    # Evalua expresiones unarias
    def evaluate_unary(self, expression: UnaryExpr):
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

    # Evalua expresiones binarias
    def evaluate_binary(self, expression: BinaryExpr):
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
