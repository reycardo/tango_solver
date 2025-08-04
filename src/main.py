from utils.tools import get_txt_files, read_input, timing_decorator
from utils.colors import magenta_color, reset_color
from utils.tools import Point, Grid, Vectors

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
