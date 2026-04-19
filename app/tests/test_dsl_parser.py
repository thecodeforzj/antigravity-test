import unittest
import os
import sys
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from smt_dsl_parser import SMTDSLParser

class TestSMTDSLParser(unittest.TestCase):
    def setUp(self):
        self.manifest_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../flow/02_Specs/Hardware_Manifest.json'))
        self.sample_dsl = os.path.abspath(os.path.join(os.path.dirname(__file__), 'horner_sample.json'))

    def test_horner_end_to_end(self):
        """AC-DSL-01: End-to-end schedule for Horner sequence"""
        parser = SMTDSLParser(self.manifest_path)
        parser.load_instructions(self.sample_dsl)
        
        # Start search from II=1
        result = parser.solve_modulo(initial_ii=1)
        
        self.assertIsNotNone(result)
        self.assertGreaterEqual(result["ii"], 1)
        
        # Verify latency constraints in schedule
        s = result["schedule"]
        # R0:1, R1:1, MUL:4, ADD:4, W:1
        # R0, R1 -> MUL0 (at least t_R + 1)
        self.assertGreaterEqual(s["MUL0"], min(s["R0"], s["R1"]) + 1)
        # MUL0 -> ADD0 (at least t_MUL + 4)
        self.assertGreaterEqual(s["ADD0"], s["MUL0"] + 4)
        # ADD0 -> W0 (at least t_ADD + 4)
        self.assertGreaterEqual(s["W0"], s["ADD0"] + 4)

    def test_ii_search_loop(self):
        """Verify the 'ii += 1' logic in solve_modulo"""
        parser = SMTDSLParser(self.manifest_path)
        # Force a conflict at II=1 by adding two fpadd
        parser.scheduler.add_instruction("A", "fpadd")
        parser.scheduler.add_instruction("B", "fpadd")
        
        # II=1 will fail, loop will move to II=2 and succeed
        result = parser.solve_modulo(initial_ii=1)
        self.assertIsNotNone(result)
        self.assertEqual(result["ii"], 2)

    def test_impossible_ii(self):
        """Verify the 'return None' when II > 1024"""
        parser = SMTDSLParser(self.manifest_path)
        # Start search from a very high value that will fail
        # (This is a simplified test for the return None branch)
        result = parser.solve_modulo(initial_ii=1025)
        self.assertIsNone(result)
