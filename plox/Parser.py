from .Token import Token, TokenType
from .Expr import Expr, BinaryExpr, GroupingExpr, LiteralExpr, UnaryExpr


class Parser(object):
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens  # la lista de tokens ya escaneados
        self.current = 0  # el token en el que estamos parados

    # Obtiene expresion parseada
    def parse(self) -> Expr:
        return self.expression()

    # ---------- Reglas de Producción ---------- #

    # expression     → equality ;
    def expression(self) -> Expr:
        if self._is_at_end():
            # Si no tenemos tokens, devolvemos Nil
            return LiteralExpr(None)
        return self.equality()

    # equality       → comparison ( ( "!=" | "==" ) comparison )* ;
    def equality(self) -> Expr:
        expr = self.comparison()

        # mientras nos crucemos != o ==, seguimos parseando
        # la secuencia de igualdades
        while not self._is_at_end() and self._match(
            TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL
        ):
            operator = self._previous()
            right = self.comparison()
            expr = BinaryExpr(expr, operator, right)

        return expr

    # comparison     → term ( ( ">" | ">=" | "<" | "<=" ) term )* ;
    def comparison(self) -> Expr:
        expr = self.term()

        # mientras nos crucemos >, >=, < o <=, seguimos parseando
        # la secuencia de comparadores
        while not self._is_at_end() and self._match(
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
        ):
            operator = self._previous()
            right = self.term()
            expr = BinaryExpr(expr, operator, right)

        return expr

    # term           → factor ( ( "-" | "+" ) factor )* ;
    def term(self) -> Expr:
        expr = self.factor()

        # mientras nos crucemos - o +, seguimos parseando
        # la secuencia de sumas o restas
        while not self._is_at_end() and self._match(TokenType.MINUS, TokenType.PLUS):
            operator = self._previous()
            right = self.factor()
            expr = BinaryExpr(expr, operator, right)

        return expr

    # factor         → unary ( ( "/" | "*" ) unary )* ;
    def factor(self) -> Expr:
        expr = self.unary()

        # mientras nos crucemos * o /, seguimos parseando
        # la secuencia de multiplicaciones o divisiones
        while not self._is_at_end() and self._match(TokenType.STAR, TokenType.SLASH):
            operator = self._previous()
            right = self.unary()
            expr = BinaryExpr(expr, operator, right)

        return expr

    # unary          → ( "!" | "-" ) unary | primary ;
    def unary(self) -> Expr:
        # a diferencia de las reglas de expresiones binarias,
        # acá el operador es un prefijo.
        # primero chequeamos el operador, y después seguimos
        if self._match(TokenType.BANG, TokenType.MINUS):
            operator = self._previous()
            right = self.unary()
            return UnaryExpr(operator, right)

        # Si no tuve recursividad de unarios, entonces tengo un primario
        return self.primary()

    # primary        → NUMBER | STRING | "true" | "false" | "nil" | "(" expression ")" ;
    def primary(self) -> Expr:
        # Si es un token literal, lo convertimos en una expresión literal
        if self._match(TokenType.FALSE):
            return LiteralExpr(False)
        if self._match(TokenType.TRUE):
            return LiteralExpr(True)
        if self._match(TokenType.NIL):
            return LiteralExpr(None)

        # Si es un token literal, lo convertimos en una expresión literal con el valor del token
        if self._match(TokenType.NUMBER, TokenType.STRING):
            return LiteralExpr(self._previous().literal)

        # Si me cruzo un parentesis abierto, quiero parsear la expresion que contiene y
        # si o si cerrar el parentesis. Si no aparece ese parentesis de cierre, tengo un error
        if self._match(TokenType.LEFT_PAREN):
            expr = self.expression()
            if not self._match(TokenType.RIGHT_PAREN):
                raise SyntaxError(
                    f"Expected ')' after expression, got `{self._lookahead()}` instead"
                )
            return GroupingExpr(expr)

        # Si llegué aca sin matchear ningun otro token, entonces
        # me quede colgado esperando una expresion del usuario
        raise SyntaxError(f"Expected expression, got `{self._lookahead()}` instead")

    # ---------- Helpers ---------- #

    # Devuelve si llegamos al token EOF
    def _is_at_end(self) -> bool:
        return self._lookahead().token_type == TokenType.EOF

    # Devuelve el token anterior, ya consumido
    def _previous(self) -> Token:
        return self.tokens[self.current - 1]

    # Devuelve el token actual, sin consumirlo
    def _lookahead(self) -> Token:
        return self.tokens[self.current]

    # Consume un token y lo devuelve
    def _advance(self) -> Token:
        token = self._lookahead()
        if not self._is_at_end():
            self.current += 1

        return token

    # Devuelve si el siguiente token es cualquiera de los esperados, y lo consume
    # Es solo una combinación de advance y check
    # Como estamos tomando decisiones en base a los tokens que se vienen,
    # este parser se clasifica como un parser predictivo
    def _match(self, *token_types: TokenType) -> bool:
        for token_type in token_types:
            token = self._lookahead()
            if token.token_type == token_type:
                self._advance()
                return True

        return False
