V = ["A","B","C","D","E","F","G","H","I"]

E = set([
    ("A","C"), ("C","A"),
    ("A","E"), ("E","A"),

    ("B","C"), ("C","B"),
    ("B","D"), ("D","B"),
    ("B","H"), ("H","B"),

    ("C","D"), ("D","C"),
    ("C","E"), ("E","C"),
    ("C","F"), ("F","C"),

    ("D","E"), ("E","D"),
    ("D","F"), ("F","D"),

    ("E","F"), ("F","E"),
    ("E","G"), ("G","E"),
    ("E","I"), ("I","E"),

    ("F","G"), ("G","F"),
    ("F","H"), ("H","F"),

    ("G","H"), ("H","G"),
    ("G","I"), ("I","G"),

    ("H","I"), ("I","H"),
])

n = len(V)

# map vertex name -> 1..n
idx = {}
for i in range(n):
    idx[V[i]] = i + 1

def var(v, pos, k):
    # pos is 1..k, variables are 1..n*k
    return (pos - 1) * n + idx[v]

def write_dimacs(filename, num_vars, clauses):
    f = open(filename, "w")
    f.write("p cnf " + str(num_vars) + " " + str(len(clauses)) + "\n")
    for clause in clauses:
        for lit in clause:
            f.write(str(lit) + " ")
        f.write("0\n")
    f.close()

def build_clique_cnf(k):
    clauses = []

    # each position has exactly one vertex
    for pos in range(1, k + 1):

        # at least one vertex at this position
        atleast = []
        for v in V:
            atleast.append(var(v, pos, k))
        clauses.append(atleast)

        # at most one vertex at this position
        for i in range(n):
            for j in range(i + 1, n):
                u = V[i]
                v = V[j]
                clauses.append([-var(u, pos, k), -var(v, pos, k)])

    # vertex can't be used twice (across positions)
    for v in V:
        for p in range(1, k + 1):
            for q in range(p + 1, k + 1):
                clauses.append([-var(v, p, k), -var(v, q, k)])

    # if two vertices are chosen in different positions, they must be connected by an edge
    # for every pair (u,v) that is not an edge, don't choose either
    for i in range(n):
        for j in range(i + 1, n):
            u = V[i]
            v = V[j]

            # if there is no edge between u and v
            if (u, v) not in E:
                for p in range(1, k + 1):
                    for q in range(p + 1, k + 1):
                        clauses.append([-var(u, p, k), -var(v, q, k)])
                        clauses.append([-var(v, p, k), -var(u, q, k)])

    num_vars = n * k
    return num_vars, clauses

if __name__ == "__main__":
    ks = [4, 5]
    for k in ks:
        num_vars, clauses = build_clique_cnf(k)
        write_dimacs("clique_" + str(k) + ".cnf", num_vars, clauses)
        print("Wrote clique_" + str(k) + ".cnf")