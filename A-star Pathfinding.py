import pygame
import math
from queue import PriorityQueue

Dimension = 700
WINDOW = pygame.display.set_mode((Dimension, Dimension))
pygame.display.set_caption("A* PathFinding Visualization")

WHITE = (255, 255, 255)
RED = (252, 51, 51)
ORANGE = (255, 100, 0)
BLACK = (0, 0, 0)
PURPLE = (6, 65, 179)
BLUE = (2, 189, 247)
GREEN = (1, 174, 0)
GREY = (106, 106, 106)


class Node:
    def __init__(self, row, column, width, total_rows):
        self.row = row
        self.column = column
        self.width = width
        self.total_rows = total_rows
        self.x = row * width
        self.y = column * width
        self.color = WHITE
        self.neighbors = []

    def node_pos(self):
        return self.row, self.column

    def is_closed(self):
        return self.color == RED

    def is_open(self):
        return self.color == ORANGE

    def is_barrier(self):
        return self.color == BLACK

    def is_start(self):
        return self.color == PURPLE

    def is_end(self):
        return self.color == BLUE

    def reset(self):
        self.color = WHITE

    def make_closed(self):
        self.color = RED

    def make_open(self):
        self.color = ORANGE

    def make_barrier(self):
        self.color = BLACK

    def make_start(self):
        self.color = PURPLE

    def make_end(self):
        self.color = BLUE

    def make_path(self):
        self.color = GREEN

    def draw(self, window):
        pygame.draw.rect(window, self.color,
                         (self.x, self.y, self.width, self.width))

    def update_neighbor(self, grid):
        self.neighbors = []
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.column].is_barrier():
            self.neighbors.append(grid[self.row + 1][self.column])

        if self.row > 0 and not grid[self.row - 1][self.column].is_barrier():
            self.neighbors.append(grid[self.row - 1][self.column])

        if self.column < self.total_rows - 1 and not grid[self.row][self.column + 1].is_barrier():
            self.neighbors.append(grid[self.row][self.column + 1])

        if self.row > 0 and not grid[self.row][self.column - 1].is_barrier():
            self.neighbors.append(grid[self.row][self.column - 1])

    def __lt__(self, other):
        return False


def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    print(int(math.sqrt((abs(x1 - x2)) + abs(y1 - y2))))
    return int(math.sqrt((abs(x1 - x2)) + abs(y1 - y2)))


def algorithm(draw, grid, startNode, endNode):
    count = 0
    openSet = PriorityQueue()
    openSet.put((0, count, startNode))
    previous = {}
    gScore = {node: float('inf') for row in grid for node in row}
    gScore[startNode] = 0
    fScore = {node: float('inf') for row in grid for node in row}
    fScore[startNode] = h(startNode.node_pos(), endNode.node_pos())
    openSetHash = {startNode}

    while not openSet.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = openSet.get()[2]
        openSetHash.remove(current)

        if current == endNode:
            reconstruct_path(previous, endNode, draw)
            endNode.make_end()
            return True

        for neighbor in current.neighbors:
            tempGScore = gScore[current]+1
            if tempGScore < gScore[neighbor]:
                previous[neighbor] = current
                gScore[neighbor] = tempGScore
                fScore[neighbor] = tempGScore + \
                    h(neighbor.node_pos(), endNode.node_pos())
                if neighbor not in openSetHash:
                    count += 1
                    openSet.put((fScore, count, neighbor))
                    openSetHash.add(neighbor)
                    neighbor.make_open()
        draw()

        if current != startNode:
            current.make_closed()

    return False


def reconstruct_path(previous, endNode, draw):
    while endNode in previous:
        endNode = previous[endNode]
        endNode.make_path()
        draw()


def make_grid(rows, width):
    grid = []
    size = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, size, rows)
            grid[i].append(node)
    return grid


def draw_grid(win, rows, width):
    size = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * size), (width, i * size))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j * size, 0), (j * size, width))


def draw(win, grid, rows, width):
    win.fill(WHITE)
    for row in grid:
        for node in row:
            row[0].make_barrier()
            row[49].make_barrier()
            node.draw(win)
    draw_grid(win, rows, width)
    pygame.display.update()


def clicked_pos(pos, rows, width):
    size = width // rows
    y, x = pos
    row = y // size
    column = x // size
    return row, column


def main(win, width):
    rows = 50
    grid = make_grid(rows, width)
    startNode = None
    endNode = None
    run = True

    while run:
        draw(win, grid, rows, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row, column = clicked_pos(pos, rows, width)
                node = grid[row][column]
                if not startNode and node != endNode:
                    startNode = node
                    startNode.make_start()
                elif not endNode and node != startNode:
                    endNode = node
                    endNode.make_end()
                elif node != startNode and node != endNode:
                    node.make_barrier()

            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, column = clicked_pos(pos, rows, width)
                node = grid[row][column]
                node.reset()
                if node == startNode:
                    startNode = None
                elif node == endNode:
                    endNode = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and startNode and endNode:
                    for row in grid:
                        for node in row:
                            node.update_neighbor(grid)
                    algorithm(lambda: draw(WINDOW, grid, rows, width),
                              grid, startNode, endNode)

                if event.key == pygame.K_c:
                    startNode = None
                    endNode = None
                    grid = make_grid(rows, width)

    pygame.quit()


main(WINDOW, Dimension)
