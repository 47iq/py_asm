"""
Unit-тесты для транслятора
"""

import unittest

import translation

import isa


class TranslatorTest(unittest.TestCase):
    """Unit-тесты для транслятора"""

    def simple_test(self, input_file, output, correct):
        translation.main([input_file, output])

        result_code = isa.read_code(output)
        correct_code = isa.read_code(correct)

        self.assertEqual(result_code, correct_code)

    def test_cat(self):
        self.simple_test("cat.asm", "cat.test", "cat")

    def test_prob2(self):
        self.simple_test("prob1.asm", "prob1.test", "prob1")

    def test_hello_world(self):
        self.simple_test("hello.asm", "hello.test", "hello")
