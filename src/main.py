from utils.tools import get_txt_files, read_input, timing_decorator
from utils.colors import magenta_color, reset_color
from utils.tools import Point, Grid, Vectors


from enum import Enum

class Symbol(Enum):
    Sun = "S"
    Moon = "M"
    opposite_up = "u"
    opposite_down = "d"
    opposite_left = "l"
    opposite_right = "r"
    equal_up = "U"
    equal_down = "D"
    equal_left = "L"
    equal_right = "R"

files = get_txt_files(__file__)

class Puzzle:
    def __init__(self, text_input):
        self.input = text_input
        self.grid = Grid(self.input)
        pass

    def rule_1(self):
        # Example: enforce 3 adjacent rows/columns cannot have the same value
        for i in range(len(self.grid) - 2):
            if self.grid[i] == self.grid[i + 1] == self.grid[i + 2]:
                return False
        return True
    
    def rule_2(self):
        # Example: enforce maximum of 3 S and 3 M in any row/column
        for i in range(len(self.grid)):
            if self.grid[i].count('S') > 3 or self.grid[i].count('M') > 3:
                return False
        return True
    
    def solve_use_case_1(self):
        changed = False
        for r in range(len(self.grid)):
            for c in range(len(self.grid[0]) - 2):
                a, b, c_ = self.grid[r][c], self.grid[r][c+1], self.grid[r][c+2]
                if a == b != '_' and c_ == '_':
                    self.grid[r][c+2] = 'M' if a == 'S' else 'S'
                    changed = True
                if b == c_ != '_' and a == '_':
                    self.grid[r][c] = 'M' if b == 'S' else 'S'
                    changed = True
        # Repeat for columns
        for c in range(len(self.grid[0])):
            for r in range(len(self.grid) - 2):
                a, b, c_ = self.grid[r][c], self.grid[r+1][c], self.grid[r+2][c]
                if a == b != '_' and c_ == '_':
                    self.grid[r+2][c] = 'M' if a == 'S' else 'S'
                    changed = True
                if b == c_ != '_' and a == '_':
                    self.grid[r][c] = 'M' if b == 'S' else 'S'
                    changed = True
        return changed

    def solve(self):
        pass

@timing_decorator
def main(raw):
    text_input = read_input(raw)
    input_parsed = [i if i else "" for i in text_input]
    puzzle = Puzzle(input_parsed)
    return puzzle.solve()


def run_tests():
    print(f"\nRunning Tests:")
    assert main(raw=files["test"]) == 18
    assert main(raw=files["test"]) == 9

    # solutions
    print(f"\nRunning Solutions:")
    assert main(raw=files["input"]) == 2547
    assert main(raw=files["input"]) == 1939


def solve():
    print(f"\nSolving:")
    answer1 = main(raw=files["input"])
    print(f"Answer part1: {magenta_color}{answer1}{reset_color}")
    answer2 = main(raw=files["input"])
    print(f"Answer part2: {magenta_color}{answer2}{reset_color}")


if __name__ == "__main__":
    run_tests()
    solve()
