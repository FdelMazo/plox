from enum import Enum
from ..Chunk import Chunk, OpCode


class VM(object):
    def __init__(self, chunk: Chunk):
        # El chunk a ejecutar
        self.chunk = chunk
        # El instruction pointer
        # siempre apunta a la siguiente instrucción a ejecutar
        self.ip = 0
        # El stack de la máquina virtual
        # almacena todos los valores intermedios que se van produciendo
        self.values: list[float] = []

    def push(self, value: float):
        # Agrega un resultado al tope del stack
        self.values.append(value)

    def pop(self):
        # Si el stack está vacío y llame a pop, es un error
        if not self.values:
            raise RuntimeError("STACK UNDERFLOW")

        # Devuelve el tope del stack, y lo elimina
        return self.values.pop()

    def run(self):
        while self.ip < len(self.chunk.bytes):
            # print(f"{self.ip:04d} - STACK {self.values}")
            byte = self.chunk.bytes[self.ip]
            self.ip += 1
            match byte:
                case OpCode.OP_RETURN:
                    print(f"RESULT {self.pop()}")
                    return True
                case OpCode.OP_CONSTANT:
                    constant_index = self.chunk.bytes[self.ip]
                    constant_value = self.chunk.constants[constant_index]
                    # La instrucción de constante es "cargar" la constante en memoria:
                    # es solamente producir el resultado y pushearlo al tope del stack!
                    self.push(constant_value)
                    # Salteamos el índice de la constante en el ip
                    self.ip += 1
                case OpCode.OP_NEGATE:
                    value = self.pop()
                    self.push(-value)
                case OpCode.OP_ADD:
                    b = self.pop()
                    a = self.pop()
                    self.push(a + b)
                case OpCode.OP_SUBTRACT:
                    b = self.pop()
                    a = self.pop()
                    self.push(a - b)
                case OpCode.OP_MULTIPLY:
                    b = self.pop()
                    a = self.pop()
                    self.push(a * b)
                case OpCode.OP_DIVIDE:
                    b = self.pop()
                    a = self.pop()
                    self.push(a // b)
                case _:
                    raise RuntimeError(f"UNKNOWN {byte}")
