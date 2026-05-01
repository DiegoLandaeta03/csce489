#!/usr/bin/env python3
# SatPlan for 3 blocks (A,B,C), horizon 4.
# Initial: A on B, C alone. Goal: A alone, B on C.

import os
import subprocess
import sys

BLOCKS = ["A", "B", "C"]
HORIZON = 4  # states at 0..4, actions at 0..3

F = []
for b in BLOCKS:
    F.append(f"OT_{b}")
for x in BLOCKS:
    for y in BLOCKS:
        if x != y:
            F.append(f"On{x}{y}")
for b in BLOCKS:
    F.append(f"Cl_{b}")
for b in BLOCKS:
    F.append(f"H_{b}")
F.append("HE")


def on_name(x, y):
    return f"On{x}{y}"


ACT = {}
for b in BLOCKS:
    ACT[f"Pickup{b}"] = ([f"HE", f"Cl_{b}", f"OT_{b}"], [f"H_{b}"], [f"HE", f"OT_{b}"])
    ACT[f"Putdown{b}"] = ([f"H_{b}"], [f"HE", f"OT_{b}", f"Cl_{b}"], [f"H_{b}"])

for x in BLOCKS:
    for y in BLOCKS:
        if x == y:
            continue
        ACT[f"Stack{x}{y}"] = ([f"H_{x}", f"Cl_{y}"], [on_name(x, y), "HE"], [f"H_{x}", f"Cl_{y}"])
        ACT[f"Unstack{x}{y}"] = (
            ["HE", on_name(x, y), f"Cl_{x}"],
            [f"H_{x}", f"Cl_{y}"],
            ["HE", on_name(x, y)],
        )

ACT_NAMES = list(ACT.keys())
nF = len(F)
nA = len(ACT_NAMES)

table = set()

def S(t, name, neg=False):
    # Fluent literal at time t (DIMACS index 1..n)
    v = t * nF + F.index(name) + 1
    # tableEntry = "", t, name, neg, v
    # if tableEntry not in table:
    #     print(t, name, neg, v)   
    # table.add(tableEntry)
    return -v if neg else v

def Avar(t, name):
    base = (HORIZON + 1) * nF
    entryAction = base + t * nA + ACT_NAMES.index(name) + 1
    tableEntry = "", t, name, entryAction
    if tableEntry not in table:
        print(t, name, entryAction)   
    table.add(tableEntry)
    return base + t * nA + ACT_NAMES.index(name) + 1


def add_pairwise_at_most_one(clauses, lits):
    for i in range(len(lits)):
        for j in range(i + 1, len(lits)):
            clauses.append([-lits[i], -lits[j]])


def main():
    clauses = []

    # Initial state at t=0:
    # A on B, C by itself, hand empty.
    init_true = ["OnAB", "OT_B", "OT_C", "Cl_A", "Cl_C", "HE"]
    init_false = [
        "OT_A",
        "OnAC",
        "OnBA",
        "OnBC",
        "OnCA",
        "OnCB",
        "Cl_B",
        "H_A",
        "H_B",
        "H_C",
    ]
    for n in init_true:
        clauses.append([S(0, n)])
    for n in init_false:
        clauses.append([S(0, n, neg=True)])

    # Goal at t=HORIZON:
    # A by itself and B on C.
    clauses.append([S(HORIZON, "OT_A")])
    clauses.append([S(HORIZON, "Cl_A")])
    clauses.append([S(HORIZON, "OnBC")])

    # Mutex / structural constraints at every time.
    for t in range(HORIZON + 1):
        # For each block X: at most one support among table / another block.
        for x in BLOCKS:
            supports = [S(t, f"OT_{x}")]
            for y in BLOCKS:
                if x != y:
                    supports.append(S(t, on_name(x, y)))
            add_pairwise_at_most_one(clauses, supports)

        # Nothing can be on two different blocks at once.
        for y in BLOCKS:
            on_y = [S(t, on_name(x, y)) for x in BLOCKS if x != y]
            add_pairwise_at_most_one(clauses, on_y)

        # If X is on Y, then Y is not clear.
        for x in BLOCKS:
            for y in BLOCKS:
                if x != y:
                    clauses.append([S(t, on_name(x, y), True), S(t, f"Cl_{y}", True)])

        # If holding X, X is not on table or on another block.
        for x in BLOCKS:
            clauses.append([S(t, f"H_{x}", True), S(t, f"OT_{x}", True)])
            for y in BLOCKS:
                if x != y:
                    clauses.append([S(t, f"H_{x}", True), S(t, on_name(x, y), True)])

        # Hand-empty consistency and at most one held block.
        held = [S(t, "H_A"), S(t, "H_B"), S(t, "H_C")]
        add_pairwise_at_most_one(clauses, held)
        clauses.append([S(t, "HE"), S(t, "H_A"), S(t, "H_B"), S(t, "H_C")])
        for h in ["H_A", "H_B", "H_C"]:
            clauses.append([S(t, "HE", True), S(t, h, True)])

    # Transitions
    for t in range(HORIZON):
        # Exactly one action at each step.
        acts = [Avar(t, n) for n in ACT_NAMES]
        clauses.append(acts)
        add_pairwise_at_most_one(clauses, acts)

        for aname in ACT_NAMES:
            pre, add, delete = ACT[aname]
            add = set(add)
            delete = set(delete)
            av = Avar(t, aname)

            for p in pre:
                clauses.append([-av, S(t, p)])

            for x in add:
                clauses.append([-av, S(t + 1, x)])

            for x in delete:
                clauses.append([-av, S(t + 1, x, True)])

            # Frame: unaffected fluents persist.
            for x in F:
                if x in add or x in delete:
                    continue
                clauses.append([-av, S(t, x, True), S(t + 1, x)])
                clauses.append([-av, S(t, x), S(t + 1, x, True)])

    nvars = (HORIZON + 1) * nF + HORIZON * nA
    here = os.path.dirname(os.path.abspath(__file__))
    cnf_path = os.path.join(here, "problem.cnf")

    with open(cnf_path, "w", encoding="utf-8") as out:
        out.write("c blocksworld satplan A,B,C horizon 4 goal: OT_A and OnBC\n")
        out.write("p cnf %d %d\n" % (nvars, len(clauses)))
        for c in clauses:
            out.write(" ".join(str(x) for x in c) + " 0\n")

    print("Wrote %s (%d vars, %d clauses)" % (cnf_path, nvars, len(clauses)))

    if "--run-minisat" not in sys.argv:
        return

    res_path = os.path.join(here, "minisat.out")
    with open(os.devnull, "wb") as dn:
        rc = subprocess.call(
            ["minisat", "-verb=0", cnf_path, res_path],
            stdout=dn,
            stderr=dn,
        )

    if rc not in (10, 20):
        print("minisat weird exit code:", rc, file=sys.stderr)
        sys.exit(rc)

    status = None
    model = {}
    with open(res_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line == "SAT" or line.startswith("SAT ") or line.startswith("SATISFIABLE"):
                status = "SAT"
            elif line.startswith("UNSAT"):
                status = "UNSAT"
            elif line[0] in "-0123456789":
                for part in line.split():
                    if part == "0":
                        break
                    v = int(part)
                    if v > 0:
                        model[v] = True
                    else:
                        model[-v] = False

    print(status)
    if status != "SAT" or not model:
        print("No plan.")
        return

    print("Plan:")
    for t in range(HORIZON):
        for aname in ACT_NAMES:
            if model.get(Avar(t, aname)):
                print("  t=%d: %s" % (t, aname))
                break


if __name__ == "__main__":
    main()