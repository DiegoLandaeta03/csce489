V = ["A","B","C","D","E","F","G","H","I","J","K","L"]
n = len(V)

def decode_model(model_lits, k):
    chosen_vertices = set()

    for lit in model_lits:
        if lit > 0:
            pos = (lit - 1) // n + 1
            i = (lit - 1) % n

            if 1 <= pos <= k:
                chosen_vertices.add(V[i])

    return sorted(list(chosen_vertices))

def main():
    model_string = "-1 -2 -3 -4 -5 -6 -7 8 -9 -10 -11 -12 -13 -14 -15 -16 -17 18 -19 -20 -21 -22 -23 -24 -25 -26 -27 28 -29 -30 -31 -32 -33 -34 -35 -36 37 -38 -39 -40 -41 -42 -43 -44 -45 -46 -47 -48 -49 -50 -51 -52 -53 -54 -55 -56 -57 -58 -59 60 -61 -62 -63 -64 -65 -66 -67 -68 69 -70 -71 -72 -73 -74 75 -76 -77 -78 -79 -80 -81 -82 -83 -84 0"
    model = [int(x) for x in model_string.split() if x != "0"]
    print(decode_model(model, 8))

if __name__ == "__main__":
    main()