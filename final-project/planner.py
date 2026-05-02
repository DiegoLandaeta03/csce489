from itertools import product


class ActionSchema:
    def __init__(self, name, parameters, preconditions, add_effects, delete_effects):
        self.name = name
        self.parameters = parameters
        self.preconditions = set(preconditions)
        self.add_effects = set(add_effects)
        self.delete_effects = set(delete_effects)


class GroundAction:
    def __init__(self, name, args, preconditions, add_effects, delete_effects):
        self.name = name
        self.args = tuple(args)
        self.preconditions = set(preconditions)
        self.add_effects = set(add_effects)
        self.delete_effects = set(delete_effects)

    def pretty(self):
        return f"{self.name} {' '.join(self.args)}"


def build_action_schemas(parsed_actions):
    schemas = []
    for a in parsed_actions:
        schemas.append(
            ActionSchema(
                name=a["name"],
                parameters=a["parameters"],
                preconditions=a["preconditions"],
                add_effects=a["add_effects"],
                delete_effects=a["delete_effects"],
            )
        )
    return schemas


def _substitute_literal(literal, assignment):
    grounded = []
    for token in literal:
        grounded.append(assignment.get(token, token))
    return tuple(grounded)


def _is_ignored_literal(literal):
    """Treat clear(table) as implicit and skip it."""
    return literal == ("clear", "table")


def _is_valid_assignment(schema, assignment):
    """
    Simple grounding rules:
    - moving block cannot be table
    - avoid actions like move(A, A)
    """
    if not schema.parameters:
        return True

    first = assignment[schema.parameters[0]]
    if first == "table":
        return False

    if len(schema.parameters) >= 2:
        second = assignment[schema.parameters[1]]
        if first == second:
            return False

    return True


def ground_actions(action_schemas, objects):
    grounded = []
    for schema in action_schemas:
        if not schema.parameters:
            grounded.append(
                GroundAction(
                    schema.name,
                    (),
                    schema.preconditions,
                    schema.add_effects,
                    schema.delete_effects,
                )
            )
            continue

        for combo in product(objects, repeat=len(schema.parameters)):
            assignment = dict(zip(schema.parameters, combo))
            if not _is_valid_assignment(schema, assignment):
                continue

            pre = {
                g
                for g in {_substitute_literal(lit, assignment) for lit in schema.preconditions}
                if not _is_ignored_literal(g)
            }
            add = {
                g
                for g in {_substitute_literal(lit, assignment) for lit in schema.add_effects}
                if not _is_ignored_literal(g)
            }
            delete = {
                g
                for g in {_substitute_literal(lit, assignment) for lit in schema.delete_effects}
                if not _is_ignored_literal(g)
            }

            grounded.append(GroundAction(schema.name, combo, pre, add, delete))
    return grounded


def regress(goal, action):
    """
    Goal regression (weakest preimage):
      Regress(Goal, Action) = (Goal - Add(Action)) U Precond(Action)
    We keep this direct and filter bad goals afterward.
    """
    return (set(goal) - action.add_effects) | action.preconditions


def is_relevant(goal, action):
    """Action is relevant if it adds at least one current goal literal."""
    return len(set(goal) & action.add_effects) > 0


def is_goal_consistent(goal):
    """
    Basic consistency checks to remove impossible goals.
    """
    on_map = {}
    clear_set = set()
    hand_empty = ("hand-empty",) in goal
    holding_set = set()

    for lit in goal:
        if lit[0] == "on" and len(lit) == 3:
            block, dest = lit[1], lit[2]
            if block in on_map and on_map[block] != dest:
                return False
            on_map[block] = dest
        elif lit[0] == "clear" and len(lit) == 2:
            clear_set.add(lit[1])
        elif lit[0] == "holding" and len(lit) == 2:
            holding_set.add(lit[1])

    # Impossible: hand empty and holding a block at the same time.
    if hand_empty and holding_set:
        return False

    # Impossible: holding two different blocks at once.
    if len(holding_set) > 1:
        return False

    for block, dest in on_map.items():
        if dest in clear_set:
            return False
        if block == dest:
            return False

    return True


def _fmt_goal(goal):
    return "{" + ", ".join(sorted([str(x) for x in goal])) + "}"


def _is_plan_executable(initial_state, plan):
    """Forward-simulate a candidate plan from the initial state."""
    state = set(initial_state)
    for action in plan:
        if not action.preconditions.issubset(state):
            return False
        state = (state - action.delete_effects) | action.add_effects
    return True


def _apply_plan(initial_state, plan):
    state = set(initial_state)
    for action in plan:
        if not action.preconditions.issubset(state):
            return None
        state = (state - action.delete_effects) | action.add_effects
    return state


def simplify_plan(initial_state, goal_state, plan):
    """
    Remove adjacent undo pairs, e.g.:
        puton X Y then pickup X Y
    if removing them still keeps a valid goal-reaching plan.
    """
    if plan is None:
        return None

    changed = True
    simplified = list(plan)
    while changed:
        changed = False
        i = 0
        while i < len(simplified) - 1:
            a1 = simplified[i]
            a2 = simplified[i + 1]
            is_inverse_pair = (
                a1.name == "puton"
                and a2.name == "pickup"
                and len(a1.args) == 2
                and len(a2.args) == 2
                and a1.args[0] == a2.args[0]
                and a1.args[1] == a2.args[1]
            )
            if not is_inverse_pair:
                i += 1
                continue

            candidate = simplified[:i] + simplified[i + 2 :]
            end_state = _apply_plan(initial_state, candidate)
            if end_state is not None and set(goal_state).issubset(end_state):
                simplified = candidate
                changed = True
                break
            i += 1

    return simplified


def _adjust_regressed_goal(current_goal, regressed_goal, action, protected_goals):
    """
    Remove deleted helper goals while keeping the original goal protected.
    """
    removable = (set(current_goal) & action.delete_effects) - set(protected_goals)
    return set(regressed_goal) - removable


def _action_priority(action, goal, regressed_goal, initial_state, protected_goals):
    """
    Lightweight ordering so search stays manageable.
    Higher score = try earlier.
    """
    goal = set(goal)
    score = 0

    # Prefer actions that directly achieve current goals.
    score += 10 * len(action.add_effects & goal)

    # If we need clear(X), prefer pickup(Y, X) when plausible.
    if action.name == "pickup" and len(action.args) == 2:
        block, target = action.args
        plausible_unstack = ("on", block, target) in initial_state or ("on", block, target) in goal
        if ("clear", target) in goal and plausible_unstack:
            score += 20
        # Extra boost for exact unstack seen in initial state.
        if ("on", block, target) in initial_state:
            score += 6

    # If holding X is in goal, putting X on table is often useful.
    if action.name == "puton" and len(action.args) == 2 and action.args[1] == "table":
        block = action.args[0]
        if ("holding", block) in goal:
            score += 15
        # If initial state has on(block, T) and we need clear(T), this helps.
        for lit in goal:
            if len(lit) == 2 and lit[0] == "clear":
                target = lit[1]
                if ("on", block, target) in initial_state:
                    score += 25

    # Prefer regressed goals closer to initial state.
    missing_after_regression = len(set(regressed_goal) - set(initial_state))
    score -= missing_after_regression

    # Penalize circular regressions that keep protected goals around.
    score -= 12 * len(set(regressed_goal) & set(protected_goals))

    return score


def backward_search(initial_state, goal_state, grounded_actions, max_depth=8, max_branching=2):
    """
    Backward search over regressed goals (weakest preimage).
    Uses DFS order + simple action ranking.
    """
    initial_state = set(initial_state)
    protected_goals = set(goal_state)
    start_goal = frozenset(goal_state)
    # DFS stack using the current action order.
    frontier = [(start_goal, [])]  # (current_goal, forward_plan_so_far)
    visited = {start_goal}
    step = 0

    while frontier:
        current_goal, plan = frontier.pop()
        step += 1

        print()
        print("*" * 70)
        print(f"Search node {step}")
        print("Current goal:", _fmt_goal(current_goal))
        print("*" * 70)
        if set(current_goal).issubset(initial_state):
            if _is_plan_executable(initial_state, plan):
                print("Reached initial-state subset and plan is executable.")
                return plan
            print("Reached initial-state subset but plan is not executable (skipping).")
            continue

        if len(plan) >= max_depth:
            print(f"Depth limit reached ({max_depth}); skipping expansion.")
            continue

        relevant_actions = [a for a in grounded_actions if is_relevant(current_goal, a)]

        skipped_inconsistent = 0
        skipped_visited = 0
        skipped_resource_conflict = 0
        skipped_low_priority = 0
        accepted = 0
        candidates = []

        for action in relevant_actions:
            # If hand-empty is required, skip actions that break it.
            if (
                ("hand-empty",) in current_goal
                and ("hand-empty",) in action.delete_effects
                and ("hand-empty",) not in action.add_effects
            ):
                skipped_resource_conflict += 1
                continue

            regressed = regress(current_goal, action)
            regressed = _adjust_regressed_goal(
                current_goal, regressed, action, protected_goals
            )

            if not is_goal_consistent(regressed):
                skipped_inconsistent += 1
                continue

            regressed_frozen = frozenset(regressed)
            if regressed_frozen in visited:
                skipped_visited += 1
                continue

            priority = _action_priority(
                action, current_goal, regressed, initial_state, protected_goals
            )
            candidates.append((priority, len(regressed), action, regressed, regressed_frozen))

        candidates.sort(key=lambda x: (-x[0], x[1], x[2].pretty()))
        if len(candidates) > max_branching:
            skipped_low_priority = len(candidates) - max_branching

        chosen = candidates[:max_branching]
        for priority, _, action, regressed, regressed_frozen in chosen:
            print()
            print(f"  Action: {action.pretty()}")
            print("    Regressed goal:", _fmt_goal(regressed))
            print("    Status: accepted (enqueue)")
            accepted += 1
            visited.add(regressed_frozen)
        # Reverse so best-ranked action is popped first next loop.
        for _, _, action, regressed, regressed_frozen in reversed(chosen):
            frontier.append((regressed_frozen, [action] + plan))

        print(
            f"Node summary: accepted={accepted}, "
            f"skipped_inconsistent={skipped_inconsistent}, "
            f"skipped_visited={skipped_visited}, "
            f"skipped_resource_conflict={skipped_resource_conflict}, "
            f"skipped_low_priority={skipped_low_priority}"
        )

    return None
