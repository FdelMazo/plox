import pytest
from plox.Scanner import Scanner
from plox.Token import TokenType


def test_hello_world():
    tokens = Scanner("2+2").scan()
    tokens_type = [token.token_type for token in tokens]

    expected_tokens_type = [
        TokenType.NUMBER,
        TokenType.PLUS,
        TokenType.NUMBER,
        TokenType.EOF,
    ]

    assert tokens_type == expected_tokens_type


def test_string_literal():
    tokens = Scanner('"hello world"').scan()
    tokens_type = [token.token_type for token in tokens]

    expected_tokens_type = [
        TokenType.STRING,
        TokenType.EOF,
    ]

    assert tokens_type == expected_tokens_type
    assert tokens[0].literal == "hello world"


def test_multilne_strings():
    tokens = Scanner("'hello world'").scan()
    tokens_type = [token.token_type for token in tokens]

    expected_tokens_type = [
        TokenType.STRING,
        TokenType.EOF,
    ]

    assert tokens_type == expected_tokens_type
    assert tokens[0].literal == "hello world"

    tokens = Scanner(
        """
"comentario
con salto de linea"
        """
    ).scan()
    tokens_type = [token.token_type for token in tokens]

    expected_tokens_type = [
        TokenType.STRING,
        TokenType.EOF,
    ]

    assert tokens_type == expected_tokens_type
    assert tokens[0].literal == "comentario\ncon salto de linea"


def test_number_literal():
    tokens = Scanner("123.45").scan()
    tokens_type = [token.token_type for token in tokens]

    expected_tokens_type = [
        TokenType.NUMBER,
        TokenType.EOF,
    ]

    assert tokens_type == expected_tokens_type
    assert tokens[0].literal == 123.45


def test_error_unterminated_string():
    with pytest.raises(Exception) as excinfo:
        Scanner('"hello world').scan()
    assert "Unterminated string" in str(excinfo.value)

    with pytest.raises(Exception) as excinfo:
        Scanner(
            """
            'comillas simples
            no son multilinea'
            """
        ).scan()
    assert "Unterminated string" in str(excinfo.value)

    with pytest.raises(Exception) as excinfo:
        Scanner(
            """
            "hello
            world
            """
        ).scan()
    assert "Unterminated string" in str(excinfo.value)


def test_identifiers():
    tokens = Scanner("foo bar trueman t0").scan()
    tokens_type = [token.token_type for token in tokens]

    expected_tokens_type = [
        TokenType.IDENTIFIER,
        TokenType.IDENTIFIER,
        TokenType.IDENTIFIER,
        TokenType.IDENTIFIER,
        TokenType.EOF,
    ]

    assert tokens_type == expected_tokens_type
    assert tokens[0].lexeme == "foo"
    assert tokens[1].lexeme == "bar"
    assert tokens[2].lexeme == "trueman"


def test_keywords():
    tokens = Scanner(
        "and else false fun for if nil or print return true var while const break continue"
    ).scan()
    tokens_type = [token.token_type for token in tokens]

    expected_tokens_type = [
        TokenType.AND,
        TokenType.ELSE,
        TokenType.FALSE,
        TokenType.FUN,
        TokenType.FOR,
        TokenType.IF,
        TokenType.NIL,
        TokenType.OR,
        TokenType.PRINT,
        TokenType.RETURN,
        TokenType.TRUE,
        TokenType.VAR,
        TokenType.WHILE,
        TokenType.CONST,
        TokenType.BREAK,
        TokenType.CONTINUE,
        TokenType.EOF,
    ]

    assert tokens_type == expected_tokens_type


def test_error_unexpected_character():
    with pytest.raises(Exception) as excinfo:
        Scanner("@").scan()
    assert "Unexpected character" in str(excinfo.value)

    with pytest.raises(Exception) as excinfo:
        Scanner("`").scan()
    assert "Unexpected character" in str(excinfo.value)


def test_remove_whitespace():
    expected_tokens_type = [
        TokenType.EOF,
    ]

    tokens = Scanner(" ").scan()
    tokens_type = [token.token_type for token in tokens]
    assert tokens_type == expected_tokens_type

    tokens = Scanner("  ").scan()
    tokens_type = [token.token_type for token in tokens]
    assert tokens_type == expected_tokens_type

    tokens = Scanner("\r").scan()
    tokens_type = [token.token_type for token in tokens]
    assert tokens_type == expected_tokens_type

    tokens = Scanner(
        """

        """
    ).scan()
    tokens_type = [token.token_type for token in tokens]
    assert tokens_type == expected_tokens_type


def test_remove_comments():
    expected_tokens_type = [
        TokenType.EOF,
    ]

    tokens = Scanner("// aaaa").scan()
    tokens_type = [token.token_type for token in tokens]
    assert tokens_type == expected_tokens_type


def test_remove_multiline_comments():
    expected_tokens_type = [
        TokenType.EOF,
    ]

    tokens = Scanner(
        """
        /*
        comentario multilinea
        */
        """
    ).scan()
    tokens_type = [token.token_type for token in tokens]
    assert tokens_type == expected_tokens_type

    tokens = Scanner(
        """
        /*
        comentario multilinea
        /*
        comentario multilinea anidado
        */
        // otro comentario mas
        */
        """
    ).scan()
    tokens_type = [token.token_type for token in tokens]
    assert tokens_type == expected_tokens_type

    with pytest.raises(Exception) as excinfo:
        Scanner(
            """
            /*
            comentario multilinea
            /*
            comentario multilinea anidado
            */
            // otro comentario mas
            """
        ).scan()
    assert "Unterminated comment" in str(excinfo.value)


def test_single_char_tokens():
    tokens = Scanner("(){}[],-+;*/%:?**").scan()
    tokens_type = [token.token_type for token in tokens]

    expected_tokens_type = [
        TokenType.LEFT_PAREN,
        TokenType.RIGHT_PAREN,
        TokenType.LEFT_BRACE,
        TokenType.RIGHT_BRACE,
        TokenType.LEFT_BRACKET,
        TokenType.RIGHT_BRACKET,
        TokenType.COMMA,
        TokenType.MINUS,
        TokenType.PLUS,
        TokenType.SEMICOLON,
        TokenType.STAR,
        TokenType.SLASH,
        TokenType.PERCENT,
        TokenType.COLON,
        TokenType.QUESTION,
        TokenType.STAR_STAR,
        TokenType.EOF,
    ]

    assert tokens_type == expected_tokens_type


def test_double_char_tokens():
    tokens = Scanner("! != = == < <= > >=").scan()
    tokens_type = [token.token_type for token in tokens]

    expected_tokens_type = [
        TokenType.BANG,
        TokenType.BANG_EQUAL,
        TokenType.EQUAL,
        TokenType.EQUAL_EQUAL,
        TokenType.LESS,
        TokenType.LESS_EQUAL,
        TokenType.GREATER,
        TokenType.GREATER_EQUAL,
        TokenType.EOF,
    ]

    assert tokens_type == expected_tokens_type


def test_string_literal():
    tokens = Scanner('"hello world"').scan()
    tokens_type = [token.token_type for token in tokens]

    expected_tokens_type = [
        TokenType.STRING,
        TokenType.EOF,
    ]

    assert tokens_type == expected_tokens_type
    assert tokens[0].literal == "hello world"


def test_number_literal():
    tokens = Scanner("123.45").scan()
    tokens_type = [token.token_type for token in tokens]

    expected_tokens_type = [
        TokenType.NUMBER,
        TokenType.EOF,
    ]

    assert tokens_type == expected_tokens_type
    assert tokens[0].literal == 123.45


def test_error_unterminated_string():
    with pytest.raises(Exception) as excinfo:
        Scanner('"hello world').scan()
    assert "Unterminated string" in str(excinfo.value)


def test_identifiers():
    tokens = Scanner("foo bar trueman").scan()
    tokens_type = [token.token_type for token in tokens]

    expected_tokens_type = [
        TokenType.IDENTIFIER,
        TokenType.IDENTIFIER,
        TokenType.IDENTIFIER,
        TokenType.EOF,
    ]

    assert tokens_type == expected_tokens_type
    assert tokens[0].lexeme == "foo"
    assert tokens[1].lexeme == "bar"
    assert tokens[2].lexeme == "trueman"


def test_keywords():
    tokens = Scanner(
        "and else false fun for if nil or print return true var while"
    ).scan()
    tokens_type = [token.token_type for token in tokens]

    expected_tokens_type = [
        TokenType.AND,
        TokenType.ELSE,
        TokenType.FALSE,
        TokenType.FUN,
        TokenType.FOR,
        TokenType.IF,
        TokenType.NIL,
        TokenType.OR,
        TokenType.PRINT,
        TokenType.RETURN,
        TokenType.TRUE,
        TokenType.VAR,
        TokenType.WHILE,
        TokenType.EOF,
    ]

    assert tokens_type == expected_tokens_type


def test_error_unexpected_character():
    with pytest.raises(Exception) as excinfo:
        Scanner("@").scan()
    assert "Unexpected character" in str(excinfo.value)

    with pytest.raises(Exception) as excinfo:
        Scanner("`").scan()
    assert "Unexpected character" in str(excinfo.value)


def test_error_invalid_numbers():
    with pytest.raises(Exception) as excinfo:
        Scanner("1..2").scan()
    assert "Invalid number" in str(excinfo.value)

    with pytest.raises(Exception) as excinfo:
        Scanner("1.5.2").scan()
    assert "Invalid number" in str(excinfo.value)

    with pytest.raises(Exception) as excinfo:
        Scanner("1.").scan()
    assert "Invalid number" in str(excinfo.value)

    with pytest.raises(Exception) as excinfo:
        Scanner(".2").scan()
    assert "Unexpected character" in str(excinfo.value)


def test_scanner_plus_plus_token():
    tokens = Scanner("++").scan()
    tokens_type = [token.token_type for token in tokens]

    expected_tokens_type = [TokenType.PLUS_PLUS, TokenType.EOF]

    assert tokens_type == expected_tokens_type


def test_plus_plus_token_and_plus_token():
    tokens = Scanner("+++").scan()
    tokens_type = [token.token_type for token in tokens]

    expected_tokens_type = [TokenType.PLUS_PLUS, TokenType.PLUS, TokenType.EOF]

    assert tokens_type == expected_tokens_type


def test_switch_case_default_keywords():
    tokens = Scanner("switch case default").scan()
    tokens_type = [token.token_type for token in tokens]

    expected_tokens_type = [
        TokenType.SWITCH,
        TokenType.CASE,
        TokenType.DEFAULT,
        TokenType.EOF,
    ]

    assert tokens_type == expected_tokens_type


def test_switch_not_identifier():
    tokens = Scanner("switch").scan()
    assert tokens[0].token_type == TokenType.SWITCH
    assert tokens[0].lexeme == "switch"

    tokens = Scanner("switching").scan()
    assert tokens[0].token_type == TokenType.IDENTIFIER
    assert tokens[0].lexeme == "switching"


def test_string_interpolation_simple():
    tokens = Scanner('print "hola, ${mundo}!";').scan()

    expected_tokens_type: list[tuple[TokenType, str | None]] = [
        (TokenType.PRINT, None),
        (TokenType.STRING, '"hola, '),
        (TokenType.INTERPOLATION_START, None),
        (TokenType.IDENTIFIER, "mundo"),
        (TokenType.INTERPOLATION_END, None),
        (TokenType.STRING, '!"'),
        (TokenType.SEMICOLON, None),
        (TokenType.EOF, None),
    ]

    for expected, actual in zip(expected_tokens_type, tokens):
        if expected[1] is not None:
            assert expected[1] == actual.lexeme

        assert expected[0] == actual.token_type


def test_string_interpolation_with_ternary():
    tokens = Scanner('print "hola, ${condicion ? "amigo" : "desconocido"}!";').scan()

    expected_tokens_type: list[tuple[TokenType, str | None]] = [
        (TokenType.PRINT, None),
        (TokenType.STRING, '"hola, '),
        (TokenType.INTERPOLATION_START, None),
        (TokenType.IDENTIFIER, "condicion"),
        (TokenType.QUESTION, None),
        (TokenType.STRING, '"amigo"'),
        (TokenType.COLON, None),
        (TokenType.STRING, '"desconocido"'),
        (TokenType.INTERPOLATION_END, None),
        (TokenType.STRING, '!"'),
        (TokenType.SEMICOLON, None),
        (TokenType.EOF, None),
    ]

    for expected, actual in zip(expected_tokens_type, tokens):
        if expected[1] is not None:
            assert expected[1] == actual.lexeme

        assert expected[0] == actual.token_type


def test_string_interpolation_double():
    tokens = Scanner('print "hola, ${mundo} por parte de ${quien}!";').scan()

    expected_tokens_type: list[tuple[TokenType, str | None]] = [
        (TokenType.PRINT, None),
        (TokenType.STRING, '"hola, '),
        (TokenType.INTERPOLATION_START, None),
        (TokenType.IDENTIFIER, "mundo"),
        (TokenType.INTERPOLATION_END, None),
        (TokenType.STRING, " por parte de "),
        (TokenType.INTERPOLATION_START, None),
        (TokenType.IDENTIFIER, "quien"),
        (TokenType.INTERPOLATION_END, None),
        (TokenType.STRING, '!"'),
        (TokenType.SEMICOLON, None),
        (TokenType.EOF, None),
    ]

    for expected, actual in zip(expected_tokens_type, tokens):
        if expected[1] is not None:
            assert expected[1] == actual.lexeme

        assert expected[0] == actual.token_type


def test_string_interpolation_recursive():
    tokens = Scanner('print "hola, ${"mundo ${quien}!"}";').scan()

    expected_tokens_type: list[tuple[TokenType, str | None]] = [
        (TokenType.PRINT, None),
        (TokenType.STRING, '"hola, '),
        (TokenType.INTERPOLATION_START, None),
        (TokenType.STRING, '"mundo '),
        (TokenType.INTERPOLATION_START, None),
        (TokenType.IDENTIFIER, "quien"),
        (TokenType.INTERPOLATION_END, None),
        (TokenType.STRING, '!"'),
        (TokenType.INTERPOLATION_END, None),
        (TokenType.STRING, '"'),
        (TokenType.SEMICOLON, None),
        (TokenType.EOF, None),
    ]

    for expected, actual in zip(expected_tokens_type, tokens):
        if expected[1] is not None:
            assert expected[1] == actual.lexeme

        assert expected[0] == actual.token_type


def test_string_interpolation_nested_100_deep():
    DEPTH = 100
    interpolation = '"${' * DEPTH + "x" + '}"' * DEPTH + ";"
    tokens = Scanner(interpolation).scan()

    expected_tokens_type = [
        (TokenType.STRING, '"'),
        (TokenType.INTERPOLATION_START, None),
    ] * DEPTH
    expected_tokens_type += [(TokenType.IDENTIFIER, "x")]
    expected_tokens_type += [
        (TokenType.INTERPOLATION_END, None),
        (TokenType.STRING, '"'),
    ] * DEPTH
    expected_tokens_type += [
        (TokenType.SEMICOLON, None),
        (TokenType.EOF, None),
    ]

    for expected, actual in zip(expected_tokens_type, tokens):
        if expected[1] is not None:
            assert expected[1] == actual.lexeme

        assert expected[0] == actual.token_type


def test_string_interpolation_unterminated():
    with pytest.raises(Exception) as excinfo:
        Scanner('print "hola, ${mundo!;').scan()
    assert "Unterminated interpolation" in str(excinfo.value)

    # Si se inicia un string dentro de la interpolacion y el mismo no se cierra
    # entonces el error que se lanza es de string sin cerrar,
    # porque el scanner espera que se cierre el string antes de cerrar la interpolacion
    with pytest.raises(Exception) as excinfo:
        Scanner(
            'print "hola, ${mundo! -->"<-- esto inicia un nuevo string dentro de la interpolacion;'
        ).scan()
    assert "Unterminated string" in str(excinfo.value)

    with pytest.raises(Exception) as excinfo:
        Scanner('print "hola, ${mundo} por parte de ${quien!;').scan()
    assert "Unterminated interpolation" in str(excinfo.value)
