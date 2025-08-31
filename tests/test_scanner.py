import pytest
from plox.Scanner import Scanner
from plox.Token import TokenType

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
