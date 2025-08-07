
from utils.tools import get_txt_files, read_input, timing_decorator
from utils.colors import magenta_color, reset_color
from utils.tools import Point, Grid, Vectors
from rich.live import Live
from rich.table import Table
from rich.console import Console
from rich import box
import time

from enum import Enum

class Symbol(Enum):
    Empty = "0"
    Sun = "S"
    Moon = "M"
    equal_up = "u"
    equal_down = "d"
    equal_left = "l"
    equal_right = "r"
    opposite_up = "U"
    opposite_down = "D"
    opposite_left = "L"
    opposite_right = "R"

    @property
    def emoji(self):
        if self == Symbol.Sun:
            return "☀️"
        elif self == Symbol.Moon:
            return "🌙"
        elif self == Symbol.Empty:
            return ""
        else:
            return str(self.value)

files = get_txt_files(__file__)

class Puzzle:
    def __init__(self, text_input):
        self.input = [list(row) for row in text_input]
        self.grid = Grid(self.input)
        self._step = 0
        pass
    
    def solve_adjacent_rule(self, line):
        """
        For a given line (list), if two adjacent symbols are equal and not empty,
        set the symbol adjacent to the edge(s) of those two to the opposite symbol,
        if that cell is empty.
        Example:
        [0, S, S, 0, 0, M] -> [M, S, S, M, 0, M]
        """
        changed = False
        n = len(line)
        result = list(line)  # Copy to avoid in-place issues

        for i in range(n - 1):
            if result[i] in ("S", "M") and result[i] == result[i + 1]:
                # Check left edge
                if i - 1 >= 0 and result[i - 1] not in ("S", "M"):
                    result[i - 1] = "M" if result[i] == "S" else "S"
                    changed = True
                # Check right edge
                if i + 2 < n and result[i + 2] not in ("S", "M"):
                    result[i + 2] = "M" if result[i] == "S" else "S"
                    changed = True
        return result, changed
    
    def solve_middle_rule(self, line):
        """
        For a given line (list), if there are two identical symbols with a 0 between them,
        set the 0 to the opposite symbol.
        Example:
        [0, S, 0, S, 0, 0] -> [0, S, M, S, 0, 0]
        """
        changed = False
        n = len(line)
        result = list(line)  # Copy to avoid in-place issues

        for i in range(1, n - 1):
            if (
                result[i] not in ("S", "M")
                and result[i - 1] in ("S", "M")
                and result[i + 1] == result[i - 1]
            ):
                result[i] = "M" if result[i - 1] == "S" else "S"
                changed = True
        return result, changed

    def solve_3_rule(self, line):
        """
        For a given line (list), if there are already 3 symbols of the same type,
        the other 0s should be set to the opposite symbol.
        Example:
        [0, S, 0, S, 0, S] -> [M, S, M, S, M, S]
        """
        changed = False
        result = list(line)
        count_s = result.count("S")
        count_m = result.count("M")
        # Assuming 3 is the max allowed for each symbol in a line
        max_count = 3
        if count_s == max_count:
            for i in range(len(result)):
                if result[i] not in ("S", "M"):
                    result[i] = "M"
                    changed = True
        elif count_m == max_count:
            for i in range(len(result)):
                if result[i] not in ("S", "M"):
                    result[i] = "S"
                    changed = True
        return result, changed

    def solve_comparison_rule(self, line, orientation):
        """        
        Example:
        ([0, S, l, 0, 0, 0], "horizontal") -> ([0, S, S, 0, 0, 0], "horizontal")
        ([0, S, L, 0, 0, 0], "horizontal") -> ([0, S, M, 0, 0, 0], "horizontal")
        ([0, r, S, 0, 0, 0], "horizontal") -> ([0, S, S, 0, 0, 0], "horizontal")
        ([0, R, S, 0, 0, 0], "horizontal") -> ([0, M, S, 0, 0, 0], "horizontal")

        ([0, S, u, 0, 0, 0], "vertical") -> ([0, S, S, 0, 0, 0], "vertical")
        ([0, S, U, 0, 0, 0], "vertical") -> ([0, S, M, 0, 0, 0], "vertical")
        ([0, d, S, 0, 0, 0], "vertical") -> ([0, S, S, 0, 0, 0], "vertical")
        ([0, D, S, 0, 0, 0], "vertical") -> ([0, M, S, 0, 0, 0], "vertical")        
        
        For a given line (list), if a comparison symbol (l, r, u, d, L, R, U, D) is found,
        set the adjacent cell in the direction according to the rule:
        - lowercase: set to the same as the reference symbol
        - uppercase: set to the opposite of the reference symbol

        orientation: "horizontal" or "vertical"
        """
        changed = False
        n = len(line)
        result = list(line)  # Copy to avoid in-place issues

        # Define direction offsets for horizontal and vertical
        if orientation == "horizontal":
            directions = {
                "l": -1, "L": -1,  # look left
                "r": 1,  "R": 1,   # look right
            }
        elif orientation == "vertical":
            directions = {
                "u": -1, "U": -1,  # look up
                "d": 1,  "D": 1,   # look down
            }
        else:
            raise ValueError("orientation must be 'horizontal' or 'vertical'")

        for i in range(n):
            val = result[i]
            if val in directions:
                ref_idx = i + directions[val]
                if 0 <= ref_idx < n and result[ref_idx] in ("S", "M"):
                    if val.islower():
                        # Mimic the reference symbol
                        result[i] = result[ref_idx]
                    else:
                        # Use the opposite symbol
                        result[i] = "M" if result[ref_idx] == "S" else "S"
                    changed = True

        return result, changed

    def solve_row_and_col_adjacent_rules(self, live=None):
        changed = False        
        # Solve for all rows
        for y in range(self.grid._height):
            row = [self.grid.value_at_point(Point(x, y)) for x in range(self.grid._width)]
            new_row, row_changed = self.solve_adjacent_rule(row)
            new_row, middle_changed = self.solve_middle_rule(new_row)
            new_row, comparison_changed = self.solve_comparison_rule(new_row, "horizontal")
            new_row, rule3_changed = self.solve_3_rule(new_row)
            if row_changed or middle_changed or comparison_changed or rule3_changed:
                self.grid.swap_line(axis="row", index=y, new_line=new_row)
                changed = True
                self._step += 1
                if live:
                    live.update(self.grid_to_table(highlight=("row", y)))
                    time.sleep(3)
        # Solve for all columns
        for x in range(self.grid._width):
            col = [self.grid.value_at_point(Point(x, y)) for y in range(self.grid._height)]
            new_col, col_changed = self.solve_adjacent_rule(col)
            new_col, middle_changed = self.solve_middle_rule(new_col)
            new_col, comparison_changed = self.solve_comparison_rule(new_col, "vertical")
            new_col, rule3_changed = self.solve_3_rule(new_col)
            if col_changed or middle_changed or comparison_changed or rule3_changed:
                self.grid.swap_line(axis="col", index=x, new_line=new_col)
                changed = True
                self._step += 1
                if live:
                    live.update(self.grid_to_table(highlight=("col", x)))
                    time.sleep(3)
        return changed

    def grid_to_table(self, highlight=None):
        """
        highlight: tuple ('row' or 'col', index) or None
        Uses fake borders for the highlighted row or column.
        """
        table = Table(
            title=f"Tango step {self._step}",
            show_header=False,
            show_lines=True,
            box=box.DOUBLE,
        )
        for _ in range(self.grid._width):
            table.add_column()
        for y, row in enumerate(self.grid._array):
            style = None
            cells = []
            for x, cell in enumerate(row):
                cell_str = Symbol(cell).emoji if cell in ("S", "M", "0") else str(cell)
                # Highlighted row
                if highlight and highlight[0] == "row" and highlight[1] == y:                                        
                    style = "underline magenta"
                # Highlighted column
                elif highlight and highlight[0] == "col" and highlight[1] == x:                    
                    cell_str = f"[underline cyan]{cell_str}[/]"
                cells.append(cell_str)
            table.add_row(*cells, style=style)
        return table

    def solve(self):
        console = Console()
        with Live(self.grid_to_table(), refresh_per_second=30, console=console) as live:
            time.sleep(2)
            while any(
                cell not in ("S", "M", Symbol.Sun, Symbol.Moon)
                for row in self.grid._array
                for cell in row
            ):
                changed = self.solve_row_and_col_adjacent_rules(live=live)
                time.sleep(2)
                live.update(self.grid_to_table())
                if not changed:
                    break

@timing_decorator
def main(raw):
    text_input = read_input(raw)
    input_parsed = [i if i else "" for i in text_input]
    puzzle = Puzzle(input_parsed)
    puzzle.solve()




def solve():
    print(f"\nSolving:")
    main(raw=files["input"])    

if __name__ == "__main__":    
    solve()
