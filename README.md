# plox

Intérprete de Lox (Crafting Interpreters), hecho en Python, para enseñar Lenguajes y Compiladores I (FIUBA)

```sh
# Create virtual environment and instal deps
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements

# Set up a simple type checking pre-commit hook
cp pre-commit.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

# Allow running plox from the command line
chmod +x plox.py
ln -sf $(realpath plox.py) ~/.local/bin/plox

# Run plox!
plox
```
