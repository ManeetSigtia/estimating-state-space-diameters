import unittest
from src.parser.core import SASParser
from tests.config import get_data_file


class TestGripperDomain(unittest.TestCase):
    def setUp(self):
        file_path = get_data_file("gripper_simple.sas")

        with open(file_path, "r") as f:
            content = f.read()

        self.parser = SASParser()
        self.problem = self.parser.parse(content)

    def test_metadata(self):
        """Test version and metric settings."""
        self.assertEqual(self.problem.version, 3)
        self.assertTrue(self.problem.metric)  # "begin_metric 1" means True

    def test_variable_setup(self):
        """Ensure Robot, Hand, and Ball variables have correct ranges."""
        self.assertEqual(len(self.problem.variables), 3)

        # Var 0: Robot (Range 2: Room A, Room B)
        self.assertEqual(self.problem.variables[0].name, "var0_robot")
        self.assertEqual(self.problem.variables[0].range_size, 2)

        # Var 1: Left Hand (Range 2: Free, Carry)
        self.assertEqual(self.problem.variables[1].name, "var1_left_hand")
        self.assertEqual(self.problem.variables[1].range_size, 2)

        # Var 2: Ball 1 (Range 3: Room A, Room B, Carried)
        self.assertEqual(self.problem.variables[2].name, "var2_ball1")
        self.assertEqual(self.problem.variables[2].range_size, 3)

    def test_initial_state(self):
        """
        Test the starting configuration.
        File says: 0 0 0
        Translation: Robot at Room A, Hand Free, Ball at Room A
        """
        expected_state = (0, 0, 0)
        self.assertEqual(self.problem.initial_state, expected_state)

    def test_goal_parsing(self):
        """
        Test if the goal state is correctly parsed.
        File says: Var 2 (Ball1) must be 1 (at Room B).
        """
        self.assertEqual(self.problem.goal, ((2, 1),))

    def test_pick_operator(self):
        """
        Test 'pick ball1 rooma left'.
        Requires: Robot at A (0), Hand Free (0), Ball at A (0)
        Effects: Hand Carrying (1), Ball Carried (2)
        """
        pick_op = next(op for op in self.problem.operators if "pick" in op.name)

        # 1. Check Explicit Prevail: Robot (Var 0) must be at Room A (Value 0)
        self.assertIn((0, 0), pick_op.preconditions)

        # 2. Check Implicit Preconds (from effect lines)
        # Hand (Var 1) must be Free (Value 0)
        self.assertIn((1, 0), pick_op.preconditions)
        # Ball (Var 2) must be at Room A (Value 0)
        self.assertIn((2, 0), pick_op.preconditions)

        # 3. Check Effects
        self.assertIn((1, 1, []), pick_op.effects)  # Hand becomes Carrying (1)
        self.assertIn((2, 2, []), pick_op.effects)  # Ball becomes Carried (2)

    def test_drop_operator(self):
        """
        Test 'drop ball1 roomb left'.
        Requires: Robot at B (1), Hand Carrying (1), Ball Carried (2)
        Effects: Hand Free (0), Ball at B (1)
        """
        drop_op = next(op for op in self.problem.operators if "drop" in op.name)

        # 1. Check Explicit Prevail: Robot (Var 0) must be at Room B (Value 1)
        self.assertIn((0, 1), drop_op.preconditions)

        # 2. Check Implicit Preconds (from effect lines)
        # Hand (Var 1) must be Carrying (Value 1)
        self.assertIn((1, 1), drop_op.preconditions)
        # Ball (Var 2) must be Carried (Value 2)
        self.assertIn((2, 2), drop_op.preconditions)

        # 3. Check Effects
        self.assertIn((1, 0, []), drop_op.effects)  # Hand becomes Free (0)
        self.assertIn((2, 1, []), drop_op.effects)  # Ball becomes At Room B (1)

    def test_move_operator(self):
        """Test 'move rooma roomb'."""
        move_op = next(op for op in self.problem.operators if "move" in op.name)
        # Robot moves from 0 (Room A) to 1 (Room B)
        self.assertIn((0, 0), move_op.preconditions)
        self.assertIn((0, 1, []), move_op.effects)


if __name__ == "__main__":
    unittest.main()
