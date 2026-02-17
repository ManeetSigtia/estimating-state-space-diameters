import networkx as nx
import itertools
from typing import Tuple, Set
from collections import deque
from src.parser.models import SASProblem


class StateSpaceBuilder:
    def __init__(self, problem: SASProblem):
        self.problem = problem

    def build_reachable_graph(self) -> nx.DiGraph:
        """
        GRAPH A: Builds the graph using BFS starting from the initial state.
        Represents the 'Practical' state space (Reachability Analysis).
        Guaranteed to be a single connected component containing the start state.
        """
        graph = nx.DiGraph()
        initial_state = self.problem.initial_state

        # Setup BFS
        queue = deque([initial_state])
        visited: Set[Tuple[int, ...]] = {initial_state}
        graph.add_node(initial_state)

        while queue:
            current_state = queue.popleft()

            for op in self.problem.operators:
                if not op.is_applicable(current_state):
                    continue

                next_state = op.apply(current_state)

                # Add Edge (Update weight if a cheaper path is found)
                self._add_or_update_edge(graph, current_state, next_state, op)

                # If new state, add to queue
                if next_state not in visited:
                    visited.add(next_state)
                    queue.append(next_state)
                    graph.add_node(next_state)

        return graph

    def build_cartesian_graph(self, max_states: int = 100000) -> nx.DiGraph:
        """
        GRAPH B: Builds the graph by generating every mathematically possible state tuple.
        Represents the 'Theoretical' state space (Cartesian Product).
        Likely contains disconnected islands and unreachable states.
        """
        graph = nx.DiGraph()

        # 1. Generate all possible states (Cartesian Product of variable ranges)
        # e.g., if ranges are [2, 2], creates (0,0), (0,1), (1,0), (1,1)
        var_ranges = [range(v.range_size) for v in self.problem.variables]

        # Generator to save memory before the check
        state_generator = itertools.product(*var_ranges)

        # We convert to list to check size, but in production with huge spaces
        # you might want to count differently. For now, this is safe for the limits we set.
        all_states = list(state_generator)

        if len(all_states) > max_states:
            raise MemoryError(
                f"Cartesian graph too large! Generated {len(all_states)} states, "
                f"limit is {max_states}. Stick to Reachable Graph or smaller problems."
            )

        # 2. Add all nodes first (even the isolated ones)
        for state in all_states:
            graph.add_node(state)

        # 3. 'God Mode': Check every operator against every state
        for state in all_states:
            for op in self.problem.operators:
                if op.is_applicable(state):
                    next_state = op.apply(state)
                    # Note: next_state is guaranteed to be in all_states
                    # because we generated the full Cartesian product.
                    self._add_or_update_edge(graph, state, next_state, op)

        return graph

    def get_main_component(self, graph: nx.DiGraph) -> nx.DiGraph:
        """
        Helper: Extracts the Weakly Connected Component containing the Initial State.
        Used to filter the messy Cartesian graph down to the relevant 'Island'
        before running Diameter calculations.
        """
        initial_state = self.problem.initial_state

        if initial_state not in graph:
            raise ValueError("Initial state not found in the provided graph!")

        # Get all weakly connected components (islands)
        # We use weak connectivity because the graph is directed.
        # If A->B, they are in the same component.
        components = nx.weakly_connected_components(graph)

        for component in components:
            if initial_state in component:
                # Return the subgraph (view) as a new independent graph
                return graph.subgraph(component).copy()

        # Should be unreachable code if initial_state is in graph
        return nx.DiGraph()

    def _add_or_update_edge(
        self, graph: nx.DiGraph, u: Tuple[int, ...], v: Tuple[int, ...], op
    ):
        """Standardized logic to add edges with costs"""
        if graph.has_edge(u, v):
            existing_weight = graph[u][v]["weight"]
            if op.cost < existing_weight:
                graph.add_edge(u, v, weight=op.cost, label=op.name)
        else:
            graph.add_edge(u, v, weight=op.cost, label=op.name)
