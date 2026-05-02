# Final Project - Goal Regression in Blocksworld

This project follows the goal regression (backward planning) approach
covered in lecture, using PDDL-style operators and S-expressions.

## Files

- `Sexpr.py` - provided parser from class (used as-is).
- `blocksworld.PDDL` - provided PDDL-style operators (modified slightly for consistency), including:
  - normalizing syntax (`:precondition` / `:effect`)
  - converting negation to `(not (literal))` form for compatibility with the S-expression parser
  - adding missing delete effects to better reflect standard Blocksworld behavior
- `pddl_parser.py` - reads actions from PDDL and extracts parameters/preconditions/effects.
- `planner.py` - action grounding, regression (weakest preimage), limited consistency checks, simple action ordering, and backward search.
- `main.py` - small runnable example with debug output.

## How to Run

From the repo root:

```bash
cd final-project
python3 main.py
```

## Choosing Different Presets

`main.py` includes multiple built-in test presets (different initial/goal states).

- Interactive selection:

```bash
cd final-project
python3 main.py
```

You will see a numbered menu and can type a preset number.

- Run a specific preset directly:

```bash
python3 main.py --preset 2
```

- Show available presets only:

```bash
python3 main.py --list-presets
```

## What the Program Does

1. Parses actions from `blocksworld.PDDL`.
2. Grounds actions over objects `A, B, C, table`.
3. Starts from the goal and regresses backward using:

`Regress(Goal, Action) = (Goal - Add(Action)) U Precond(Action)`

4. Uses a depth-first search over regressed goal sets with simple action ordering.
   A small depth limit and simple action ordering are used to avoid very large traces.
5. Prints the plan in normal forward order.

This regression step corresponds to computing the **weakest preimage** of the goal,
as discussed in class (i.e., the minimal conditions needed before an action
to achieve the goal after the action).

## Debug Output Explained

During search, the planner prints:

- `Current goal:` the goal set currently being expanded.
- `Action:` accepted grounded actions that are enqueued.
- `Regressed goal:` the new goal set after applying regression.
- `Node summary:` how many actions were accepted/skipped at that node.

At the end, it prints:

- `--- Final Plan ---`
- Numbered actions in forward execution order, or `No plan found.`

## Example Included in `main.py`

Initial state:

- `(ontable A)`
- `(ontable B)`
- `(clear A)`
- `(clear B)`
- `(hand-empty)`

Goal:

- `(on A B)`

Typical output plan:

1. `pickup A table`
2. `puton A B`
