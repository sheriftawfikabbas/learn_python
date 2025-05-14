# print(" _ _ _\n|_|_|_|\n|_|_|_|\n|_|_|_|")

# Game state: game information during runtime
xo = [0, 0, 0]

while True:
    X = input()
    X = int(X)
    xo[X] = "X"
    grid_string = "|"
    for i in range(3):
        if xo[i] == 0:
            grid_string = grid_string + "_|"
        else:
            grid_string = grid_string + xo[i] + "|"
    print(grid_string)
