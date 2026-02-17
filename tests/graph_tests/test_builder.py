import unittest
import networkx as nx
from src.parser.core import SASParser
from src.graph.builder import StateSpaceBuilder
from tests.config import get_data_file


class TestSimpleSwitchGraph(unittest.TestCase):
    def setUp(self):
        file_path = get_data_file("switch_simple.sas")
        with open(file_path, "r") as f:
            content = f.read()
        self.problem = SASParser().parse(content)
        self.builder = StateSpaceBuilder(self.problem)
        self.graph = self.builder.build_reachable_graph()

    def test_basic_structure(self):
        """Simple switch: 2 nodes (Off, On), 1 Edge (Turn On)."""
        self.assertEqual(len(self.graph.nodes), 2)
        self.assertEqual(len(self.graph.edges), 1)

    def test_transition_correctness(self):
        """Check if the edge correctly connects 0 -> 1."""
        off_state = (0,)
        on_state = (1,)

        # Check edge existence
        self.assertTrue(self.graph.has_edge(off_state, on_state))

        # Check edge attributes (Name and Cost)
        edge = self.graph[off_state][on_state]
        self.assertEqual(edge["weight"], 1)
        self.assertEqual(edge["label"], "turn_on")


class TestGripperGraph(unittest.TestCase):
    def setUp(self):
        file_path = get_data_file("gripper_simple.sas")
        with open(file_path, "r") as f:
            content = f.read()
        self.problem = SASParser().parse(content)
        self.builder = StateSpaceBuilder(self.problem)
        self.graph = self.builder.build_reachable_graph()

    def test_reachable_states_count(self):
        """
        All 12 states include:
        robot in room a, hand_free,  ball in room a - valid
        robot in room a, hand_free,  ball in room b - valid
        robot in room a, hand_free,  ball in hand
        robot in room a, hand_carry, ball in room a
        robot in room a, hand_carry, ball in room b
        robot in room a, hand_carry, ball in hand   - valid
        robot in room b, hand_free,  ball in room a - valid
        robot in room b, hand_free,  ball in room b - valid
        robot in room b, hand_free,  ball in hand
        robot in room b, hand_carry, ball in room a
        robot in room b, hand_carry, ball in room b
        robot in room b, hand_carry, ball in hand   - valid
        Meaningful Test: Verify exactly 6 reachable states exist.
        """
        self.assertEqual(len(self.graph.nodes), 6)

    def test_solution_path_exists(self):
        """
        Start: (0, 0, 0) -> Robot A, Free, Ball A
        Goal:  (?, ?, ?) -> Ball at Room B (Index 2 is Value 1)
        """
        start_node = tuple(self.problem.initial_state)

        # Find WHICH node in the graph represents the goal
        # The goal is "Ball (Var 2) is at Room B (Value 1)"
        goal_nodes = [
            n for n in self.graph.nodes if n[2] == 1  # Check if Variable 2 == 1
        ]

        self.assertTrue(len(goal_nodes) > 0, "Graph contains no goal states!")

        # Check if ANY goal node can be reached from start
        # Use NetworkX shortest path logic
        found_path = False
        for goal in goal_nodes:
            if nx.has_path(self.graph, start_node, goal):
                found_path = True

                # Verify the cost is 3 (Pick + Move + Drop)
                path_length = nx.shortest_path_length(
                    self.graph, start_node, goal, weight="weight"
                )
                self.assertEqual(path_length, 3, "Optimal path should be cost 3")
                break

        self.assertTrue(found_path, "Could not find path to goal!")


class TestGripperCartesianGraph(unittest.TestCase):
    """
    Tests GRAPH B: The Cartesian Graph (Theoretical).
    Verifies that we generate the full universe and can filter it back down.
    """

    def setUp(self):
        file_path = get_data_file("gripper_simple.sas")
        with open(file_path, "r") as f:
            content = f.read()
        self.problem = SASParser().parse(content)
        self.builder = StateSpaceBuilder(self.problem)
        # Build the raw 'God Mode' graph
        self.raw_graph = self.builder.build_cartesian_graph()

        # self.builder.visualize_graph(graph=self.raw_graph, initial_state=(0, 0, 0))

    def test_cartesian_states_count(self):
        """
        Verifies strict Cartesian product:
        Var0 (Robot) ranges [0,1] -> 2
        Var1 (Hand)  ranges [0,1] -> 2
        Var2 (Ball)  ranges [0,1,2] -> 3
        Total = 2 * 2 * 3 = 12 nodes.
        """
        self.assertEqual(len(self.raw_graph.nodes), 12)

    def test_filter_component_logic(self):
        """
        CRITICAL EXPERIMENT:
        1. We take the messy 12-node graph.
        2. We ask for the component containing Start (0,0,0).
        3. It should return exactly the same 6 nodes as the Reachable Graph.

        This proves that Graph B (Filtered) == Graph A.
        """
        filtered_graph = self.builder.get_main_component(self.raw_graph)

        # 1. Count must match Graph A
        self.assertEqual(len(filtered_graph.nodes), 6)

        # 2. Must contain start
        self.assertTrue(filtered_graph.has_node((0, 0, 0)))

        # 3. Must NOT contain an impossible state
        # e.g., (0, 1, 0) -> Robot A, Hand Carry, Ball A
        # This implies hand is full but ball is still on ground. Impossible.
        self.assertFalse(filtered_graph.has_node((0, 1, 0)))


if __name__ == "__main__":
    unittest.main()
