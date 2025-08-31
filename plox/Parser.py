from .Token import Token, TokenType
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
)
from .Stmt import (
    Stmt,
    PrintStmt,
    ExpressionStmt,
    BlockStmt,
    VarDecl,
    FunDecl,
    IfStmt,
    WhileStmt,
    ReturnStmt,
)


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

    # statement      → exprStmt | printStmt | varDecl | funDecl | blockStmt | ifStmt | whileStmt | forStmt ;
    def statement(self) -> Stmt:
        # si me cruzo un var, parseo una variable declaration
        if self._match(TokenType.VAR):
            return self.variable_declaration()

        # si me cruzo un fun, parseo una function declaration
        if self._match(TokenType.FUN):
            return self.function_declaration()

        # si me cruzo un return, parseo un return statement
        if self._match(TokenType.RETURN):
            return self.return_statement()

        # si me cruzo un if, parseo un if statement
        if self._match(TokenType.IF):
            return self.if_statement()

        # si me cruzo un while, parseo un while statement
        if self._match(TokenType.WHILE):
            return self.while_statement()

        # si me cruzo un for, parseo un for statement
        if self._match(TokenType.FOR):
            return self.for_statement()

        # si me cruzo una llave, busco un block statement
        if self._match(TokenType.LEFT_BRACE):
            return self.block_statement()

        # si me cruzo un print, parseo un print statement
        if self._match(TokenType.PRINT):
            return self.print_statement()

        # si no, parseo una statement de expresión
        return self.expression_statement()

    # exprStmt       → expression ";" ;
    def expression_statement(self) -> ExpressionStmt:
        expr = self.expression()

        # los statements terminan sí o sí con un punto y coma
        if not self._match(TokenType.SEMICOLON):
            raise SyntaxError(
                f"Expected ';' after expression, got `{self._lookahead()}` instead"
            )

        return ExpressionStmt(expr)

    # printStmt      → "print" expression ";" ;
    def print_statement(self) -> PrintStmt:
        value = self.expression()

        # los statements terminan sí o sí con un punto y coma
        if not self._match(TokenType.SEMICOLON):
            raise SyntaxError(
                f"Expected ';' after value to print, got `{self._lookahead()}` instead"
            )

        return PrintStmt(value)

    # blockStmt       → "{" statement* "}" ;
    def block_statement(self) -> BlockStmt:
        return BlockStmt(self.block())

    # Parsea una lista de statements hasta el siguiente }
    # sin agregarle la semántica de que es un statement de bloque:
    # de eso se ocupa el llamador
    def block(self) -> list[Stmt]:
        statements = []
        while (
            not self._is_at_end()
            and self._lookahead().token_type is not TokenType.RIGHT_BRACE
        ):
            statements.append(self.statement())

        if not self._match(TokenType.RIGHT_BRACE):
            raise SyntaxError(
                f"Expected '}}' after statements, got `{self._lookahead()}` instead"
            )

        return statements

    # whileStmt     → "while" "(" expression ")" statement ;
    def while_statement(self) -> WhileStmt:
        # Después de un while, espero un paréntesis abierto
        if not self._match(TokenType.LEFT_PAREN):
            raise SyntaxError(
                f"Expected '(' after 'while', got `{self._lookahead()}` instead"
            )

        condition = self.expression()

        # Tengo que cerrar el paréntesis abierto
        if not self._match(TokenType.RIGHT_PAREN):
            raise SyntaxError(
                f"Expected ')' after condition, got `{self._lookahead()}` instead"
            )

        body = self.statement()

        return WhileStmt(condition, body)

    # ifStmt        → "if" "(" expression ")" statement ( "else" statement )? ;
    def if_statement(self) -> IfStmt:
        # Después de un if, espero un paréntesis abierto
        if not self._match(TokenType.LEFT_PAREN):
            raise SyntaxError(
                f"Expected '(' after 'if', got `{self._lookahead()}` instead"
            )

        condition = self.expression()

        # Tengo que cerrar el paréntesis abierto
        if not self._match(TokenType.RIGHT_PAREN):
            raise SyntaxError(
                f"Expected ')' after condition, got `{self._lookahead()}` instead"
            )

        then_branch = self.statement()

        # Si me cruzo un else, parseo el statement que sigue
        if self._match(TokenType.ELSE):
            else_branch = self.statement()
        else:
            else_branch = None

        return IfStmt(condition, then_branch, else_branch)

    # forStmt        → "for" "(" ( varDecl | expressionStmt | ";") expression? ";" expression? ")" statement ;
    def for_statement(self) -> Stmt:
        # El for se compone de 3 cláusulas: un inicializador, una condición y un incremento
        # Y estas 3 cláusulas son opcionales!

        # En vez de agregar un statement a nuestra gramática, vamos a reutilizar lo que ya tenemos:
        # implementamos el for como un syntactic sugar de un while.
        # Parseamos el inicializador, la condición y el incremento, y los agrupamos en un bloque que sea
        # { inicializador; while (condición) { cuerpo; incremento; } }

        # Después de un for, espero un paréntesis abierto
        if not self._match(TokenType.LEFT_PAREN):
            raise SyntaxError(
                f"Expected '(' after 'for', got `{self._lookahead()}` instead"
            )

        initializer: None | VarDecl | ExpressionStmt = None
        # Si ya me cruzo un punto y coma, me saltee el inicializaodr
        if self._match(TokenType.SEMICOLON):
            initializer = None
        elif self._match(TokenType.VAR):
            initializer = self.variable_declaration()
        else:
            initializer = self.expression_statement()

        # Después del inicializador, espero una expresión de condicion, y un ;
        if not self._lookahead().token_type == TokenType.SEMICOLON:
            condition = self.expression()
        else:
            condition = None
        if not self._match(TokenType.SEMICOLON):
            raise SyntaxError(
                f"Expected ';' after for loop condition, got `{self._lookahead()}` instead"
            )

        # Y después de la condición, espero una expresión de incremento, y un )
        if not self._lookahead().token_type == TokenType.RIGHT_PAREN:
            increment = self.expression()
        else:
            increment = None
        if not self._match(TokenType.RIGHT_PAREN):
            raise SyntaxError(
                f"Expected ')' after for loop clauses, got `{self._lookahead()}` instead"
            )

        # Tomamos el cuerpo del form
        body = self.statement()

        # Si tengo un incremento, lo agrego al final del cuerpo que voy a ejecutar en cada iteración
        if increment is not None:
            body = BlockStmt([body, ExpressionStmt(increment)])

        # Si no tengo una condición, la reemplazo por un literal que siempre evalue a verdadero
        if condition is None:
            condition = LiteralExpr(True)

        body = WhileStmt(condition, body)

        # Si tengo un inicializador, entonces reemplazo los statements que tengo por un
        # bloque que arranque por el inicializador, y después interprete el while
        if initializer is not None:
            body = BlockStmt([initializer, body])

        return body

    # returnStmt     → "return" expression? ";" ;
    def return_statement(self) -> ReturnStmt:
        value = None

        # Si no me cruzo un punto y coma, parseo la expresión que me
        # da el valor de retorno
        if not self._lookahead().token_type == TokenType.SEMICOLON:
            value = self.expression()

        # Después de eso, si o sí tengo que encontrar un punto y coma
        if not self._match(TokenType.SEMICOLON):
            raise SyntaxError(
                f"Expected ';' after return statement, got `{self._lookahead()}` instead"
            )

        return ReturnStmt(value)

    # funDecl        → "fun" IDENTIFIER "(" parameters? ")" blockStmt ;
    def function_declaration(self) -> FunDecl:
        # Después del fun, viene el nombre de la función
        if not self._match(TokenType.IDENTIFIER):
            raise SyntaxError(
                f"Expected function declaration, got `{self._lookahead()}` instead"
            )

        function_name = self._previous()
        parameters: list[Token] = []

        # Después del nombre de la función, vienen los argumentos entre paréntesis
        if not self._match(TokenType.LEFT_PAREN):
            raise SyntaxError(
                f"Expected '(' after function name, got `{self._lookahead()}` instead"
            )

        # Mientras no me cruce un paréntesis de cierre, sigo parseando argumentos
        while (
            not self._is_at_end()
            and self._lookahead().token_type != TokenType.RIGHT_PAREN
        ):
            if not self._match(TokenType.IDENTIFIER):
                raise SyntaxError(
                    f"Expected parameter name, got `{self._lookahead()}` instead"
                )

            parameters.append(self._previous())

            # Si me cruzo una coma, sigo parseando parámetros
            if not self._match(TokenType.COMMA):
                break

        # Si no me cruce un paréntesis de cierre, tengo un error
        if not self._match(TokenType.RIGHT_PAREN):
            raise SyntaxError(
                f"Expected ')' after function parameters, got `{self._lookahead()}` instead"
            )

        # Después de los parámetros, viene el cuerpo de la función
        if not self._match(TokenType.LEFT_BRACE):
            raise SyntaxError(
                f"Expected '{{' after function parameters, got `{self._lookahead()}` instead"
            )

        body = self.block()
        return FunDecl(function_name, parameters, body)

    # varDecl        → "var" IDENTIFIER ( "=" expression )? ";" ;
    def variable_declaration(self) -> VarDecl:
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

    # assignment     → IDENTIFIER "=" assignment | logic_or ;
    def assignment(self) -> Expr:
        expr = self.logic_or()

        # Solo se puede asignar sobre variables. Si no, es un error
        if self._match(TokenType.EQUAL):
            if not isinstance(expr, VariableExpr):
                raise SyntaxError(
                    f"Invalid assignment target, got `{self._lookahead()}` instead"
                )

            value = self.assignment()
            return AssignmentExpr(expr._name, value)

        return expr

    # logic_or      → logic_and ( "or" logic_and )* ;
    def logic_or(self) -> Expr:
        expr = self.logic_and()

        # mientras nos crucemos or, seguimos parseando
        while not self._is_at_end() and self._match(TokenType.OR):
            operator = self._previous()
            right = self.logic_and()
            expr = LogicExpr(expr, operator, right)

        return expr

    # logic_and     → equality ( "and" equality )* ;
    def logic_and(self) -> Expr:
        expr = self.equality()

        # mientras nos crucemos and, seguimos parseando
        while not self._is_at_end() and self._match(TokenType.AND):
            operator = self._previous()
            right = self.equality()
            expr = LogicExpr(expr, operator, right)

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

    # factor         → unary ( ( "/" | "*" | "%" ) unary )* ;
    def factor(self) -> Expr:
        expr = self.unary()

        # mientras nos crucemos *, / o %, seguimos parseando
        # la secuencia de multiplicaciones, divisiones o modulos
        while not self._is_at_end() and self._match(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            operator = self._previous()
            right = self.unary()
            expr = BinaryExpr(expr, operator, right)

        return expr

    # unary          → ( "!" | "-" ) unary | call ;
    def unary(self) -> Expr:
        # a diferencia de las reglas de expresiones binarias,
        # acá el operador es un prefijo.
        # primero chequeamos el operador, y después seguimos
        if self._match(TokenType.BANG, TokenType.MINUS):
            operator = self._previous()
            right = self.unary()
            return UnaryExpr(operator, right)

        # Si no tuve recursividad de unarios, entonces tengo una llamada a una función
        return self.call()

    # call           → primary ( "(" arguments? ")" )* ;
    # arguments      → expression ( "," expression )* ;
    def call(self) -> Expr:
        expr = self.primary()
        arguments: list[Expr] = []

        # Si me cruzo un paréntesis abierto, tengo una llamada a función
        # y tengo que parsear los argumentos
        while self._match(TokenType.LEFT_PAREN):
            # Mientras no me cruce un paréntesis de cierre, sigo parseando argumentos
            while (
                not self._is_at_end()
                and self._lookahead().token_type != TokenType.RIGHT_PAREN
            ):
                # Consumo el primer argumento
                arguments.append(self.expression())

                # Consumo un argumento por cada coma que tengo adelante
                while not self._is_at_end() and self._match(TokenType.COMMA):
                    arguments.append(self.expression())

            # Si o sí tengo que cerrar el paréntesis abierto
            if not self._match(TokenType.RIGHT_PAREN):
                raise SyntaxError(
                    f"Expected ')' after function arguments, got `{self._lookahead()}` instead"
                )

            expr = CallExpr(expr, arguments)

        return expr

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
                    f"Expected ')' after grouping expression, got `{self._lookahead()}` instead"
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
