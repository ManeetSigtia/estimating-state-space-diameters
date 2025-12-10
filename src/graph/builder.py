import networkx as nx
from typing import Tuple, Set
from collections import deque
from src.parser.models import SASProblem


class StateSpaceBuilder:
    def __init__(self, problem: SASProblem):
        self.problem = problem
        # Using a Directed Graph because moving A->B doesn't always mean you can move B->A
        self.graph = nx.DiGraph()

    def build(self) -> nx.DiGraph:
        """
        Explores the entire state space and returns the graph.
        Nodes = State Tuples (e.g., (0, 1, 0))
        Edges = Actions (labeled with operator name and cost)
        """
        # 1. Initial State is already a tuple
        initial_state = self.problem.initial_state

        # 2. Setup BFS
        queue = deque([initial_state])
        visited: Set[Tuple[int, ...]] = {initial_state}

        self.graph.add_node(initial_state)

        while queue:
            current_state = queue.popleft()  # BFS: Pop from left

            # Try every single operator on this state
            for op in self.problem.operators:
                if not op.is_applicable(current_state):
                    continue

                # 1. Calculate next state
                next_state_list = op.apply(current_state)
                next_state = tuple(next_state_list)

                # 2. Add Edge to Graph
                # Store the cost and name so they can be used in algorithms later
                self.graph.add_edge(
                    current_state, next_state, weight=op.cost, label=op.name
                )

                # 3. If this is a new state, add to queue
                if next_state not in visited:
                    visited.add(next_state)
                    queue.append(next_state)
                    self.graph.add_node(next_state)

        return self.graph
