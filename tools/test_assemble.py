"""Regresiones de validacion y codificacion del ensamblador heredado."""
import unittest

from assemble import assemble


class AssemblerTests(unittest.TestCase):
    def test_known_encodings_and_label(self):
        self.assertEqual(assemble("lui x1, 0x80010\nloop: addi x2, x0, -1\njal x0, loop"),
                         ["800100b7", "fff00113", "ffdff06f"])

    def test_invalid_inputs_fail(self):
        for source in ["addi x1, x0, 2048", "addi x1, x0, -2049",
                       "lw x1, 4096(x0)", "sw x1, -2049(x0)",
                       "beq x0, x0, 4096", "jal x0, 1048576",
                       "jal x0, 2", "addi x16, x0, 0",
                       "lui x1, 0x100000", "loop: add x0, x0, x0\nloop: jal x0, loop",
                       ".word 123", "addi x1, x0, 1, 2", "lw x1, 0(x0)garbage"]:
            with self.subTest(source=source), self.assertRaises(SystemExit):
                assemble(source)

    def test_supported_directives(self):
        self.assertEqual(assemble(".section .text\n.global _start\n_start: addi x0, x0, 0"),
                         ["00000013"])


if __name__ == "__main__":
    unittest.main()
