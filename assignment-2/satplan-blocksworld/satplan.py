#!/usr/bin/env python3
# SatPlan for 2 blocks (A,B), horizon 2, goal On(A,B). Writes problem.cnf, optional minisat.

import os
import subprocess
import sys

# --- problem is fixed: A and B, 3 time layers 0,1,2, one action at t=0 and t=1 ---

HORIZON = 2  # states at 0,1,2

# fluents in order (each gets a var per time step)
F = [
    "OT_A",
    "OT_B",
    "OnAB",
    "OnBA",
    "Cl_A",
    "Cl_B",
    "H_A",
    "H_B",
    "HE",
]

# action name -> (pre list, add list, del list)
ACT = {
    "PickupA": (["HE", "Cl_A", "OT_A"], ["H_A"], ["HE", "OT_A"]),
    "PickupB": (["HE", "Cl_B", "OT_B"], ["H_B"], ["HE", "OT_B"]),
    "PutdownA": (["H_A"], ["HE", "OT_A", "Cl_A"], ["H_A"]),
    "PutdownB": (["H_B"], ["HE", "OT_B", "Cl_B"], ["H_B"]),
    "StackAB": (["H_A", "Cl_B"], ["OnAB", "HE"], ["H_A", "Cl_B"]),
    "StackBA": (["H_B", "Cl_A"], ["OnBA", "HE"], ["H_B", "Cl_A"]),
    "UnstackAB": (["HE", "OnAB", "Cl_A"], ["H_A", "Cl_B"], ["HE", "OnAB"]),
    "UnstackBA": (["HE", "OnBA", "Cl_B"], ["H_B", "Cl_A"], ["HE", "OnBA"]),
}

ACT_NAMES = list(ACT.keys())
nF = len(F)
nA = len(ACT_NAMES)


def S(t, name, neg=False):
    # fluent literal at time t (DIMACS index 1..n)
    v = t * nF + F.index(name) + 1
    return -v if neg else v


def Avar(t, name):
    base = (HORIZON + 1) * nF
    return base + t * nA + ACT_NAMES.index(name) + 1


def main():
    clauses = []

    # initial state at t=0
    for n in ["OT_A", "OT_B", "Cl_A", "Cl_B", "HE"]:
        clauses.append([S(0, n)])
    for n in ["OnAB", "OnBA", "H_A", "H_B"]:
        clauses.append([S(0, n, neg=True)])

    # goal On(A,B) at t=2
    clauses.append([S(HORIZON, "OnAB")])

    # mutex / extra constraints at every time
    for t in range(HORIZON + 1):
        clauses.append([S(t, "OT_A", True), S(t, "OnAB", True)])
        clauses.append([S(t, "OT_B", True), S(t, "OnBA", True)])
        clauses.append([S(t, "OnAB", True), S(t, "OnBA", True)])
        clauses.append([S(t, "H_A", True), S(t, "OnAB", True)])
        clauses.append([S(t, "H_B", True), S(t, "OnBA", True)])
        clauses.append([S(t, "H_A", True), S(t, "OT_A", True)])
        clauses.append([S(t, "H_B", True), S(t, "OT_B", True)])
        clauses.append([S(t, "OnAB", True), S(t, "Cl_B", True)])
        clauses.append([S(t, "OnBA", True), S(t, "Cl_A", True)])
        clauses.append([S(t, "H_A", True), S(t, "H_B", True)])
        # hand empty <-> not holding anything
        clauses.append([S(t, "HE", True), S(t, "H_A", True)])
        clauses.append([S(t, "HE", True), S(t, "H_B", True)])
        clauses.append([S(t, "HE", False), S(t, "H_A", False), S(t, "H_B", False)])

    # transitions
    for t in range(HORIZON):
        # exactly one action (also means we always do something at each step)
        acts = [Avar(t, n) for n in ACT_NAMES]
        clauses.append(acts)
        for i in range(nA):
            for j in range(i + 1, nA):
                clauses.append([-acts[i], -acts[j]])

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

            # frame: fluents not in add or delete stay the same if this action runs
            for x in F:
                if x in add or x in delete:
                    continue
                clauses.append([-av, S(t, x, True), S(t + 1, x)])
                clauses.append([-av, S(t, x), S(t + 1, x, True)])

    nvars = (HORIZON + 1) * nF + HORIZON * nA
    here = os.path.dirname(os.path.abspath(__file__))
    cnf_path = os.path.join(here, "problem.cnf")

    with open(cnf_path, "w", encoding="utf-8") as out:
        out.write("c tiny blocksworld satplan A B horizon 2 goal On(A,B)\n")
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
            if line == "SAT" or line.startswith("SAT "):
                status = "SAT"
            elif line.startswith("SATISFIABLE"):
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
