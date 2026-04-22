import unittest
import networkx as nx
from src.parser.core import SASParser
from src.graph.builder import StateSpaceBuilder
from src.algorithms.diameter import DiameterCalculator
from tests.config import get_data_file


class TestGripperDiameter(unittest.TestCase):
    def setUp(self):
        file_path = get_data_file("gripper_simple.sas")
        with open(file_path, "r") as f:
            content = f.read()
        self.problem = SASParser().parse(content)
        self.builder = StateSpaceBuilder(self.problem)
        self.graph = self.builder.build_reachable_graph()
        self.calc = DiameterCalculator(self.graph)

    def test_gripper_exact_diameter(self):
        """
        In the 6-state reachable gripper graph:
        Longest shortest path is 5 steps.
        Path: (1,0,0) -> (0,0,0) -> (0,1,2) -> (1,1,2) -> (1,0,1) -> (0,0,1)
        """

        self.assertEqual(self.calc.floyd_warshall(), 5.0)

    def test_gripper_aingworth_bounds(self):
        """
        Verify Aingworth returns a value within the 2/3 approximation bound.
        """
        approx = self.calc.aingworth_approximation()
        exact = self.calc.floyd_warshall()  # 5.0

        print(f"Gripper Exact: {exact}, Aingworth: {approx}")

        # Lower bound guarantee (2/3 * 5.0 = 3.33)
        self.assertGreaterEqual(approx, (2 / 3) * exact)

        # Upper bound guarantee (cannot exceed true diameter)
        self.assertLessEqual(approx, exact)


class TestSwitchDiameter(unittest.TestCase):
    def setUp(self):
        file_path = get_data_file("switch_simple.sas")
        with open(file_path, "r") as f:
            content = f.read()
        self.problem = SASParser().parse(content)
        self.builder = StateSpaceBuilder(self.problem)
        self.graph = self.builder.build_cartesian_graph()
        self.calc = DiameterCalculator(self.graph)

    def test_switch_aingworth(self):
        """
        Diameter is 1.0. Aingworth should capture this exactly
        because s=sqrt(2) approx 1, so partial BFS visits nearly everything
        in such a tiny graph.
        """
        approx = self.calc.aingworth_approximation()
        self.assertEqual(approx, 1.0)
