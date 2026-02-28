N = 8

def var_to_rc(v):
    v -= 1  # back to 0-based
    r = v // 8
    c = v % 8
    return r, c

def main():
    with open("solution1.txt", "r") as f:
        tokens = f.read().split()

    if not tokens or tokens[0] != "SAT":
        print("Not SAT (or no model found). First token was:", tokens[0] if tokens else "EMPTY")
        return

    # model literals until 0; keep only positive ones
    lits = [int(x) for x in tokens[1:] if x != "0"]
    true_vars = [x for x in lits if x > 0]

    # build chess board
    board = [["." for _ in range(8)] for _ in range(8)]
    for v in true_vars:
        r, c = var_to_rc(v)
        if 0 <= r < 8 and 0 <= c < 8:
            board[r][c] = "Q"

    # print board
    for row in board:
        print(" ".join(row))

if __name__ == "__main__":
    main()