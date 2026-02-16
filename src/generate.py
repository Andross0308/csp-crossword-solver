from queue import Queue
import sys

from crossword import *




class CrosswordCreator:

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for variable in self.domains:
            note_consistens = set()
            for value in self.domains[variable]:
                if len(value) == variable.length:
                    note_consistens.add(value)
            self.domains[variable] = note_consistens

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        modify = False
        if self.crossword.overlaps[x,y] is not None:
            x_position, y_position = self.crossword.overlaps[x, y]
            for X in self.domains[x]:
                found = False
                for Y in self.domains[y]:
                    if X[x_position] == Y[y_position] and X != Y:
                        found = True
                        break
                if not found:
                    new_domain = set()
                    for i in self.domains[x]:
                        if i != X:
                            new_domain.add(i)
                    self.domains[x] = new_domain
                    modify=True
        return modify
            

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        allArcs = Queue()
        if arcs is None:
            for arc in self.crossword.overlaps:
                if arc is not None:
                    allArcs.put(arc)
        else:
            for arc in arcs:
                allArcs.put(arc)

        while not allArcs.empty():
            (x, y) = allArcs.get()
            if self.revise(x,y):
                if len(self.domains[x]) == 0:
                    return False
                for arc in self.crossword.overlaps:
                    if x in arc and arc != (x,y) and self.crossword.overlaps[arc] is not None:
                        allArcs.put(arc)
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        if assignment.keys() == self.domains.keys():
            for value in assignment.values():
                if value is None:
                    return False
            return True
        return False

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        for var in assignment:
            word = assignment[var]
            if word is not None:
                if len(word) != var.length:
                    return False
                for neighbour in self.crossword.neighbors(var):
                    if neighbour in assignment.keys() and assignment[neighbour] is not None:
                        interception = assignment[neighbour]
                        var_pos, nei_pos = self.crossword.overlaps[var, neighbour]
                        if word[var_pos] != interception[nei_pos]:
                            return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        values = {}
        for value in self.domains[var]:
            values[value] = 0

        for val in self.domains[var]:
            for other_var in self.crossword.neighbors(var):
                for other_val in self.domains[other_var]:
                    this_pos, other_pos = self.crossword.overlaps[var, other_var]
                    if val[this_pos] != other_val[other_pos]:
                        values[val] += 1

        return sorted([x for x in values], key= lambda x: values[x])


    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unsigned_variables = set()
        for var in self.domains:
            if var not in assignment:
                unsigned_variables.add(var)
        cur_var = None
        for variable in unsigned_variables:
            if cur_var is None:
                cur_var = variable
            else:
                if len(self.domains[cur_var]) > len(self.domains[variable]):
                    cur_var = variable
                elif len(self.crossword.neighbors(cur_var)) > len(self.crossword.neighbors(variable)):
                    cur_var = variable
        return cur_var


    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var, assignment):
            assignment[var] = value
            if self.consistent(assignment):
                result = self.backtrack(assignment)
                if result is not None:
                    return result
            assignment.pop(var)
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
