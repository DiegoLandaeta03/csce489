# Assignment 2 - Run Guide and Test Cases

## Situation Calculus — Light Switch (`situation-calculus-light-switch/`)

### Brief Description

This models a simple light switch using Situation Calculus.
There is one fluent (`On(s)`) and one action (`FlipSwitch`). The axioms show how the state changes over time.

### How to View

No code needed. Just open the writeup:

```bash
cd assignment-2/situation-calculus-light-switch
```

Then open `README.md`.

### Explanation

Initial state:

* ¬On(S0) → light starts off

After one flip:

* S1 = do(FlipSwitch, S0)
* On(S1) → light turns on

After another flip:

* S2 = do(FlipSwitch, S1)
* ¬On(S2) → light turns off again

### Why this matters

Shows how Situation Calculus represents state changes using actions and situations.

---

## SatPlan — Blocksworld (`satplan-blocksworld/`)

### Brief Description

This uses SatPlan to solve a small Blocksworld problem.
The planning problem is encoded as a SAT problem and solved using Minisat.

The setup is:

* Blocks: A, B
* Goal: On(A,B)
* Horizon: 2 steps

### How to Run

```bash
cd assignment-2/satplan-blocksworld
python3 satplan.py
```

This generates `problem.cnf`.

Then run:

```bash
minisat problem.cnf minisat.out
```

Or run both together:

```bash
python3 satplan.py --run-minisat
```

### Expected Result

* A CNF file is generated
* Minisat returns SAT
* The plan is:

```text
t=0: PickupA
t=1: StackAB
```

### Why this matters

Shows how planning can be reduced to SAT and solved using a SAT solver.

---

## Unification (`unification/unify.py`)

### Brief Description

This program attempts to unify two symbolic expressions.
If it succeeds, it prints the variable bindings and resulting expressions.
If not, it prints `not unifiable`.

### How to Run

```bash
cd assignment-2/unification
python3 unify.py "<expr1>" "<expr2>"
```

### Test Cases

1. **Command**

```bash
python3 unify.py "(likes bill ?x)" "(likes bill mary)"
```

**Expected Output**

```text
?x -> mary
(likes bill mary) = (likes bill mary)
```

**Why this matters**
Basic single-variable substitution.

---

2. **Command**

```bash
python3 unify.py "(likes ?x ?y)" "(likes bill mary)"
```

**Expected Output**

```text
?x -> bill
?y -> mary
(likes bill mary) = (likes bill mary)
```

**Why this matters**
Multiple variables unified correctly.

---

3. **Command**

```bash
python3 unify.py "(likes bill ?x)" "(likes bill (mother bill))"
```

**Expected Output**

```text
?x -> (mother bill)
(likes bill (mother bill)) = (likes bill (mother bill))
```

**Why this matters**
Handles nested expressions.

---

4. **Command**

```bash
python3 unify.py "(f ?x ?x)" "(f bill bill)"
```

**Expected Output**

```text
?x -> bill
(f bill bill) = (f bill bill)
```

**Why this matters**
Ensures the same variable is consistent.

---

5. **Command**

```bash
python3 unify.py "(f ?x ?x)" "(f bill mary)"
```

**Expected Output**

```text
not unifiable
```

**Why this matters**
Correctly detects a conflict.
