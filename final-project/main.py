import argparse

from pddl_parser import parse_blocksworld_actions
from planner import build_action_schemas, ground_actions, backward_search, simplify_plan


PRESETS = {
    "1": {
        "label": "A and B on table -> goal: on(A, B)",
        "initial_state": {
            ("ontable", "A"),
            ("ontable", "B"),
            ("clear", "A"),
            ("clear", "B"),
            ("hand-empty",),
        },
        "goal_state": {("on", "A", "B")},
    },
    "2": {
        "label": "A on table, B on C -> goal: on(A, C)",
        "initial_state": {
            ("ontable", "A"),
            ("on", "B", "C"),
            ("ontable", "C"),
            ("clear", "A"),
            ("clear", "B"),
            ("hand-empty",),
        },
        "goal_state": {("on", "A", "C")},
    },
    "3": {
        "label": "Goal already satisfied: on(A, B)",
        "initial_state": {
            ("on", "A", "B"),
            ("ontable", "B"),
            ("clear", "A"),
            ("hand-empty",),
        },
        "goal_state": {("on", "A", "B")},
    },
}


def normalize_state_literals(literals):
    """
    Small helper for this project:
    convert (ontable X) into (on X table) so it matches operator preconditions.
    """
    normalized = set(literals)
    for lit in list(literals):
        if len(lit) == 2 and lit[0] == "ontable":
            normalized.add(("on", lit[1], "table"))
    return normalized


def _print_preset_options():
    print("\nAvailable presets:")
    for key in sorted(PRESETS.keys()):
        print(f"  {key}. {PRESETS[key]['label']}")


def choose_preset(preset_arg=None):
    if preset_arg:
        preset_id = preset_arg.strip()
        if preset_id not in PRESETS:
            print(f"Unknown preset '{preset_id}'. Falling back to preset 1.")
            return "1"
        return preset_id

    _print_preset_options()
    choice = input("\nChoose a preset number [default: 1]: ").strip()
    if not choice:
        return "1"
    if choice not in PRESETS:
        print(f"Unknown preset '{choice}'. Falling back to preset 1.")
        return "1"
    return choice


def main():
    parser = argparse.ArgumentParser(description="Goal Regression planner demo")
    parser.add_argument(
        "--preset",
        help="Preset number (1, 2, or 3). If omitted, terminal prompt is shown.",
    )
    parser.add_argument(
        "--list-presets",
        action="store_true",
        help="Show preset list and exit.",
    )
    args = parser.parse_args()

    if args.list_presets:
        _print_preset_options()
        return

    preset_id = choose_preset(args.preset)
    preset = PRESETS[preset_id]

    pddl_path = "blocksworld.PDDL"
    parsed = parse_blocksworld_actions(pddl_path)
    schemas = build_action_schemas(parsed)

    objects = ["A", "B", "C", "table"]
    grounded = ground_actions(schemas, objects)

    initial_state = set(preset["initial_state"])
    initial_state = normalize_state_literals(initial_state)
    goal_state = set(preset["goal_state"])

    print("\nSelected preset:", preset_id)
    print("Description:", preset["label"])

    if goal_state.issubset(initial_state):
        print("\nGoal is already satisfied in the initial state.")
        plan = []
    else:
        plan = backward_search(initial_state, goal_state, grounded, max_depth=8, max_branching=2)
        plan = simplify_plan(initial_state, goal_state, plan)

    print("\n--- Final Plan ---")
    if plan is None:
        print("No plan found.")
        return
    if len(plan) == 0:
        print("No actions needed.")
        return

    for i, action in enumerate(plan, start=1):
        print(f"{i}. {action.pretty()}")


if __name__ == "__main__":
    main()
