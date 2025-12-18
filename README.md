# plox

Intérprete de [Lox](https://craftinginterpreters.com/) hecho en Python, para enseñar Lenguajes y Compiladores I (FIUBA)

```sh
# Install uv
# https://docs.astral.sh/uv/getting-started/installation/

# Install the project
uv tool install --editable .

# Set up a simple type checking pre-commit hook
cp pre-commit.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

# Reload your terminal!!!

# Run a script!
plox ./examples/hello.lox

# Run plox anywhere!
plox

# See full options
plox --help
```

En cada branch del repo hay distintas implementaciones de Lox:

- `main` -> Versión Final. Solamente apunta a la última branch.
- `barebones` -> Intérprete mínimo de expresiones (números, booleanos, no mucho más), con lo visto hasta el capítulo 7 de Crafting Interpreters.
- `tree-walk` -> Intérprete completo de statements. Es lo que hay en `barebones` más lo visto en los capítulos 8 a 10 del libro.
- `full-tree-walk` -> Intérprete completo de statements, con resolvedor de scopes estáticos antes de la ejecución. Es lo que hay en `tree-walk` más lo visto en el capítulo 11 del libro.
