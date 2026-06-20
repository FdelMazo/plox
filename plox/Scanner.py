from typing import Callable

from .Token import Token, TokenType, TokenKeywords


class Scanner(object):
    def __init__(self, source: str):
        # nos vamos a ir guardando los tokens, que son el texto crudo acompañado de su significado
        self.tokens: list[Token] = []

        # El lexema que queremos capturar es el que esta entre el start y el current de source
        self.source = source  # la linea entera de caracteres crudos, sin significado
        self.start = 0  # caracter desde el que empezamos a leer un nuevo lexema
        self.current = 0  # caracter donde estamos parados
        self.line = 1  # linea donde estamos parados

    # Obtiene la lista de tokens escaneados
    def scan(self) -> list[Token]:
        # recorremos cada linea hasta el final
        while not self._is_at_end():
            # arranca un lexema nuevo
            self.start = self.current
            self.scan_token()

        # terminamos la lista de tokens con un EOF, para más prolijidad
        self.start = self.current
        self.add_token(TokenType.EOF)

        return self.tokens

    # ---------- Core ---------- #

    # Devuelve el lexema actual
    def lexeme(self) -> str:
        # el lexema entero es desde el inicio hasta donde estamos parados
        return self.source[self.start : self.current]

    # Agrega un token a la lista
    def add_token(self, token_type: TokenType, literal=None):
        # nos guardamos el token con el lexema actual
        self.tokens.append(
            Token(token_type, lexeme=self.lexeme(), literal=literal, line=self.line)
        )

    # Escanea un token individual
    def scan_token(self):
        # obtenemos el primer caracter
        c = self._advance()

        # para identificadores y palabras reservadas, chequeamos
        # si el primer caracter es una letra o un guion bajo,
        # y después permitimos caracteres alfanumericos tambien
        is_alpha = lambda c: str.isalpha(c) or c == "_"
        is_alphanum = lambda c: str.isalnum(c) or c == "_"

        match c:
            # descartamos los whitespaces
            case " " | "\r" | "\t":
                pass
            case "\n":
                self.line += 1

            # tokens de un solo carácter
            case "(":
                self.add_token(TokenType.LEFT_PAREN)
            case ")":
                self.add_token(TokenType.RIGHT_PAREN)
            case "{":
                self.add_token(TokenType.LEFT_BRACE)
            case "}":
                self.add_token(TokenType.RIGHT_BRACE)
            case "[":
                self.add_token(TokenType.LEFT_BRACKET)
            case "]":
                self.add_token(TokenType.RIGHT_BRACKET)
            case ",":
                self.add_token(TokenType.COMMA)
            case "-":
                self.add_token(TokenType.MINUS)
            case ";":
                self.add_token(TokenType.SEMICOLON)
            case "?":
                self.add_token(TokenType.QUESTION)
            case ":":
                self.add_token(TokenType.COLON)
            case "%":
                self.add_token(TokenType.PERCENT)
            case "/":
                # caso especial para el /
                # si es un comentario, lo ignoramos
                if self._match("/"):
                    # consumimos el resto de la linea
                    while not self._lookahead() == "\n" and not self._is_at_end():
                        self._advance()
                # si es un comentario multilinea, lo ignoramos
                # se permiten comentarios anidados de n niveles del estilo /* /* ... */ */
                elif self._match("*"):
                    level = 1
                    while level > 0 and not self._is_at_end():
                        if self._match("\n"):
                            self.line += 1
                            continue
                        if self._match("*") and self._match(
                            "/"
                        ):  # cierre de comentario
                            level -= 1
                            continue
                        if self._match("/") and self._match(
                            "*"
                        ):  # apertura de comentario
                            level += 1
                            continue
                        self._advance()
                    # si llegamos al final del archivo, sin cerrar el comentario, es un error
                    if level > 0:
                        raise Exception(f"Unterminated comment: `{self.lexeme()}`")
                else:
                    self.add_token(TokenType.SLASH)
            # tokens de uno o dos caracteres
            case "+":
                self.add_token(
                    TokenType.PLUS_PLUS if self._match("+") else TokenType.PLUS
                )
            case "*":
                self.add_token(
                    TokenType.STAR_STAR if self._match("*") else TokenType.STAR
                )
            case "!":
                self.add_token(
                    TokenType.BANG_EQUAL if self._match("=") else TokenType.BANG
                )
            case "=":
                self.add_token(
                    TokenType.EQUAL_EQUAL if self._match("=") else TokenType.EQUAL
                )
            case "<":
                self.add_token(
                    TokenType.LESS_EQUAL if self._match("=") else TokenType.LESS
                )
            case ">":
                self.add_token(
                    TokenType.GREATER_EQUAL if self._match("=") else TokenType.GREATER
                )

            case "'":
                # consumimos la cadena hasta el proximo ' o hasta el fin de linea
                self._scan_string(
                    string_eof_criteria=lambda: (
                        not self._is_at_end()
                        and not self._lookahead() == "'"
                        and not self._lookahead() == "\n"
                    ),
                    terminated_string_criteria=lambda: (
                        self._is_at_end() or self._lookahead() == "\n"
                    ),
                )

            # string multilinea
            case '"':
                self._scan_string(
                    string_eof_criteria=lambda: (
                        not self._is_at_end() and not self._lookahead() == '"'
                    ),
                    terminated_string_criteria=lambda: self._is_at_end(),
                )

            case _ if c in "0123456789":
                # consumimos el número hasta que no sea un dígito o un punto para decimales

                scanned_dots = 0  # contador de puntos escaneados

                while not self._is_at_end() and self._lookahead() in "0123456789.":
                    if self._lookahead() == ".":
                        scanned_dots += 1

                    self._advance()

                if scanned_dots > 1:
                    # un número no puede tener más de un punto decimal
                    raise Exception(f"Invalid number: `{self.lexeme()}`")

                if self._previous() == ".":
                    # un número no puede terminar en punto
                    raise Exception(f"Invalid number: `{self.lexeme()}`")

                numvalue = float(self.lexeme())
                self.add_token(TokenType.NUMBER, literal=numvalue)

            # identificadores y palabras reservadas
            case _ if is_alpha(c):
                # consumimos el identificador hasta que no sea un alfanumérico
                while not self._is_at_end() and is_alphanum(self._lookahead()):
                    self._advance()

                lexeme = self.lexeme()

                if lexeme in TokenKeywords:
                    self.add_token(TokenKeywords[lexeme])
                else:
                    self.add_token(TokenType.IDENTIFIER)

            # si no es ninguno de los anteriores, es un error
            case _:
                raise Exception(f"Unexpected character: `{c}`")

    # ---------- Helpers ---------- #

    # Devuelve si llegamos al final de la linea
    def _is_at_end(self) -> bool:
        return self.current >= len(self.source)

    # Devuelve el caracter actual, sin consumirlo
    def _lookahead(self) -> str:
        # si llegamos al final de la linea, no hay nada para mirar
        if self._is_at_end():
            return "\0"

        return self.source[self.current]

    def _lookahead_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return "\0"

        return self.source[self.current + 1]

    # Consume un caracter y lo devuelve
    def _advance(self) -> str:
        lookahead = self._lookahead()
        self.current += 1
        return lookahead

    # Devuelve el caracter anterior, ya consumido
    def _previous(self) -> str:
        return self.source[self.current - 1]

    # Devuelve si el siguiente caracter es el esperado, y lo consume
    # Es solo una combinación de advance y lookahead
    def _match(self, expected: str) -> bool:
        lookahead = self._lookahead()
        if not lookahead == expected:
            return False

        self._advance()
        return True

    def _scan_string(
        self, string_eof_criteria: Callable, terminated_string_criteria: Callable
    ):
        """
        Escanea un string hasta que se deje de cumplir "string_eof_criteria"
        Una vez que se deje de cumplir, chequea si se cumplió "terminated_string_criteria" para lanzar un error de string sin cerrar,
        o si no, consume el cierre del string y lo guarda como token.
        Maneja la interpolación de strings, que tiene la forma `${expresion}`.
        Si encuentra una interpolacion, se encarga de empaquetar el string para que los tokens queden ordenados
        de la forma [ INTERPOLATION_START, STRING, ..., INTERPOLATION_END ].
        Por ejemplo, para el caso "hola ${nombre}!", los tokens serían:
        [ INTERPOLATION_START, STRING<'hola '>, IDENTIFIER<nombre>, STRING<'!'>, INTERPOLATION_END ]
        """
        has_interpolation = False

        while string_eof_criteria():
            if self._lookahead() == "$" and self._lookahead_next() == "{":
                # Si no es la primera interpolacion, no agregamos offset al literal
                # Esto skippeaba el char despues de '}' y algo como
                # "${var} hola ${var2}" resultaba en [ INTERPOLATION_START, IDENTIFIER<var>, STRING<'hola ', IDENTIFIER<var2>, INTERPOLATION_END ]
                # Notar la falta de espacio antes de 'hola ' en STRING<'hola '>
                start_offset = 1 if not has_interpolation else 0
                str_literal = self.source[self.start + start_offset : self.current]
                self.add_token(TokenType.STRING, literal=str_literal)

                self.add_token(TokenType.INTERPOLATION_START)
                has_interpolation = True

                # Salteamos '${'
                self._advance()
                self._advance()
                self.start = self.current

                brace_depth = 1
                while brace_depth > 0 and not self._is_at_end():
                    char = self._lookahead()

                    if char == "{":
                        brace_depth += 1
                    elif char == "}":
                        brace_depth -= 1

                    if brace_depth > 0:
                        # Escaneamos los tokens contenidos dentro de la interpolacion
                        self.scan_token()
                        self.start = self.current
                    else:
                        self.add_token(TokenType.INTERPOLATION_END)
                        self._advance()
                        self.start = self.current

                if brace_depth > 0:
                    raise Exception(f"Unterminated interpolation: `{self.lexeme()}`")

                continue

            self._advance()

        if terminated_string_criteria():
            # si llegamos al final del archivo, sin cerrar la cadena, es un error
            raise Exception(f"Unterminated string: `{self.lexeme()}`")

        self._advance()  # consumimos el cierre de la cadena

        # la cadena la guardamos sin las comillas
        start_offset = 1 if not has_interpolation else 0
        strvalue = self.source[self.start + start_offset : self.current - 1]
        self.add_token(TokenType.STRING, literal=strvalue)
