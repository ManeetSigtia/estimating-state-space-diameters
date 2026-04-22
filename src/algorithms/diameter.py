import networkx as nx
import numpy as np
import math
import heapq
from typing import Dict, Set, List, Tuple


class DiameterCalculator:
    def __init__(self, graph: nx.DiGraph):
        self.graph = graph

    def floyd_warshall(self) -> float:
        """Exact diameter calculation using O(V^3) Floyd-Warshall."""
        nodes = list(self.graph.nodes())
        n = len(nodes)
        if n == 0:
            return 0.0

        node_to_idx = {node: i for i, node in enumerate(nodes)}

        # Initialize distances
        dist = np.full((n, n), np.inf)
        np.fill_diagonal(dist, 0)

        for u, v, data in self.graph.edges(data=True):
            dist[node_to_idx[u]][node_to_idx[v]] = data.get("weight", 1)

        # Standard FW relaxation
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    if dist[i][j] > dist[i][k] + dist[k][j]:
                        dist[i][j] = dist[i][k] + dist[k][j]

        finite_distances = dist[np.isfinite(dist)]
        return float(np.max(finite_distances)) if finite_distances.size > 0 else 0.0

    def calculate_exact_diameter(self) -> float:
        """
        Calculates exact diameter using 'All Pairs Shortest Path'.

        Why this replaces Floyd-Warshall:
        - FW is O(V^3) and uses O(V^2) memory (dense matrix).
        - This approach runs Dijkstra/BFS from each node: O(V * (E + V log V)).
        - For planning graphs (sparse), this is significantly faster.
        """
        nodes = list(self.graph.nodes())
        n = len(nodes)
        if n == 0:
            return 0.0

        max_dist = 0.0

        # nx.all_pairs_dijkstra_path_length yields (source, {target: dist})
        # This is optimized C-under-the-hood in NetworkX for standard graphs.
        try:
            # We use 'weight' if it exists, otherwise it defaults to 1 (BFS)
            for source, lengths in nx.all_pairs_dijkstra_path_length(
                self.graph, weight="weight"
            ):
                if not lengths:
                    continue

                # Get max distance from this specific source
                curr_max = max(lengths.values())

                if curr_max > max_dist:
                    max_dist = curr_max

        except Exception as e:
            print(f"Error in exact calc: {e}")
            return -1.0

        return float(max_dist)

    def aingworth_approximation(self, force_s=None) -> float:
        """
        Approximates the diameter using the Aingworth algorithm (Algorithm Approx-Diameter).
        Source: 'Fast Estimation of Diameter and Shortest Paths', Section 3.2 & 3.3.

        Guarantees: 2/3 * Diameter <= Estimate <= Diameter.
        Complexity: O(m * sqrt(n log n) + n^2 log n).
        """
        nodes = list(self.graph.nodes())
        n = len(nodes)
        if n == 0:
            return 0.0

        # Allow overriding s for your benchmarking
        if force_s is not None:
            s = force_s
        else:
            # Parameter s = sqrt(n * log(n)).
            # We ensure s is at least 1 and at most n.
            val_s = int(math.sqrt(n * math.log(n + 1))) + 1
            s = max(1, min(val_s, n))

        # --- Step 1: Compute s-partial-BFS (Dijkstra) from each vertex ---
        # We store PBFS_s(v) -> Set of vertices visited
        pbfs_sets: Dict[Tuple[int, ...], Set[Tuple[int, ...]]] = {}

        # Track vertex w with the maximum depth in its partial tree
        w = nodes[0]
        max_depth_w = -1.0

        for v in nodes:
            visited_nodes, max_dist = self._partial_dijkstra(v, s)
            pbfs_sets[v] = set(visited_nodes)

            if max_dist > max_depth_w:
                max_depth_w = max_dist
                w = v

        # Set of "Source" nodes to run full Dijkstra from.
        # Initialize with w and PBFS_s(w)
        sources_to_check = set()
        sources_to_check.add(w)
        sources_to_check.update(pbfs_sets[w])

        # --- Step 4 & 5: Compute Dominating Set D in G_hat ---
        # G_hat has edges (v, u) for all u in PBFS_s(v).
        # We need a set D such that for every v, D intersects PBFS_s(v).
        # This is a Set Cover problem: Universe = V, Subsets = {PBFS_s(v) | v in V}.

        # Greedy Set Cover Approximation
        D = self._greedy_dominating_set(nodes, pbfs_sets)

        # Add D to our sources
        sources_to_check.update(D)

        # --- Step 3 & 6: Full BFS/Dijkstra from selected sources ---
        estimator = 0.0

        for source in sources_to_check:
            # Full single-source shortest path
            lengths = nx.single_source_dijkstra_path_length(
                self.graph, source, weight="weight"
            )
            if lengths:
                max_dist_from_source = max(lengths.values())
                if max_dist_from_source > estimator:
                    estimator = max_dist_from_source

        return float(estimator)

    def _partial_dijkstra(self, start_node, limit_k: int) -> Tuple[List, float]:
        """
        Runs Dijkstra but stops after settling limit_k nodes.
        Returns (list of visited nodes, max distance found).
        """
        pq = [(0.0, start_node)]
        # Map of settled nodes
        dists = {}
        max_dist = 0.0

        # We might add duplicates to PQ, typical lazy Dijkstra
        while pq and len(dists) < limit_k:
            d, u = heapq.heappop(pq)

            if u in dists:
                continue

            dists[u] = d
            if d > max_dist:
                max_dist = d

            if len(dists) == limit_k:
                break

            for neighbor, data in self.graph[u].items():
                weight = data.get("weight", 1)
                if neighbor not in dists:
                    heapq.heappush(pq, (d + weight, neighbor))

        return list(dists.keys()), max_dist

    def _greedy_dominating_set(self, universe: List, subsets: Dict) -> Set:
        """
        Approximates the Dominating Set problem via Greedy Set Cover.
        """
        uncovered = set(universe)
        dominating_set = set()

        # Optimization: subsets are PBFS_s(v).
        # We need to pick 'v' (key) such that PBFS_s(v) (value) covers the most uncovered.

        # While the universe is not fully covered
        while uncovered:
            best_v = None
            best_cover_count = -1

            # This search is O(N^2) in worst case, acceptable for the algorithm's constraints
            for v in subsets:
                if v in dominating_set:
                    continue

                # Count intersection size
                # (Intersection of this node's partial neighborhood with remaining uncovered nodes)
                count = 0
                for u in subsets[v]:
                    if u in uncovered:
                        count += 1

                if count > best_cover_count:
                    best_cover_count = count
                    best_v = v

            if best_v is None or best_cover_count == 0:
                # Should not happen in connected components if pbfs_sets includes self
                break

            dominating_set.add(best_v)
            # Remove covered elements
            for u in subsets[best_v]:
                if u in uncovered:
                    uncovered.remove(u)

        return dominating_set
