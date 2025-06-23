from enum import IntEnum, auto
from typing import Union


class OpCode(IntEnum):
    # Instrucción con operandos:
    # después del opcode, hay un byte que es el índice de la constante referenciada
    OP_CONSTANT = auto()
    # Todo el resto son operaciones sin operandos.
    # Operan directamente sobre el tope del stack de la máquina virtual.
    OP_RETURN = auto()
    OP_NEGATE = auto()
    OP_ADD = auto()
    OP_SUBTRACT = auto()
    OP_MULTIPLY = auto()
    OP_DIVIDE = auto()


class Chunk(object):
    def __init__(self):
        # Todos los bytes del chunk.
        # Hay dos tipos de bytes:
        # - Instrucciones de bytecode (OpCode)
        # - Referencias a constantes (índices en el pool de constantes)
        self.bytes: list[int] = []

        # Pool de constantes
        self.constants: list[float] = []

    # Escribe un byte al chunk
    def write(self, byte: int):
        self.bytes.append(byte)

    # Agrega una constante al pool y devuelve el índice
    def add_constant(self, value: float):
        self.constants.append(value)
        return len(self.constants) - 1

    # Desensambla el chunk (muchos bytes) para imprimirlo en un formato legible (el nombre de las instrucciones)
    # (es la operación inversa a ensamblar instrucciones assembly a código máquina)
    def dis(self):
        print(f"== chunk ==")
        i = 0
        while i < len(self.bytes):
            byte = self.bytes[i]
            print(f"{i:04d}", end=" ")
            match byte:
                case OpCode.OP_RETURN:
                    print("OP_RETURN")
                    i += 1
                case OpCode.OP_NEGATE:
                    print("OP_NEGATE")
                    i += 1
                case OpCode.OP_ADD:
                    print("OP_ADD")
                    i += 1
                case OpCode.OP_SUBTRACT:
                    print("OP_SUBTRACT")
                    i += 1
                case OpCode.OP_MULTIPLY:
                    print("OP_MULTIPLY")
                    i += 1
                case OpCode.OP_DIVIDE:
                    print("OP_DIVIDE")
                    i += 1
                case OpCode.OP_CONSTANT:
                    constant_index = self.bytes[i + 1]
                    constant_value = self.constants[constant_index]
                    print(f"OP_CONSTANT {constant_index} '{constant_value}'")
                    # Hay que saltar el byte de la constante!
                    i += 2
                case _:
                    print(f"UNKNOWN {byte}")
                    i += 1
        print(f"== chunk ==")
