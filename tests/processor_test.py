"""
Unit-тесты для процессора
"""
import unittest
import processor


class ProcessorTest(unittest.TestCase):
    """
    Unit-тесты для процессора
    """
    input = "tests/input.json"

    def start_machine(self, output, output_type='str'):
        return processor.launch_processor([output, self.input, output_type])

    def test_cat(self):
        output, instr_counter, ticks = self.start_machine("tests/cat")
        self.assertEqual(output, 'hello world')

    def test_hello(self):
        output, instr_counter, ticks = self.start_machine("tests/hello")
        self.assertEqual(output, 'hello world')

    def test_prob1(self):
        output, instr_counter, ticks = self.start_machine("tests/prob1", "int")
        self.assertEqual(output, '233168')
