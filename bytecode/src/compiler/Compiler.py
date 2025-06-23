from enum import Enum
from .Scanner import Token, TokenType
from ..Chunk import Chunk, OpCode


class Precedence(Enum):
    # Ordenados de menor a mayor precedencia!
    PREC_NONE = 0
    PREC_TERM = 1  # +, -
    PREC_FACTOR = 2  # *, /
    PREC_UNARY = 3  # -
    PREC_PRIMARY = 4  # (expr), number

    # Permite hacer comparaciones entre precedencias
    def __lt__(self, other):
        return self.value < other.value

    # Obtiene la siguiente precedencia (mayor a la actual)
    def next(self):
        members = list(type(self))
        index = members.index(self)
        return members[index + 1] if index + 1 < len(members) else None


# fmt: off
PRATT: dict[TokenType, tuple[str | None, str | None, Precedence, Precedence]] = {
    # TokenType              (prefix_fn,   infix_fn,   prefix_precedence,     infix_precedence)
    # Es muy flexible! Agregar operadores es una fila nueva, y cambiár la gramática es solamente editar una celda
    TokenType.LEFT_PAREN:    ("grouping",  None,       Precedence.PREC_NONE,  Precedence.PREC_NONE),
    TokenType.RIGHT_PAREN:   (None,        None,       Precedence.PREC_NONE,  Precedence.PREC_NONE),
    TokenType.MINUS:         ("unary",     "binary",   Precedence.PREC_UNARY, Precedence.PREC_TERM),
    TokenType.PLUS:          (None,        "binary",   Precedence.PREC_NONE,  Precedence.PREC_TERM),
    TokenType.STAR:          (None,        "binary",   Precedence.PREC_NONE,  Precedence.PREC_FACTOR),
    TokenType.SLASH:         (None,        "binary",   Precedence.PREC_NONE,  Precedence.PREC_FACTOR),
    TokenType.NUMBER:        ("number",    None,       Precedence.PREC_NONE,  Precedence.PREC_NONE),
}
# fmt: on


class Compiler(object):
    def __init__(self, tokens: list[Token]):
        # Todos los tokens a compilar
        self._tokens = tokens
        # El índice del token actual
        self._current = 0
        # El chunk resultante de la compilación
        self.chunk = Chunk()

    # ---------- Core ---------- #

    # Agrega un byte al chunk
    def emit(self, byte: int):
        self.chunk.write(byte)

    # Compila una expresión completa, y emite un return final para tener de centinela
    def compile(self):
        self.expression()
        self.emit(OpCode.OP_RETURN)
        return self.chunk

    # Parsea una expresión de una precedencia mayor o igual a la pasada.
    # Es el core del algoritmo de Pratt Parsing.
    def parse(self, precedence: Precedence):
        # Usando - 5 + 3 de ejemplo

        # Consume: -
        token = self._advance()

        # Si llamamos a `parse` con un token que no es un prefijo,
        # entonces fue mal llamada. Directamente lanzamos un error
        rule = self.get_rule(token.token_type)
        if rule["prefix_fn"] is None:
            raise SyntaxError(f"Unexpected token: {token}")

        # Llama a unary, que compila el - y el 5
        rule["prefix_fn"]()

        # Ya compilamos el - 5, nos queda el + 3
        # Ahora, nos fijamos si estamos parados en una expresión infija
        while not self._is_at_end():
            # Lee: +
            next_token = self._lookahead()
            next_rule = self.get_rule(next_token.token_type)

            # Nos aseguramos de no capturar operandos que no pertenecen
            # a este nivel de precedencia
            if precedence > next_rule["infix_precedence"]:
                break

            # Consume: +
            self._advance()
            # Llama a binary que consume el + y el 3
            # Y llega al final de la expresión
            next_rule["infix_fn"]()

    # ---------- Parsers de Expresiones ---------- #

    # Parsear una expresión completa es parsear la precedencia más baja
    def expression(self):
        self.parse(Precedence.PREC_TERM)

    # Parsea un número
    def number(self):
        # El número ya fue consumido
        num = self._previous()
        if num.literal is None:
            raise SyntaxError(f"Expected a number literal, got `{num}` instead")

        # Agrega los bytes correspondientes a una operación de una constante
        constant_index = self.chunk.add_constant(num.literal)
        self.emit(OpCode.OP_CONSTANT)
        self.emit(constant_index)

    # Parsea expresiones unarias
    # Por más que el orden de lectura sea <operador><operando>,
    # emite los bytes correspondientes a <operando><operador>,
    # para que el operador se utilice sobre el tope del stack de la VM
    def unary(self):
        # El operador ya fue consumido
        operator = self._previous()

        # Obtiene la regla asociada al operador y
        # parsea lo que viene después del operador,
        # con la precedencia correspondiente
        rule = self.get_rule(operator.token_type)
        self.parse(rule["prefix_precedence"])

        match operator.token_type:
            # El menos es una operación de negación
            case TokenType.MINUS:
                self.emit(OpCode.OP_NEGATE)
            case _:
                raise SyntaxError(f"Unexpected unary operator: {operator}")

    # Parsea expresiones binarias
    # La magia es que ahora tenemos todos los operadores binarios en la misma función!
    def binary(self):
        # El operador, y el operando de la izquierda ya fueron consumidos
        operator = self._previous()

        # Obtiene la regla asociada al operador y
        # compila el operando de la derecha con el
        # nivel de precedencia siguiente al de la tabla
        # Esto es porque todos nuestros operadores binarios solo
        # operan con un nivel mayor al propio.
        # En la primera suma de 2 + 3 + 4, queremos que a la derecha
        # se parsee el 3, en vez de capturar el 3 + 4
        rule = self.get_rule(operator.token_type)
        self.parse(rule["infix_precedence"].next())

        match operator.token_type:
            case TokenType.PLUS:
                self.emit(OpCode.OP_ADD)
            case TokenType.MINUS:
                self.emit(OpCode.OP_SUBTRACT)
            case TokenType.STAR:
                self.emit(OpCode.OP_MULTIPLY)
            case TokenType.SLASH:
                self.emit(OpCode.OP_DIVIDE)
            case _:
                raise SyntaxError(f"Unexpected binary operator: {operator}")

    # El agrupamiento no produce código extra, solamente es un atajo a
    # parsear una expresión de la precedencia más baja
    def grouping(self):
        # El `(` inicial ya fue consumido,
        # solo falta la expresión dentro de los parentesis
        self.expression()

        # Si no me cruzo un `)`, lanzo un error
        if not self._match(TokenType.RIGHT_PAREN):
            raise SyntaxError(
                f"Expected ')' after grouping expression, got `{self._lookahead()}` instead"
            )

    # ---------- Helpers ---------- #

    # Dado un tipo de token, devuelve las funciones y precedencias asociadas
    def get_rule(self, token_type: TokenType) -> dict:
        try:
            prefix_fn, infix_fn, prefix_prec, infix_prec = PRATT[token_type]
        except KeyError:
            raise SyntaxError(f"Unexpected Token Type: {token_type}")

        return {
            "prefix_fn": getattr(self, prefix_fn) if prefix_fn else None,
            "infix_fn": getattr(self, infix_fn) if infix_fn else None,
            "prefix_precedence": prefix_prec,
            "infix_precedence": infix_prec,
        }

    def _is_at_end(self) -> bool:
        return self._lookahead().token_type == TokenType.EOF

    def _previous(self) -> Token:
        return self._tokens[self._current - 1]

    def _lookahead(self) -> Token:
        return self._tokens[self._current]

    def _advance(self) -> Token:
        token = self._lookahead()
        if not self._is_at_end():
            self._current += 1
        return token

    def _match(self, *token_types: TokenType) -> bool:
        for token_type in token_types:
            token = self._lookahead()
            if token.token_type == token_type:
                self._advance()
                return True

        return False
