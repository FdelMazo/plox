from enum import Enum, auto
from typing import Union


class TokenType(Enum):
    # tokens de un solo carácter
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    LEFT_BRACE = auto()
    RIGHT_BRACE = auto()
    COMMA = auto()
    MINUS = auto()
    SEMICOLON = auto()
    STAR = auto()
    PERCENT = auto()

    # en particular, el / es un token de un solo caracter, pero tambien puede
    # ser el comienzo de un comentario cuando es //
    # en ese caso, debe ser descartado por el scanner
    SLASH = auto()

    # tokens de uno o dos caracteres
    PLUS = auto()
    PLUS_PLUS = auto()
    BANG = auto()
    BANG_EQUAL = auto()
    EQUAL = auto()
    EQUAL_EQUAL = auto()
    GREATER = auto()
    GREATER_EQUAL = auto()
    LESS = auto()
    LESS_EQUAL = auto()
    QUESTION = auto()
    COLON = auto()
    STAR_STAR = auto()

    # literales
    IDENTIFIER = auto()
    STRING = auto()
    NUMBER = auto()

    # palabras clave
    AND = auto()
    ELSE = auto()
    FALSE = auto()
    FUN = auto()
    FOR = auto()
    IF = auto()
    NIL = auto()
    OR = auto()
    PRINT = auto()
    RETURN = auto()
    TRUE = auto()
    VAR = auto()
    WHILE = auto()

    # fin de archivo
    EOF = auto()


# Los literales admitidos son numeros, cadenas, true, false y null
TokenLiteralType = Union[float, str, bool, None]


class Token(object):
    def __init__(
        self,
        token_type: TokenType,
        *,
        lexeme: str,
        literal: TokenLiteralType,
        line: int,
    ):
        self.token_type = token_type  # Que tipo de token es
        self.lexeme = lexeme  # Los caracteres en sí, crudos
        self.literal = literal  # Si es un literal, aprovechamos y nos almacenamos directamente el valor al que resuelve
        self.line = line  # Numero de linea donde se encuentra el caracter para devolver errores mas especificos

    def __repr__(self) -> str:
        if self.token_type == TokenType.IDENTIFIER:
            return f"{self.token_type.name}<{self.lexeme}>"

        return (
            f"{self.token_type.name}"
            if self.literal is None
            else f"{self.token_type.name}<{self.literal}>"
        )


TokenKeywords = {
    "and": TokenType.AND,
    "else": TokenType.ELSE,
    "false": TokenType.FALSE,
    "fun": TokenType.FUN,
    "for": TokenType.FOR,
    "if": TokenType.IF,
    "nil": TokenType.NIL,
    "or": TokenType.OR,
    "print": TokenType.PRINT,
    "return": TokenType.RETURN,
    "true": TokenType.TRUE,
    "var": TokenType.VAR,
    "while": TokenType.WHILE,
}
