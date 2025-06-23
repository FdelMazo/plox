# Implementación con compilación

Este directorio contiene una mini implementación de Lox que previo a la ejecución compila el código a secuencias de bytecode, y luego las ejecuta en una VM.

No es más que una calculadora

- Números literales: `1`, `2`
- Negar numeros: `-1`
- Sumar y restar: `1 + 2`, `2 - 1`
- Multiplicar y dividir: `2 * 2`, `4 / 2`
- Agrupar: `2 * (1 + 2)`
- Comentarios `// ignorar`

```sh
# levantar un repl, que compila y ejecuta línea por línea
$ ./plox.py
# correr un archivo linea por linea
$ ./plox.py ../examples/calc.lox
```
