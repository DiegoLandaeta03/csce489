V = ["A","B","C","D","E","F","G","H","I","J","K","L"]
n = len(V)

# build idx (A->1)
idx = {}
for i in range(n):
    idx[V[i]] = i + 1

E = set([
    ("A","B"), ("B","A"),
    ("A","G"), ("G","A"),
    ("A","H"), ("H","A"),

    ("B","C"), ("C","B"),
    ("B","I"), ("I","B"),

    ("C","D"), ("D","C"),
    ("C","K"), ("K","C"),

    ("D","E"), ("E","D"),
    ("D","K"), ("K","D"),

    ("E","F"), ("F","E"),
    ("E","L"), ("L","E"),

    ("F","G"), ("G","F"),
    ("F","L"), ("L","F"),

    ("G","H"), ("H","G"),

    ("H","J"), ("J","H"),

    ("I","J"), ("J","I"),
    ("I","K"), ("K","I"),

    ("J","L"), ("L","J"),
])

unique_edges = []
seen = set()
for (u, v) in E:
    if (v, u) in seen:
        continue
    seen.add((u, v))
    unique_edges.append((u, v))

def var(v, pos, k):
    # pos = 1..k, variables = 1..(n*k)
    return (pos - 1) * n + idx[v]

def write_dimacs(filename, num_vars, clauses):
    f = open(filename, "w")
    f.write("p cnf " + str(num_vars) + " " + str(len(clauses)) + "\n")

    for clause in clauses:
        for lit in clause:
            f.write(str(lit) + " ")
        f.write("0\n")

    f.close()

def build_vertex_cover_cnf(k):
    clauses = []

    # each position chooses exactly one vertex
    for pos in range(1, k + 1):

        # at least one vertex in this position
        atleast = []
        for v in V:
            atleast.append(var(v, pos, k))
        clauses.append(atleast)

        # at most one vertex in this position (pairwise)
        for i in range(n):
            for j in range(i + 1, n):
                u = V[i]
                v = V[j]
                clauses.append([-var(u, pos, k), -var(v, pos, k)])

    # no vertex can appear in two different positions
    for v in V:
        for p in range(1, k + 1):
            for q in range(p + 1, k + 1):
                clauses.append([-var(v, p, k), -var(v, q, k)])

    # every edge must be covered:
    # meaning: for edge (u, v), u is chosen somewhere or v is chosen somewhere
    for (u, v) in unique_edges:
        clause = []

        # u chosen in any position
        for pos in range(1, k + 1):
            clause.append(var(u, pos, k))

        # v chosen in any position
        for pos in range(1, k + 1):
            clause.append(var(v, pos, k))

        clauses.append(clause)

    num_vars = n * k
    return num_vars, clauses

if __name__ == "__main__":
    ks = [6, 7, 8]
    for k in ks:
        nv, cls = build_vertex_cover_cnf(k)
        out = "vc_" + str(k) + ".cnf"
        write_dimacs(out, nv, cls)
        print("Wrote", out)