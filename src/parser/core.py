from typing import List, Iterator, Tuple
from .models import SASProblem, SASVariable, SASOperator


class SASParser:
    def __init__(self):
        self.lines: Iterator[str] = iter([])

    def parse(self, content: str) -> SASProblem:
        """Main entry point: Converts raw SAS string to SASProblem AST."""
        self.lines = iter(content.strip().splitlines())

        # Placeholders
        version = 3
        metric = True
        variables = []
        initial_state = tuple()
        goal = tuple()
        operators = []

        while True:
            try:
                line = next(self.lines).strip()
                if line == "begin_version":
                    version = int(next(self.lines))
                elif line == "begin_metric":
                    metric = bool(int(next(self.lines)))
                elif line == "begin_variable":
                    variables.append(self._parse_variable(len(variables)))
                elif line == "begin_state":
                    initial_state = self._parse_state(len(variables))
                elif line == "begin_goal":
                    goal = self._parse_goal()
                elif line == "begin_operator":
                    operators.append(self._parse_operator())
            except StopIteration:
                break

        return SASProblem(version, metric, variables, initial_state, goal, operators)

    def _parse_variable(self, var_id: int) -> SASVariable:
        name = next(self.lines).strip()
        next(self.lines)  # Ignore layer
        range_size = int(next(self.lines))
        atom_names = []
        for _ in range(range_size):
            atom_names.append(next(self.lines).strip())
        next(self.lines)  # end_variable
        return SASVariable(name, var_id, range_size, atom_names)

    def _parse_state(self, variable_count: int) -> Tuple[int, ...]:
        state = []
        for _ in range(variable_count):
            val = next(self.lines).strip()
            state.append(int(val))

        # Sanity Check: The very next line MUST be 'end_state'
        check_tag = next(self.lines).strip()
        if check_tag != "end_state":
            raise ValueError(
                f"Error parsing state: Expected 'end_state' but found '{check_tag}'"
            )

        return tuple(state)

    def _parse_goal(self) -> Tuple[Tuple[int, int], ...]:
        count = int(next(self.lines))
        goals = []
        for _ in range(count):
            line = next(self.lines).split()
            goals.append((int(line[0]), int(line[1])))
        next(self.lines)  # end_goal
        return tuple(goals)

    def _parse_operator(self) -> SASOperator:
        name = next(self.lines).strip()

        # 1. Explicit Preconditions (Prevail conditions)
        prevail_count = int(next(self.lines))
        preconditions = []
        for _ in range(prevail_count):
            line = next(self.lines).split()
            preconditions.append((int(line[0]), int(line[1])))

        # 2. Effects
        effect_count = int(next(self.lines))
        effects = []
        for _ in range(effect_count):
            line = next(self.lines).split()

            # [0] is the count of conditions for this specific effect
            cond_count = int(line[0])
            effect_conditions = []

            # Loop through the condition pairs (if any)
            # Conditions start at index 1. Each condition is 2 numbers (var, val).
            for i in range(cond_count):
                c_var_idx = 1 + (2 * i)
                c_val_idx = c_var_idx + 1

                c_var = int(line[c_var_idx])
                c_val = int(line[c_val_idx])
                effect_conditions.append((c_var, c_val))

            # The standard effect triplet is always at the end
            # Calculate the start index exactly as we discussed
            base_idx = 1 + (2 * cond_count)

            var_id = int(line[base_idx])
            pre_val = int(line[base_idx + 1])
            post_val = int(line[base_idx + 2])

            # Logic: If pre_val is not -1, it applies to the whole operator
            if pre_val != -1:
                preconditions.append((var_id, pre_val))

            effects.append((var_id, post_val, effect_conditions))

        cost = int(next(self.lines))
        next(self.lines)  # end_operator

        return SASOperator(name, cost, preconditions, effects)
