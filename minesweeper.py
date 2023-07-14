import itertools
import random
import copy
import time


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():


    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count:
            return self.cells
        return None

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if 0 == self.count:
            return self.cells
        return None

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
  
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):

        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        empty = Sentence(set(), 0)
        self.moves_made.add(cell)
        self.mark_safe(cell)
        i, j = cell[0] - 1, cell[1] -1
        cells = set()
        # get of the surrounding cells
        for x in range(i, i + 3):
            for y in range(j, j + 3):
                if (not (x == cell[0] and y == cell[1])) and x > -1 and y > -1:
                    if (x, y) not in self.moves_made and x < 8 and y < 8:
                        cells.add((x, y))
        sentence = Sentence(cells, count)

        # check if the sentence is not inside knowledge base
        if sentence not in self.knowledge:
            self.knowledge.append(sentence)
            lenght = len(self.knowledge) - 1
            # check for subset of a bigger set than minus each other to make new set
            for i in range(0, lenght):
                if self.knowledge[i].cells.issubset(sentence.cells):
                    inferred = Sentence(sentence.cells - self.knowledge[i].cells, sentence.count - self.knowledge[i].count)
                    if inferred != empty:
                        self.knowledge.append(inferred)
                elif sentence.cells.issubset(self.knowledge[i].cells):
                    inferred = Sentence(self.knowledge[i].cells - sentence.cells, self.knowledge[i].count - sentence.count)
                    if inferred != empty:
                        self.knowledge.append(inferred)

        # make sure the knowledge has no empty sets or duplicate                
        def removed(KB):
            new = list()
            for i in KB:
                if i not in new and i != empty:
                    new.append(i)
            return new

        # conclude new knowledge from the newly gather data
        def conclude(KB):
            while True:
                for k in KB:
                    if k == empty:
                        KB.remove(k)
                    if k.known_safes():
                        cells = copy. deepcopy(k.known_safes())
                        for cell in cells:
                            self.mark_safe(cell)
                        KB.remove(k)
                        KB = removed(KB)
                        break
                    elif k.known_mines():
                        cells = copy.deepcopy(k.known_mines())
                        for cell in cells:
                            self.mark_mine(cell)
                        KB.remove(k)
                        KB = removed(KB)
                        break
                if (len(KB) > 0 and k == KB[-1]) or len(KB) == 0:
                    return
        conclude(self.knowledge)
        self.knowledge = removed(self.knowledge)

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for cell in self.safes:
            if cell not in self.moves_made:
                return cell
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        while True:
            x = random.randint(0, 7)
            y = random.randint(0, 7)
            if (x, y) not in self.moves_made and (x, y) not in self.mines:
                return (x, y)
