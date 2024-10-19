import pygame
import random

pygame.init()

# Window setup
WIDTH, HEIGHT = 300, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tetris")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Shapes
SHAPES = [
    [[1, 1, 1],
     [0, 1, 0]],

    [[0, 1, 1],
     [1, 1, 0]],

    [[1, 1, 0],
     [0, 1, 1]],

    [[1, 1, 1, 1]],

    [[1, 1],
     [1, 1]]
]

# Block size and grid
BLOCK_SIZE = 30
GRID_WIDTH, GRID_HEIGHT = WIDTH // BLOCK_SIZE, HEIGHT // BLOCK_SIZE

def draw_grid():
    for x in range(0, WIDTH, BLOCK_SIZE):
        pygame.draw.line(screen, WHITE, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, BLOCK_SIZE):
        pygame.draw.line(screen, WHITE, (0, y), (WIDTH, y))

def draw_shape(shape, position):
    for i, row in enumerate(shape):
        for j, val in enumerate(row):
            if val == 1:
                pygame.draw.rect(screen, BLUE, (position[0] + j * BLOCK_SIZE, position[1] + i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

def shape_collides(shape, x, y):
    if y + len(shape) * BLOCK_SIZE > HEIGHT:
        return True
    return False

# Main loop
def main():
    running = True
    clock = pygame.time.Clock()
    shape = random.choice(SHAPES)
    x, y = GRID_WIDTH // 2 * BLOCK_SIZE, 0
    speed = 500  # in milliseconds
    last_move_down_time = pygame.time.get_ticks()

    while running:
        screen.fill(BLACK)
        draw_grid()
        draw_shape(shape, (x, y))

        current_time = pygame.time.get_ticks()
        if current_time - last_move_down_time > speed:
            if not shape_collides(shape, x, y + BLOCK_SIZE):
                y += BLOCK_SIZE
            last_move_down_time = current_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and x > 0:
                    x -= BLOCK_SIZE
                if event.key == pygame.K_RIGHT and x < (GRID_WIDTH - len(shape[0])) * BLOCK_SIZE:
                    x += BLOCK_SIZE
                if event.key == pygame.K_DOWN:
                    if not shape_collides(shape, x, y + BLOCK_SIZE):
                        y += BLOCK_SIZE

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()
