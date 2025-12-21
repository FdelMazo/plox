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
    tokens = Scanner("(){},-+;*/").scan()
    tokens_type = [token.token_type for token in tokens]

    expected_tokens_type = [
        TokenType.LEFT_PAREN,
        TokenType.RIGHT_PAREN,
        TokenType.LEFT_BRACE,
        TokenType.RIGHT_BRACE,
        TokenType.COMMA,
        TokenType.MINUS,
        TokenType.PLUS,
        TokenType.SEMICOLON,
        TokenType.STAR,
        TokenType.SLASH,
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
