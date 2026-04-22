import os
import time
import bz2
import networkx as nx
import pandas as pd
import psutil
from src.parser.core import SASParser
from src.graph.builder import StateSpaceBuilder
from src.algorithms.diameter import DiameterCalculator

# ==========================================
# CONFIGURATION
# ==========================================
DATA_DIR = "data"
TOTAL_ROUNDS = 5
FW_NODE_LIMIT = 999  # Strict cutoff for O(V^3) algorithm

# Organize your targets by topology folders
TARGET_FILES = [
    "1_dense_planning/blocksworld_4.sas",
    "1_dense_planning/blocksworld_5.sas",
    "1_dense_planning/blocksworld_6.sas",
    "1_dense_planning/gripper_4.sas",
    "1_dense_planning/gripper_8.sas",
    "1_dense_planning/hanoi_8.sas",
    "2_sparse_planning/visitall_2x5.sas",
    "2_sparse_planning/visitall_3x3.sas",
    "2_sparse_planning/visitall_3x4.sas",
    "3_scale_free_social/PGPgiantcompo.graph.bz2",
    "3_scale_free_social/cond-mat.graph.bz2",
    "3_scale_free_social/hep-th.graph.bz2",
    "4_pathological_custom/aingworth_breaker.graph",
    "5_random/erdos_renyi_1000.graph",
    "5_random/erdos_renyi_5000.graph",
    "5_random/erdos_renyi_10000.graph",
]


def elevate_process_priority():
    """Tells Windows to prioritize this script over background tasks."""
    try:
        p = psutil.Process(os.getpid())
        p.nice(psutil.HIGH_PRIORITY_CLASS)
        print("SUCCESS: Process elevated to HIGH_PRIORITY_CLASS.")
    except Exception as e:
        print(f"WARNING: Could not elevate process priority: {e}")


def load_graph(file_path, filename):
    """Handles both SAS parsing and DIMACS edge lists."""
    if filename.endswith(".sas"):
        try:
            with open(file_path, "r") as f:
                content = f.read()
            problem = SASParser().parse(content)
            return StateSpaceBuilder(problem).build_reachable_graph()
        except Exception as e:
            print(f"  [!] Failed to parse SAS: {e}")
            return None

    elif filename.endswith(".bz2") or filename.endswith(".graph"):
        G = nx.Graph()
        try:
            f = (
                bz2.open(file_path, "rt")
                if filename.endswith(".bz2")
                else open(file_path, "r")
            )
            with f:
                for line in f:
                    if line.startswith("%") or line.startswith("#") or not line.strip():
                        continue
                    parts = line.split()
                    if len(parts) >= 2:
                        G.add_edge(int(parts[0]), int(parts[1]))
            return G
        except Exception as e:
            print(f"  [!] Failed to parse DIMACS: {e}")
            return None
    return None


def main():
    elevate_process_priority()
    results = []

    # Create CSV immediately to ensure write permissions
    csv_filename = "final_benchmark_results.csv"
    cols = [
        "Round",
        "File",
        "Nodes",
        "Edges",
        "Density",
        "Diam (Exact)",
        "Diam (Aing-Def)",
        "Diam (Aing-s10)",
        "Diam (FW)",
        "Time (Exact)",
        "Time (Aing-Def)",
        "Time (Aing-s10)",
        "Time (FW)",
    ]
    pd.DataFrame(columns=cols).to_csv(csv_filename, index=False)

    print(f"\nStarting {TOTAL_ROUNDS} benchmark rounds on {len(TARGET_FILES)} files...")

    # Round-Robin Loop
    for current_round in range(TOTAL_ROUNDS + 1):
        is_warmup = current_round == 0
        round_label = (
            "WARM-UP" if is_warmup else f"ROUND {current_round}/{TOTAL_ROUNDS}"
        )

        print("\n" + "=" * 50)
        print(f" COMMENCING: {round_label}")
        print("=" * 50)

        for filepath in TARGET_FILES:
            full_path = os.path.join(DATA_DIR, filepath)
            filename = os.path.basename(filepath)

            if not os.path.exists(full_path):
                print(f"  [Skipping] File not found: {filepath}")
                continue

            print(f"\n--- {filename} ---")

            # 1. Load Data
            t0 = time.time()
            graph = load_graph(full_path, filename)
            if graph is None:
                continue

            n_nodes = len(graph.nodes())
            n_edges = len(graph.edges())
            density = round(n_edges / n_nodes, 4) if n_nodes > 0 else 0
            print(
                f"  Graph Loaded. Nodes: {n_nodes} | Edges: {n_edges} | Density: {density} | Load Time: {time.time()-t0:.2f}s"
            )

            calc = DiameterCalculator(graph)

            # --- ALGORITHM EXECUTIONS ---

            # A. Exact (NetworkX)
            t0 = time.time()
            diam_exact = calc.calculate_exact_diameter()
            t_exact = time.time() - t0
            print(f"  > Exact (NetworkX): {diam_exact} ({t_exact:.2f}s)")

            # B. Aingworth (Default Threshold)
            t0 = time.time()
            diam_aing_def = calc.aingworth_approximation()
            t_aing_def = time.time() - t0
            print(f"  > Aingworth (Default): {diam_aing_def} ({t_aing_def:.2f}s)")

            # C. Aingworth (Forced s=10)
            t0 = time.time()
            diam_aing_s10 = calc.aingworth_approximation(force_s=10)
            t_aing_s10 = time.time() - t0
            print(f"  > Aingworth (s=10): {diam_aing_s10} ({t_aing_s10:.2f}s)")

            # D. Floyd-Warshall (Strict Cutoff)
            if n_nodes <= FW_NODE_LIMIT:
                t0 = time.time()
                diam_fw = calc.floyd_warshall()
                t_fw = time.time() - t0
                print(f"  > Exact (Floyd-Warshall): {diam_fw} ({t_fw:.2f}s)")
            else:
                diam_fw = "N/A"
                t_fw = 0.0
                print(f"  > Exact (Floyd-Warshall): Skipped (Nodes > {FW_NODE_LIMIT})")

            # --- SAVE RESULTS (Only if not warmup) ---
            if not is_warmup:
                res = {
                    "Round": current_round,
                    "File": filename,
                    "Nodes": n_nodes,
                    "Edges": n_edges,
                    "Density": density,
                    "Diam (Exact)": diam_exact,
                    "Diam (Aing-Def)": diam_aing_def,
                    "Diam (Aing-s10)": diam_aing_s10,
                    "Diam (FW)": diam_fw,
                    "Time (Exact)": round(t_exact, 4),
                    "Time (Aing-Def)": round(t_aing_def, 4),
                    "Time (Aing-s10)": round(t_aing_s10, 4),
                    "Time (FW)": round(t_fw, 4),
                }

                # Append to CSV immediately
                pd.DataFrame([res]).to_csv(
                    csv_filename, mode="a", header=False, index=False
                )
                print(f"  [Data Saved to CSV]")

    print("\n" + "=" * 50)
    print(" BENCHMARKING COMPLETE!")
    print(f" Data secured in {csv_filename}")
    print("=" * 50)


if __name__ == "__main__":
    main()
