class TokenType:
    ( # tokens de un solo carácter
    LEFT_PAREN, RIGHT_PAREN, LEFT_BRACE, RIGHT_BRACE,
    COMMA, DOT, MINUS, PLUS, SEMICOLON, STAR,
    # en particular, el / es un token de un solo caracter, pero tambien puede
    # ser el comienzo de un comentario cuando es //
    # en ese caso, debe ser descartado por el scanner
    SLASH,

    # tokens de uno o dos caracteres
    BANG, BANG_EQUAL, EQUAL, EQUAL_EQUAL,
    GREATER, GREATER_EQUAL, LESS, LESS_EQUAL,

    # literales
    IDENTIFIER, STRING, NUMBER,

    # palabras clave
    AND, ELSE, FALSE, FUN, FOR, IF, NIL, OR,
    PRINT, RETURN, SUPER, THIS, TRUE, VAR, WHILE,

    # fin de archivo
    EOF) = range(38)

class Token(object):
    def __init__(self, token: TokenType, *, lexeme: str, literal: object):
        self._lexeme = lexeme  # Los caracteres en sí, ya con significado
        self._token = token  # Que token es
        self._literal = literal  # Si es un literal, aprovechamos y nos almacenamos directamente el valor al que resuelve

    def __repr__(self) -> str:
        # IDEA: incluir el token type en vez del número
        return str(self.__dict__)

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
    "super": TokenType.SUPER,
    "this": TokenType.THIS,
    "true": TokenType.TRUE,
    "var": TokenType.VAR,
    "while": TokenType.WHILE
}
