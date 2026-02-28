V = ["A","B","C","D","E","F","G","H","I"]
n = len(V)

def decode_model(model_lits, k):
    chosen = {}
    for lit in model_lits:
        if lit > 0:
            pos = (lit - 1) // n + 1
            i = (lit - 1) % n
            chosen[pos] = V[i]
    return [chosen[p] for p in sorted(chosen)]

def main():
    model_string = "-1 -2 3 -4 -5 -6 -7 -8 -9 -10 -11 -12 13 -14 -15 -16 -17 -18 -19 -20 -21 -22 -23 24 -25 -26 -27 -28 -29 -30 -31 32 -33 -34 -35 -36 0"
    model = [int(x) for x in model_string.split() if x != "0"]
    print(decode_model(model, 4))

if __name__ == "__main__":
    main()