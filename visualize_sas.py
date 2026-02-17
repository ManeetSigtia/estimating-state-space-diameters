import os
from src.parser.core import SASParser
from src.graph.builder import StateSpaceBuilder
from src.graph.visualizer import StateSpaceVisualizer


def main():
    # 1. PATH SETUP
    # Change this to point to whatever SAS file you want to check
    sas_file_path = "data/gripper_simple.sas"

    if not os.path.exists(sas_file_path):
        print(f"Error: Could not find file at {sas_file_path}")
        return

    # 2. PARSE
    print(f"Parsing {sas_file_path}...")
    with open(sas_file_path, "r") as f:
        problem = SASParser().parse(f.read())

    # 3. BUILD GRAPH
    print("Building State Space Graph...")
    builder = StateSpaceBuilder(problem)

    # Toggle this comment to switch between "God Mode" and "Robot Mode"
    graph = builder.build_cartesian_graph()
    # graph = builder.build_reachable_graph()

    print(f"Graph built with {len(graph.nodes)} states.")

    # 4. VISUALIZE
    print("Launching Visualizer...")
    viz = StateSpaceVisualizer(initial_state=problem.initial_state)
    viz.visualize(graph)


if __name__ == "__main__":
    main()
