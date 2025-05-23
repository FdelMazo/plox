from .Token import Token, TokenType
from .Expr import (
    Expr,
    BinaryExpr,
    GroupingExpr,
    LiteralExpr,
    UnaryExpr,
    VariableExpr,
    AssignmentExpr,
)
from .Stmt import Stmt, PrintStmt, ExpressionStmt, BlockStmt, VarDecl


class Parser(object):
    def __init__(self, tokens: list[Token]):
        self._tokens = tokens  # la lista de tokens ya escaneados
        self._current = 0  # el token en el que estamos parados

    # Obtiene la lista de statements parseados
    def parse(self) -> list[Stmt]:
        statements = []
        while not self._is_at_end():
            statements.append(self.statement())
        return statements

    # ---------- Reglas de Producción de Statements ---------- #

    # statement      → exprStmt | printStmt | varDecl | blockStmt ;
    def statement(self) -> Stmt:
        # si me cruzo un var, parseo una variable declaration
        if self._match(TokenType.VAR):
            return self.variable_declaration()

        # si me cruzo una llave, busco un block statement
        if self._match(TokenType.LEFT_BRACE):
            return self.block_statement()

        # si me cruzo un print, parseo un print statement
        if self._match(TokenType.PRINT):
            return self.print_statement()

        # si no, parseo una statement de expresión
        return self.expression_statement()

    # exprStmt       → expression ";" ;
    def expression_statement(self) -> Stmt:
        expr = self.expression()

        # los statements terminan sí o sí con un punto y coma
        if not self._match(TokenType.SEMICOLON):
            raise SyntaxError(
                f"Expected ';' after expression, got `{self._lookahead()}` instead"
            )

        return ExpressionStmt(expr)

    # printStmt      → "print" expression ";" ;
    def print_statement(self) -> Stmt:
        value = self.expression()

        # los statements terminan sí o sí con un punto y coma
        if not self._match(TokenType.SEMICOLON):
            raise SyntaxError(
                f"Expected ';' after value to print, got `{self._lookahead()}` instead"
            )

        return PrintStmt(value)

    # blockStmt       → "{" statement* "}" ;
    def block_statement(self) -> Stmt:
        statements = []
        while (
            not self._is_at_end()
            and self._lookahead().token_type is not TokenType.RIGHT_BRACE
        ):
            statements.append(self.statement())

        if not self._match(TokenType.RIGHT_BRACE):
            raise SyntaxError(
                f"Expected '}}' after block statement, got `{self._lookahead()}` instead"
            )

        return BlockStmt(statements)

    # varDecl        → "var" IDENTIFIER ( "=" expression )? ";" ;
    def variable_declaration(self) -> Stmt:
        if not self._match(TokenType.IDENTIFIER):
            raise SyntaxError(
                f"Expected variable declaration, got `{self._lookahead()}` instead"
            )

        variable_name = self._previous()

        # Si no se especifica un valor para la variable, se le asigna Nil
        if self._match(TokenType.EQUAL):  # var x = valor;
            variable_value = self.expression()
        else:  # var x;
            variable_value = None

        # los statements terminan sí o sí con un punto y coma
        if not self._match(TokenType.SEMICOLON):
            raise SyntaxError(
                f"Expected ';' after variable declaration, got `{self._lookahead()}` instead"
            )

        return VarDecl(variable_name, variable_value)

    # ---------- Reglas de Producción de Expresiones ---------- #

    # expression     → assignment ;
    def expression(self) -> Expr:
        return self.assignment()

    # assignment     → IDENTIFIER "=" assignment | equality ;
    def assignment(self) -> Expr:
        expr = self.equality()

        # Solo se puede asignar sobre variables. Si no, es un error
        if self._match(TokenType.EQUAL):
            if not isinstance(expr, VariableExpr):
                raise SyntaxError(
                    f"Invalid assignment target, got `{self._lookahead()}` instead"
                )

            value = self.assignment()
            return AssignmentExpr(expr._name, value)

        return expr

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

    # primary        → NUMBER | STRING | "true" | "false" | "nil" | "(" expression ")" | IDENTIFIER ;
    # Nuestro átomo más chico es un literal, un identificador, o una expresión entre paréntesis
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

        # Si es un token de un identificador, lo convertimos en una expresión de una variable
        if self._match(TokenType.IDENTIFIER):
            return VariableExpr(self._previous())

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
        return self._tokens[self._current - 1]

    # Devuelve el token actual, sin consumirlo
    def _lookahead(self) -> Token:
        return self._tokens[self._current]

    # Consume un token y lo devuelve
    def _advance(self) -> Token:
        token = self._lookahead()
        if not self._is_at_end():
            self._current += 1

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
