from enum import Enum, auto
from typing import Union

# Versión muy reducida del scaner de Lox
# solo soporta números, operadores aritméticos (+, -, *, /)
# agrupar en parentesis y comentarios (//)


class TokenType(Enum):
    MINUS = auto()
    PLUS = auto()
    STAR = auto()
    SLASH = auto()
    NUMBER = auto()
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    EOF = auto()


class Token(object):
    def __init__(
        self, token_type: TokenType, *, lexeme: str, literal: Union[float, None]
    ):
        self.token_type = token_type
        self.lexeme = lexeme
        self.literal = literal

    def __repr__(self) -> str:
        return f"{self.token_type.name} '{self.lexeme}'"


class Scanner(object):
    def __init__(self, source: str):
        self.tokens: list[Token] = []
        self._source = source
        self._start = 0
        self._current = 0

    # Obtiene la lista de tokens escaneados
    def scan(self) -> list[Token]:
        while not self._is_at_end():
            self._start = self._current
            self.scan_token()

        self._start = self._current
        self.add_token(TokenType.EOF)

        return self.tokens

    # ---------- Core ---------- #

    # Devuelve el lexema actual
    def lexeme(self) -> str:
        return self._source[self._start : self._current]

    # Agrega un token a la lista
    def add_token(self, token_type: TokenType, literal=None):
        self.tokens.append(Token(token_type, lexeme=self.lexeme(), literal=literal))

    # Escanea un token individual
    def scan_token(self):
        c = self._advance()

        match c:
            # descartamos los whitespaces y los punto y coma
            case " " | "\r" | "\t" | "\n" | ";":
                pass

            # tokens de un solo carácter
            case "(":
                self.add_token(TokenType.LEFT_PAREN)
            case ")":
                self.add_token(TokenType.RIGHT_PAREN)
            case "-":
                self.add_token(TokenType.MINUS)
            case "+":
                self.add_token(TokenType.PLUS)
            case "*":
                self.add_token(TokenType.STAR)
            case "*":
                self.add_token(TokenType.STAR)
            case "/":
                if self._match("/"):
                    while not self._is_at_end() and not self._lookahead() == "\n":
                        self._advance()
                else:
                    self.add_token(TokenType.SLASH)

            # literales
            case _ if c in "0123456789":
                while not self._is_at_end() and self._lookahead() in "0123456789.":
                    self._advance()

                value = float(self.lexeme())
                self.add_token(TokenType.NUMBER, literal=value)

            # si no es ninguno de los anteriores, es un error
            case _:
                raise Exception(f"Unexpected character: `{c}`")

    # ---------- Helpers ---------- #

    # Devuelve si llegamos al final de la linea
    def _is_at_end(self) -> bool:
        return self._current >= len(self._source)

    # Devuelve el caracter actual, sin consumirlo
    def _lookahead(self) -> str:
        # si llegamos al final de la linea, no hay nada para mirar
        if self._is_at_end():
            return "\0"

        return self._source[self._current]

    # Consume un caracter y lo devuelve
    def _advance(self) -> str:
        lookahead = self._lookahead()
        self._current += 1
        return lookahead

    # Devuelve si el siguiente caracter es el esperado, y lo consume
    # Es solo una combinación de advance y lookahead
    def _match(self, expected: str) -> bool:
        lookahead = self._lookahead()
        if not lookahead == expected:
            return False

        self._advance()
        return True
