import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from smt_visualizer import SMTVisualizer

class TestSMTVisualizer(unittest.TestCase):
    def test_config_generation(self):
        """AC-VIS-01: Verify dely and loop config"""
        sample_result = {
            "ii": 4,
            "schedule": {"ADD0": 0, "MUL0": 5}
        }
        viz = SMTVisualizer(sample_result)
        config = viz.generate_hardware_config(loop_count=50)
        self.assertEqual(config["initiation_interval_dely"], 4)
        self.assertEqual(config["loop_count"], 50)

    def test_gantt_rendering(self):
        """AC-VIS-02: Verify overlapped stage view"""
        sample_result = {
            "ii": 2,
            "schedule": {"R0": 0, "R1": 1, "MUL0": 2}
        }
        # MUL0 at t=2, II=2 -> Cycle 0, Stage 1
        viz = SMTVisualizer(sample_result)
        chart = viz.render_gantt()
        self.assertIn("R0(S0)", chart)
        self.assertIn("MUL0(S1)", chart)
        self.assertIn("Cycle 00", chart)
        self.assertIn("Cycle 01", chart)
