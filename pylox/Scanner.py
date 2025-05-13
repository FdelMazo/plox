from .Token import Token, TokenType, TokenKeywords


class Scanner(object):
    def __init__(self, source: str):
        self._tokens = []  # nos vamos a ir guardando los tokens, ya con significado

        # El lexema que queremos capturar es el que esta entre el start y el current de source
        self._source = source  # la linea entera de caracteres crudos, sin significado
        self._start = 0  # caracter desde el que empezamos a leer un nuevo lexema
        self._current = 0  # caracter donde estamos parados

    # Obtiene la lista de tokens escaneados
    def tokens(self) -> list[Token]:
        # recorremos cada linea hasta el final
        while not self._is_at_end():
            # arranca un lexema nuevo
            self._start = self._current
            self._scan_token()

        # terminamos la lista de tokens con un EOF, para más prolijidad
        self._start = self._current
        self._add_token(TokenType.EOF)

        return self._tokens

    # ---------- Core ---------- #

    # Devuelve el lexema actual
    def _lexeme(self) -> str:
        # el lexema entero es desde el inicio hasta donde estamos parados
        return self._source[self._start : self._current]

    # Agrega un token a la lista
    def _add_token(self, token_type: TokenType, literal=None):
        # nos guardamos el token con el lexema actual
        self._tokens.append(Token(token_type, lexeme=self._lexeme(), literal=literal))

    # Escanea un token individual
    def _scan_token(self):
        # obtenemos el primer caracter
        c = self._advance()

        # para identificadores y palabras reservadas, chequeamos
        # si el caracter es alfanumérico o un guion bajo
        is_alpha = lambda c: str.isalpha(c) or c == "_"

        match c:
            # descartamos los whitespaces
            case " " | "\r" | "\t":
                pass

            # tokens de un solo carácter
            case "(":
                self._add_token(TokenType.LEFT_PAREN)
            case ")":
                self._add_token(TokenType.RIGHT_PAREN)
            case "{":
                self._add_token(TokenType.LEFT_BRACE)
            case "}":
                self._add_token(TokenType.RIGHT_BRACE)
            case ",":
                self._add_token(TokenType.COMMA)
            case ".":
                self._add_token(TokenType.DOT)
            case "-":
                self._add_token(TokenType.MINUS)
            case "+":
                self._add_token(TokenType.PLUS)
            case ";":
                self._add_token(TokenType.SEMICOLON)
            case "*":
                self._add_token(TokenType.STAR)
            case "/":
                # caso especial para el /
                # si es un comentario, lo ignoramos
                if self._match("/"):
                    # consumimos el resto de la linea
                    while not self._is_at_end():
                        self._advance()
                else:
                    self._add_token(TokenType.SLASH)

            # tokens de uno o dos caracteres
            case "!":
                self._add_token(
                    TokenType.BANG_EQUAL if self._match("=") else TokenType.BANG
                )
            case "=":
                self._add_token(
                    TokenType.EQUAL_EQUAL if self._match("=") else TokenType.EQUAL
                )
            case "<":
                self._add_token(
                    TokenType.LESS_EQUAL if self._match("=") else TokenType.LESS
                )
            case ">":
                self._add_token(
                    TokenType.GREATER_EQUAL if self._match("=") else TokenType.GREATER
                )

            # literales
            case '"':
                # consumimos la cadena hasta el proximo "
                while not self._is_at_end() and not self._lookahead() == '"':
                    self._advance()

                if self._is_at_end():
                    # si llegamos al final de la linea, sin cerrar la cadena, es un error
                    raise Exception(f"Unterminated string: {self._lexeme()}")

                self._advance()  # consumimos el cierre de la cadena

                # la cadena la guardamos sin las comillas
                value = self._source[self._start + 1 : self._current - 1]
                self._add_token(TokenType.STRING, literal=value)

            case _ if c in "0123456789":
                # consumimos el número hasta que no sea un dígito o un punto para decimales
                while not self._is_at_end() and self._lookahead() in "0123456789.":
                    self._advance()

                value = float(self._lexeme())
                self._add_token(TokenType.NUMBER, literal=value)

            # identificadores y palabras reservadas
            case _ if is_alpha(c):
                # consumimos el identificador hasta que no sea un alfanumérico
                while not self._is_at_end() and is_alpha(self._lookahead()):
                    self._advance()

                lexeme = self._lexeme()

                if lexeme in TokenKeywords:
                    self._add_token(TokenKeywords[lexeme])
                else:
                    self._add_token(TokenType.IDENTIFIER)

            # si no es ninguno de los anteriores, es un error
            case _:
                raise Exception(f"Unexpected character: {c}")

    # ---------- Helpers ---------- #

    # Devuelve si llegamos al final de la linea
    def _is_at_end(self) -> bool:
        return self._current >= len(self._source)

    # Devuelve los siguiente N caracteres desde el que esta parado
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
