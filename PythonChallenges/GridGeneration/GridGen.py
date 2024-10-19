import random
import numpy as np

def generate_grid():
    return np.random.randint(1, 10, (6, 6))

def highlight_even_sums(grid):
    rows, cols = grid.shape

    print("Generated 6x6 Grid:")
    print(grid)
    print("\nHighlighted Rows and Columns with Even Sums:\n")

    # Check row sums
    for i in range(rows):
        row_sum = np.sum(grid[i, :])
        if row_sum % 2 == 0:
            print(f"Row {i+1}: {grid[i, :]}, Sum: {row_sum}")

    # Check column sums
    for j in range(cols):
        col_sum = np.sum(grid[:, j])
        if col_sum % 2 == 0:
            print(f"Column {j+1}: {grid[:, j]}, Sum: {col_sum}")

if __name__ == "__main__":
    grid = generate_grid()
    highlight_even_sums(grid)
