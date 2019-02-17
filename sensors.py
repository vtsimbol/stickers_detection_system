rows = 14
columns = 32
sensors = {d: range(d, d + rows * columns + 1, columns) for d in range(1, columns + 1)}
