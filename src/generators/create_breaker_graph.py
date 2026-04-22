import networkx as nx


def create_breaker_graph():
    print("Building the Aingworth Breaker...")
    G = nx.Graph()

    # 1. Left dense cluster (Grid 30x30)
    left_grid = nx.grid_2d_graph(30, 30)
    left_mapping = {n: f"L_{n[0]}_{n[1]}" for n in left_grid.nodes()}
    nx.relabel_nodes(left_grid, left_mapping, copy=False)
    G.add_edges_from(left_grid.edges())

    # 2. Right dense cluster (Grid 30x30)
    right_grid = nx.grid_2d_graph(30, 30)
    right_mapping = {n: f"R_{n[0]}_{n[1]}" for n in right_grid.nodes()}
    nx.relabel_nodes(right_grid, right_mapping, copy=False)
    G.add_edges_from(right_grid.edges())

    # 3. The Highway (length 1000)
    highway_nodes = [f"H_{i}" for i in range(1000)]
    nx.add_path(G, highway_nodes)

    # Connect Highway to centers of Grids
    G.add_edge("L_15_15", "H_0")
    G.add_edge("R_15_15", "H_999")

    # 4. The Fake Tail (length 400)
    tail_nodes = [f"T_{i}" for i in range(400)]
    nx.add_path(G, tail_nodes)

    # Connect Tail to middle of Highway
    G.add_edge("H_500", "T_0")

    # Relabel all nodes to integers so your DIMACS parser can read it
    int_mapping = {node: i + 1 for i, node in enumerate(G.nodes())}
    nx.relabel_nodes(G, int_mapping, copy=False)

    # Save to data folder
    with open("data/aingworth_breaker.graph", "w") as f:
        for u, v in G.edges():
            f.write(f"{u} {v}\n")

    print(f"Done! Created 'aingworth_breaker.graph' with {G.number_of_nodes()} nodes.")


if __name__ == "__main__":
    create_breaker_graph()
