# SatPlan blocksworld (A and B)

**Assignment task:** Use SatPlan to solve planning problems in Blocksworld (or another domain) by encoding as a Boolean formula and using Minisat to generate a model.

My version is only blocksworld with A and B: I built the CNF in `satplan.py`, ran minisat, and read the plan off the satisfying assignment. Not a general planner.

## Setup

Blocks A and B. Start: both on the table, both clear, hand empty. Goal: A on B (`On(A,B)`). Horizon is 2 so we have states at t=0,1,2 and we pick an action at t=0 and t=1.

Actions are the grounded ones you would expect: pickup/putdown for each block, stack/unstack for both orders. Preconditions and effects are in `satplan.py` in the `ACT` dict.

## How I encoded it

Each fluent gets a variable per time step (on table, on other block, clear, holding, hand empty, same idea as the notes). Each grounded action gets a variable at t=0 and t=1.

CNF has: start state, goal at t=2, exactly one action each step, implications for preconditions and effects, frame axioms for fluents that do not change, plus a few mutex clauses so we do not get nonsense like A on the table and on B at once. Output is normal DIMACS (`p cnf ...`).

## Running it

```bash
cd assignment-2/satplan-blocksworld
python3 satplan.py
```

Writes `problem.cnf` next to the script.

```bash
python3 satplan.py --run-minisat
```

Same but also runs minisat and prints `SAT` and the plan on stdout. Plan should be PickupA then StackAB.

If you already have the cnf:

```bash
minisat problem.cnf minisat.out
```

Need minisat installed (I used homebrew on mac). Exit 10 = SAT, 20 = UNSAT for the minisat I have.

## minisat.out

That is just minisat's answer file: `SAT` or `UNSAT`, and if SAT a line of literals ending in 0. I am including it as proof the instance is satisfiable.

## Files in here

- `satplan.py`: builds the CNF  
- `problem.cnf`: DIMACS from the script  
- `minisat.out`: minisat output (also written if you use `python3 satplan.py --run-minisat`)
