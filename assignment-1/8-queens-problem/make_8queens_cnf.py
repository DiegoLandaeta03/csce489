def var(r, c):
    # convert board position to DIMACS variable number
    return r * 8 + c + 1

def main():
    clauses = []

    # rows
    for r in range(8):
        row = []
        for c in range(8):
            row.append(var(r, c))

        clauses.append(row)

        for i in range(8):
            for j in range(i + 1, 8):
                clauses.append([-row[i], -row[j]])

    # columns
    for c in range(8):
        column = []
        for r in range(8):
            column.append(var(r, c))

        for i in range(8):
            for j in range(i + 1, 8):
                clauses.append([-column[i], -column[j]])

    # down and right diagonals
    for r in range(8):
        for c in range(8):
            diagonal = []
            rr = r
            cc = c

            while rr < 8 and cc < 8:
                diagonal.append(var(rr, cc))
                rr += 1
                cc += 1

            for i in range(len(diagonal)):
                for j in range(i + 1, len(diagonal)):
                    clauses.append([-diagonal[i], -diagonal[j]])

    # down and left diagonals
    for r in range(8):
        for c in range(8):
            diagonal = []
            rr = r
            cc = c

            while rr < 8 and cc >= 0:
                diagonal.append(var(rr, cc))
                rr += 1
                cc -= 1

            for i in range(len(diagonal)):
                for j in range(i + 1, len(diagonal)):
                    clauses.append([-diagonal[i], -diagonal[j]])

    num_vars = 64

    f = open("queens8.cnf", "w")
    f.write("p cnf " + str(num_vars) + " " + str(len(clauses)) + "\n")

    for clause in clauses:
        for literal in clause:
            f.write(str(literal) + " ")
        f.write("0\n")

    f.close()

    print("Created queens8.cnf")

if __name__ == "__main__":
    main()