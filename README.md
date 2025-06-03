# plox

Intérprete de Lox (Crafting Interpreters), hecho en Python, para enseñar Lenguajes y Compiladores I (FIUBA)

```sh
# Create virtual environment and install deps
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements

# Set up a simple type checking pre-commit hook
cp pre-commit.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

# Allow running plox from the command line
chmod +x plox.py
ln -sf $(realpath plox.py) ~/.local/bin/plox

# Run a lox script!
plox ./examples/hello.lox

# Run plox prompt!
plox

# See full options
plox --help
```

En cada branch del repo hay distintas implementaciones de Lox:

- `main` -> Versión Final
- `barebones` -> Intérprete mínimo de expresiones (números, booleanos, no mucho más), con lo visto hasta el capítulo 7 de Crafting Interpreters.
- `tree-walk` -> Intérprete completo de statements. Es lo que hay en `barebones` más lo visto en los capítulos 8 a 10 del libro.
- `full-tree-walk` -> Intérprete completo de statements, con resolvedor de scopes estáticos antes de la ejecución. Es lo que hay en `tree-walk` más lo visto en el capítulo 11 del libro.
