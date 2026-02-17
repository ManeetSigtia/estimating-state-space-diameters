import networkx as nx
import matplotlib.pyplot as plt
import math
from typing import Tuple


class StateSpaceVisualizer:
    def __init__(self, initial_state: Tuple[int, ...] = None):
        """
        Initialize with a default initial state (optional).
        """
        self.default_initial_state = initial_state

    def visualize(self, graph: nx.DiGraph, initial_state: Tuple[int, ...] = None):
        """
        Visualizes the state space graph.
        """
        # 1. Resolve Initial State
        start_node = initial_state or self.default_initial_state

        if start_node is None:
            # Fallback: Try to find a node with in-degree 0, or just pick the first one
            # This handles cases where user didn't pass state info
            try:
                start_node = list(graph.nodes)[0]
            except IndexError:
                print("Graph is empty.")
                return

        # --- 0. SETUP CANVAS ---
        N = len(graph.nodes)
        scale_factor = 1.0 if N < 15 else 15 / N

        # Dynamic sizes
        node_size = max(300, 2800 * scale_factor)
        font_size = max(6, 9 * scale_factor)
        arrow_size = max(10, 20 * scale_factor)

        # Spacing
        y_spacing = 1.5 * max(0.6, scale_factor)
        x_spacing = 3.0 * max(0.6, scale_factor)

        plt.figure(figsize=(18, 12))

        # --- 1. LAYOUTS ---
        pos = {}
        layers = {}
        try:
            lengths = nx.single_source_shortest_path_length(graph, start_node)
            max_depth = 0
            for node, depth in lengths.items():
                if depth not in layers:
                    layers[depth] = []
                layers[depth].append(node)
                max_depth = max(max_depth, depth)

            for depth, nodes in layers.items():
                nodes.sort()
                for i, node in enumerate(nodes):
                    y_pos = (i - (len(nodes) - 1) / 2) * y_spacing
                    pos[node] = (depth * x_spacing, y_pos)
        except nx.NetworkXNoPath:
            pass

        positioned_nodes = set(pos.keys())
        unreachable_nodes = list(set(graph.nodes()) - positioned_nodes)

        if unreachable_nodes:
            junk_subgraph = graph.subgraph(unreachable_nodes)
            components = list(nx.weakly_connected_components(junk_subgraph))
            current_x_offset = 0.0

            for comp in components:
                comp_subgraph = junk_subgraph.subgraph(comp)
                comp_pos = nx.spring_layout(comp_subgraph, seed=42, k=1.5)

                cx = sum(p[0] for p in comp_pos.values()) / len(comp_pos)
                cy = sum(p[1] for p in comp_pos.values()) / len(comp_pos)

                drop_height = 4.0 * max(0.8, scale_factor)
                for node, coords in comp_pos.items():
                    pos[node] = (
                        (coords[0] - cx) + current_x_offset,
                        (coords[1] - cy) - drop_height,
                    )
                current_x_offset += x_spacing

        # --- 2. DRAW NODES ---
        node_colors = []
        for node in graph.nodes():
            if node == start_node:
                node_colors.append("#32CD32")
            elif node in positioned_nodes:
                node_colors.append("#87CEEB")
            else:
                node_colors.append("#FFB6C1")

        nx.draw_networkx_nodes(
            graph,
            pos,
            node_color=node_colors,
            node_size=node_size,
            edgecolors="black",
            linewidths=2.0 * scale_factor,
        )

        if node_size > 500:
            nx.draw_networkx_labels(
                graph,
                pos,
                font_size=font_size,
                font_weight="bold",
                font_family="sans-serif",
            )

        # --- 3. DRAW EDGES ---
        curvature = 0.12
        nx.draw_networkx_edges(
            graph,
            pos,
            node_size=node_size,
            arrowstyle="-|>",
            arrowsize=arrow_size,
            edge_color="#555555",
            width=1.5 * scale_factor,
            connectionstyle=f"arc3, rad={curvature}",
        )

        # --- 4. DRAW LABELS ---
        edge_labels = nx.get_edge_attributes(graph, "label")

        for (u, v), label_text in edge_labels.items():
            if u not in pos or v not in pos:
                continue

            x1, y1 = pos[u]
            x2, y2 = pos[v]
            label = label_text.split()[0]

            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            dx, dy = x2 - x1, y2 - y1
            dist = math.sqrt(dx**2 + dy**2)

            if dist == 0:
                continue

            # Right Normal Vector
            nx_vec, ny_vec = dy / dist, -dx / dist

            # Shift Logic
            shift_amount = dist * (curvature * 0.6)

            lx = mx + (nx_vec * shift_amount)
            ly = my + (ny_vec * shift_amount)

            plt.text(
                lx,
                ly,
                label,
                size=font_size * 0.9,
                color="darkblue",
                horizontalalignment="center",
                verticalalignment="center",
                bbox=dict(facecolor="white", edgecolor="none", alpha=1.0, pad=0.2),
            )

        # --- 5. LEGEND ---
        from matplotlib.lines import Line2D

        legend_elements = [
            Line2D(
                [0],
                [0],
                marker="o",
                color="w",
                markerfacecolor="#32CD32",
                label="Start State",
                markersize=15,
            ),
            Line2D(
                [0],
                [0],
                marker="o",
                color="w",
                markerfacecolor="#87CEEB",
                label="Reachable",
                markersize=15,
            ),
            Line2D(
                [0],
                [0],
                marker="o",
                color="w",
                markerfacecolor="#FFB6C1",
                label="Unreachable",
                markersize=15,
            ),
        ]

        plt.legend(handles=legend_elements, loc="upper right", fontsize=12)
        plt.title(f"State Space: {N} States", fontsize=18)
        plt.axis("off")
        plt.tight_layout()
        plt.show()
