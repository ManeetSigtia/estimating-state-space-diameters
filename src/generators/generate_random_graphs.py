import networkx as nx
import os


def generate_random_graphs():
    output_dir = "data/5_random"
    # Ensure the directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Format: (Number of Nodes, Probability of Edge)
    # As nodes increase, probability decreases to keep it a sparse network
    configs = [(1000, 0.01), (5000, 0.002), (10000, 0.001)]

    for n, p in configs:
        print(f"Generating {n}-node Erdos-Renyi graph (p={p})...")
        G = nx.erdos_renyi_graph(n, p)

        filepath = os.path.join(output_dir, f"erdos_renyi_{n}.graph")
        with open(filepath, "w") as f:
            for u, v in G.edges():
                f.write(f"{u} {v}\n")

        print(f"  -> Saved to {filepath}")


if __name__ == "__main__":
    generate_random_graphs()
