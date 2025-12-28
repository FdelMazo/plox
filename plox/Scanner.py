import re
from .Token import Token, TokenType, TokenKeywords


class Scanner(object):
    TOKEN_REGEX = re.compile(
        r"""
        (?P<WHITESPACE>[ \t\r\n]+)
      | (?P<COMMENT>//[^\n]*)
      | (?P<STRING>"[^"\n]*")
      | (?P<NUMBER>\d+(?:\.\d+)?)
      | (?P<IDENTIFIER>[A-Za-z_][A-Za-z_]*)

      | (?P<BANG_EQUAL>!=)
      | (?P<EQUAL_EQUAL>==)
      | (?P<LESS_EQUAL><=)
      | (?P<GREATER_EQUAL>>=)

      | (?P<LEFT_PAREN>\()
      | (?P<RIGHT_PAREN>\))
      | (?P<LEFT_BRACE>\{)
      | (?P<RIGHT_BRACE>\})
      | (?P<COMMA>,)
      | (?P<MINUS>-)
      | (?P<PLUS>\+)
      | (?P<SEMICOLON>;)
      | (?P<STAR>\*)
      | (?P<SLASH>/)
      | (?P<BANG>!)
      | (?P<EQUAL>=)
      | (?P<LESS><)
      | (?P<GREATER>>)

      | (?P<MISMATCH>.)
        """,
        re.VERBOSE,
    )

    def __init__(self, source: str):
        # nos vamos a ir guardando los tokens, que son el texto crudo acompañado de su significado
        self.tokens: list[Token] = []
        self.source = source

    def scan(self) -> list[Token]:
        for match in self.TOKEN_REGEX.finditer(self.source):
            kind = match.lastgroup
            lexeme = match.group()

            if kind in ("WHITESPACE", "COMMENT"):
                continue

            if kind == "STRING":
                value = lexeme[1:-1]
                self.tokens.append(
                    Token(TokenType.STRING, lexeme=lexeme, literal=value)
                )
                continue

            if kind == "NUMBER":
                self.tokens.append(
                    Token(TokenType.NUMBER, lexeme=lexeme, literal=float(lexeme))
                )
                continue

            if kind == "IDENTIFIER":
                token_type = TokenKeywords.get(lexeme, TokenType.IDENTIFIER)
                self.tokens.append(Token(token_type, lexeme=lexeme, literal=None))
                continue

            if kind == "MISMATCH":
                raise Exception(f"Unexpected character: `{lexeme}`")

            if type(kind) == str:
                self.tokens.append(Token(TokenType[kind], lexeme=lexeme, literal=None))

        self.tokens.append(Token(TokenType.EOF, lexeme="", literal=None))
        return self.tokens
