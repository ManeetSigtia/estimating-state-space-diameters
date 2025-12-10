import unittest
from src.parser.core import SASParser
from tests.config import get_data_file


class TestSimpleSwitch(unittest.TestCase):
    def setUp(self):
        file_path = get_data_file("switch_simple.sas")

        with open(file_path, "r") as f:
            content = f.read()

        self.parser = SASParser()
        self.problem = self.parser.parse(content)

    def test_metadata(self):
        """Test version and metric settings."""
        self.assertEqual(self.problem.version, 3)
        self.assertTrue(self.problem.metric)  # "begin_metric 1" means True

    def test_variable_setup(self):
        """Test if variables are parsed correctly from file."""
        self.assertEqual(len(self.problem.variables), 1)

        # Validate Var 0
        var0 = self.problem.variables[0]
        self.assertEqual(var0.name, "var0")
        self.assertEqual(var0.range_size, 2)
        # Optional: Check the debug names if you want to be thorough
        self.assertIn("Atom light-is-off", var0.atom_names)
        self.assertIn("Atom light-is-on", var0.atom_names)

    def test_initial_state(self):
        """Test if initial state is read correctly."""
        # File says: 0 (Light is Off)
        self.assertEqual(self.problem.initial_state, (0,))

    def test_operator_logic(self):
        """Test if the operator rules (preconditions/effects) are parsed."""
        self.assertEqual(len(self.problem.operators), 1)

        op = self.problem.operators[0]
        self.assertEqual(op.name, "turn_on")
        self.assertEqual(op.cost, 1)

        # Check Precondition (Implicit from '0 0 0 1')
        # Var 0 must be 0 (Off) to turn it on
        self.assertIn((0, 0), op.preconditions)

        # Check Effect
        # Var 0 becomes 1 (On)
        self.assertIn((0, 1), op.effects)

    def test_goal(self):
        """Test if the goal is parsed correctly."""
        # File says: Var 0 must be 1 (On)
        self.assertEqual(self.problem.goal, ((0, 1),))


if __name__ == "__main__":
    unittest.main()
