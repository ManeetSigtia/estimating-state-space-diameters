from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class SASVariable:
    name: str
    var_id: int
    range_size: int
    atom_names: List[str]


@dataclass
class SASOperator:
    name: str
    cost: int
    preconditions: List[Tuple[int, int]]  # (var_id, val)
    effects: List[Tuple[int, int, List[Tuple[int, int]]]]  # (var_id, val, conditions)

    def is_applicable(self, state: Tuple[int, ...]) -> bool:
        """Checks if this operator can be applied to the given state."""
        for var_id, val in self.preconditions:
            if state[var_id] != val:
                return False
        return True

    def apply(self, state: Tuple[int, ...]) -> Tuple[int, ...]:
        """Returns a NEW state resulting from applying this operator."""
        new_state = list(state)  # Create a mutable copy

        for var_id, new_val, conditions in self.effects:
            # Check if this specific effect's conditions are met
            # If conditions is empty, this loop is skipped and trigger remains True
            trigger = True
            for cond_var, cond_val in conditions:
                if state[cond_var] != cond_val:
                    trigger = False
                    break

            # Only apply the change if all conditions were met
            if trigger:
                new_state[var_id] = new_val

        return tuple(new_state)


@dataclass
class SASProblem:
    version: int
    metric: bool
    variables: List[SASVariable]
    initial_state: Tuple[int, ...]
    # Goal should not change midway, hence is declared as tuple (immutable). Also allows hashing later on
    goal: Tuple[Tuple[int, int], ...]
    operators: List[SASOperator]
    mutex_groups: List = field(default_factory=list)
