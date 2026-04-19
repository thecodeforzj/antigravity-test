import unittest
import os
import sys
# Add parent dir to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from smt_modulo_core import SMTModuloScheduler

class TestSMTModuloCore(unittest.TestCase):
    def setUp(self):
        # Use the relative path to manifest
        self.manifest_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../flow/02_Specs/Hardware_Manifest.json'))

    def test_resource_constraint(self):
        """AC-MOD-01: Verify resource limit for fpadd (count=1)"""
        scheduler = SMTModuloScheduler(self.manifest_path)
        # Add two fpadds
        scheduler.add_instruction("A", "fpadd")
        scheduler.add_instruction("B", "fpadd")
        
        # At II=1, they must conflict
        res = scheduler.solve(ii=1)
        self.assertIsNone(res, "Should be unsat at II=1 for two fpadd units")
        
        # At II=2, they should succeed
        res = scheduler.solve(ii=2)
        self.assertIsNotNone(res)
        self.assertNotEqual(res["schedule"]["A"] % 2, res["schedule"]["B"] % 2)

    def test_bank_conflict(self):
        """AC-MOD-02: Verify bank conflict rule"""
        scheduler = SMTModuloScheduler(self.manifest_path)
        # Add two reads to same bank
        scheduler.add_instruction("R1", "ur_read", bank_id=0)
        scheduler.add_instruction("R2", "ur_read", bank_id=0)
        
        # At II=1, they conflict on Bank 0
        res = scheduler.solve(ii=1)
        self.assertIsNone(res)
        
        # At II=2, they should be assigned to different modulo cycles
        res = scheduler.solve(ii=2)
        self.assertIsNotNone(res)
        self.assertNotEqual(res["schedule"]["R1"] % 2, res["schedule"]["R2"] % 2)

    def test_dependency(self):
        """Verify C3 Dependency Constraint"""
        scheduler = SMTModuloScheduler(self.manifest_path)
        scheduler.add_instruction("ADD1", "fpadd")
        # ADD2 depends on ADD1 with delay 0 (k=0)
        # Latency of fpadd is 4
        scheduler.add_instruction("ADD2", "fpadd", deps=[("ADD1", 0)])
        
        res = scheduler.solve(ii=10)
        self.assertIsNotNone(res)
        self.assertGreaterEqual(res["schedule"]["ADD2"], res["schedule"]["ADD1"] + 4)

    def test_invalid_unit(self):
        scheduler = SMTModuloScheduler(self.manifest_path)
        with self.assertRaises(ValueError):
            scheduler.add_instruction("X", "ghost_unit")
