import pygame
import random

class CaveSimulation:
    def __init__(self, grid_height, grid_width, cell_size, density, iterations, search_range):
        self.grid_height = grid_height
        self.grid_width = grid_width
        self.cell_size = cell_size
        self.density = density
        self.iterations = iterations
        self.search_range = search_range
        self.grid = self.generate_grid()

    def generate_grid(self):
        grid = []
        for _ in range(self.grid_height):
            row = []
            for _ in range(self.grid_width):
                value = random.random()
                if value < self.density:
                    row.append(1)
                else:
                    row.append(0)
            grid.append(row)
        return grid

    def get_wall_count(self, x, y):
        wall_count = 0
        start = -1 - (self.search_range - 1) if self.search_range >= 1 else -1
        end = 2 + (self.search_range - 1) if self.search_range >= 1 else 2
        for dy in range(start, end):
            for dx in range(start, end):
                nx = x + dx
                ny = y + dy
                if nx < 0 or nx > self.grid_width - 1 or ny < 0 or ny > self.grid_height - 1:
                    wall_count += 1
                elif (dx != 0 or dy != 0) and self.grid[ny][nx] == 1:
                    wall_count += 1
        return wall_count

    def simulate_grid_step(self):
        max_wall_count = (2 * self.search_range + 1) ** 2 - 1
        ratio_wall = 0.4
        ratio_open = 0.5
        grid_copy = [[cell for cell in row] for row in self.grid]
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                wall_count = self.get_wall_count(x, y)
                threshold_wall = int(max_wall_count * ratio_wall)
                threshold_open = int(max_wall_count * ratio_open)
                if self.grid[y][x] == 1:  # If the current cell is a wall
                    grid_copy[y][x] = 1 if wall_count > threshold_wall else 0
                else:  # If the current cell is an open space
                    grid_copy[y][x] = 1 if wall_count > threshold_open else 0
        return grid_copy

    def simulate_grid(self):
        for _ in range(self.iterations):
            self.grid = self.simulate_grid_step()
        return self.grid

    def run_simulation(self):
        pygame.init()
        window_size = (self.grid_width * self.cell_size, self.grid_height * self.cell_size)
        window = pygame.display.set_mode(window_size)

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            for y in range(self.grid_height):
                for x in range(self.grid_width):
                    color = (255, 255, 255) if self.grid[y][x] == 0 else (0, 0, 0)
                    pygame.draw.rect(window, color, (x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size))
            pygame.display.flip()

        pygame.quit()