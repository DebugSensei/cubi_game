import pygame
import random
import time
import heapq

pygame.init()

WIDTH, HEIGHT = 600, 600
ROWS, COLS = 30, 30
CELL_SIZE = (WIDTH // ROWS) // 1.01
PURPLE = (139, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
PINK = (255, 182, 193)

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_star_search(maze, start, goal):
    frontier = []
    heapq.heappush(frontier, (0, start))
    came_from = {}
    cost_so_far = {}
    came_from[start] = None
    cost_so_far[start] = 0

    while frontier:
        current_cost, current_node = heapq.heappop(frontier)

        if current_node == goal:
            break

        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            next_node = (current_node[0] + dx, current_node[1] + dy)
            if 0 <= next_node[0] < COLS and 0 <= next_node[1] < ROWS and maze[next_node[1]][next_node[0]] == 0:
                new_cost = cost_so_far[current_node] + 1
                if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                    cost_so_far[next_node] = new_cost
                    priority = new_cost + heuristic(goal, next_node)
                    heapq.heappush(frontier, (priority, next_node))
                    came_from[next_node] = current_node

    path = []
    while current_node != start:
        path.append(current_node)
        current_node = came_from[current_node]
    path.reverse()
    return path

def draw_interface(screen, score, lives):
    font = pygame.font.Font(None, 36)
    score_text = font.render(f'Score: {score}', True, BLACK)
    lives_text = font.render(f'Lives: {lives}', True, BLACK)
    score_rect = score_text.get_rect()
    lives_rect = lives_text.get_rect()
    pygame.draw.rect(screen, PURPLE, score_rect.inflate(10, 10))
    pygame.draw.rect(screen, PURPLE, lives_rect.inflate(10, 10).move(WIDTH - lives_rect.width - 20, 0))
    screen.blit(score_text, (5, 5))
    screen.blit(lives_text, (WIDTH - lives_rect.width - 15, 5))

def add_power_pellets(maze, count=4):
    pellets = []
    while len(pellets) < count:
        x, y = random.randint(1, COLS - 2), random.randint(1, ROWS - 2)
        if maze[y][x] == 0:
            pellets.append((x, y))
    return pellets

def draw_power_pellets(screen, pellets):
    for x, y in pellets:
        pygame.draw.circle(screen, YELLOW, (x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 4)

def generate_maze(rows, cols):
    maze = [[1] * (cols + 2) for _ in range(rows + 2)]

    def create_path(x, y):
        maze[y][x] = 0

        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        random.shuffle(directions)

        for dx, dy in directions:
            new_x, new_y = x + dx * 2, y + dy * 2
            if 0 <= new_x < cols and 0 <= new_y < rows and maze[new_y][new_x]:
                maze[y + dy][x + dx] = 0
                create_path(new_x, new_y)

    create_path(1, 1)
    return maze

def draw_maze(screen, maze):
    screen.fill(PURPLE)

    for y in range(len(maze)):
        for x in range(len(maze[y])):
            if maze[y][x] == 1:
                pygame.draw.rect(screen, BLACK, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

pacman_sprite = pygame.transform.scale(pygame.image.load('images/cubi.png'), (CELL_SIZE, CELL_SIZE))

def draw_pacman(screen, x, y, invincible):
    if invincible:
        temp_sprite = pygame.transform.scale(pygame.image.load('images/cubi_invincible.png'), (CELL_SIZE, CELL_SIZE))
    else:
        temp_sprite = pacman_sprite
    screen.blit(temp_sprite, (x * CELL_SIZE, y * CELL_SIZE))

def generate_ghosts_start(maze):
    positions = []
    while len(positions) < 4:
        x, y = random.randint(1, COLS - 2), random.randint(1, ROWS - 2)
        if maze[y][x] == 0 and (x, y) not in positions:
            positions.append((x, y))
    return positions

def draw_ghosts(screen, ghosts):
    ghost_sprite = pygame.transform.scale(pygame.image.load('images/ghost.png'), (CELL_SIZE, CELL_SIZE))
    for x, y in ghosts:
        screen.blit(ghost_sprite, (x * CELL_SIZE, y * CELL_SIZE))

def move_ghosts(maze, ghosts, target):
    new_ghosts = []
    for x, y in ghosts:
        path = a_star_search(maze, (x, y), target)
        if len(path) > 1:
            new_ghosts.append(path[1])
        else:
            new_ghosts.append((x, y))
    return new_ghosts

def initialize_dots(maze):
    return [(x, y) for y in range(1, ROWS + 1) for x in range(1, COLS + 1) if maze[y][x] == 0]

def draw_dots(screen, dots):
    for x, y in dots:
        pygame.draw.circle(screen, PINK, (x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 10)

def update_dots(dots, pacman_x, pacman_y):
    return [(x, y) for x, y in dots if (x, y) != (pacman_x, pacman_y)]

def check_collision_with_ghosts(pacman_x, pacman_y, ghosts, lives):
    for ghost in ghosts:
        if (pacman_x, pacman_y) == ghost:
            lives -= 1
            if lives <= 0:
                return lives, True
    return lives, False

pygame.mixer.music.load("sounds/CyberMode.mp3")
pygame.mixer.music.play(-1)

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Cubi Game")
    clock = pygame.time.Clock() 

    maze = generate_maze(ROWS, COLS)
    dots = initialize_dots(maze)
    ghosts = generate_ghosts_start(maze)
    power_pellets = add_power_pellets(maze)
    pacman_x, pacman_y = 1, 1
    score = 0
    lives = 3
    invincible = False
    invincible_time = 0
    direction = None

    running = True
    ghost_frame_counter = 0  

    while running:
        screen.fill(PURPLE)
        draw_maze(screen, maze)
        draw_dots(screen, dots)
        draw_power_pellets(screen, power_pellets)
        draw_ghosts(screen, ghosts)
        draw_pacman(screen, pacman_x, pacman_y, invincible)
        draw_interface(screen, score, lives)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w and maze[pacman_y - 1][pacman_x] == 0:
                    direction = 'up'
                elif event.key == pygame.K_s and maze[pacman_y + 1][pacman_x] == 0:
                    direction = 'down'
                elif event.key == pygame.K_a and maze[pacman_y][pacman_x - 1] == 0:
                    direction = 'left'
                elif event.key == pygame.K_d and maze[pacman_y][pacman_x + 1] == 0:
                    direction = 'right'

        if direction:
            nx, ny = pacman_x, pacman_y
            if direction == 'up': ny -= 1
            elif direction == 'down': ny += 1
            elif direction == 'left': nx -= 1
            elif direction == 'right': nx += 1

            if maze[ny][nx] == 0:
                pacman_x, pacman_y = nx, ny
                if (pacman_x, pacman_y) in dots:
                    dots.remove((pacman_x, pacman_y))
                    score += 10
                if (pacman_x, pacman_y) in power_pellets:
                    power_pellets.remove((pacman_x, pacman_y))
                    invincible = True
                    invincible_time = time.time()

        if invincible and (time.time() - invincible_time > 10):
            invincible = False

        for ghost in ghosts:
            if (pacman_x, pacman_y) == ghost and not invincible:
                lives -= 1
                if lives <= 0:
                    running = False
                    pygame.mixer.music.stop()
                    lose_sound = pygame.mixer.Sound('sounds/lose.mp3')
                    lose_sound.play() 
                    screen.fill(BLACK)
                    font = pygame.font.Font(None, 74)
                    text = font.render('GAME OVER', True, RED)
                    text_rect = text.get_rect(center=(WIDTH / 2, HEIGHT / 2))
                    screen.blit(text, text_rect)
                    pygame.display.flip()
                    pygame.time.wait(6000)
                    break

        ghost_frame_counter += 1
        if ghost_frame_counter >= 3:  
            ghosts = move_ghosts(maze, ghosts, (pacman_x, pacman_y))
            ghost_frame_counter = 0

        if not power_pellets:
            pygame.mixer.music.stop()
            win_sound = pygame.mixer.Sound('sounds/win.mp3')
            win_sound.play()  
            running = False
            screen.fill(BLACK)
            font = pygame.font.Font(None, 74)
            win_text = font.render('YOU WIN', True, (255, 255, 0))
            win_rect = win_text.get_rect(center=(WIDTH / 2, HEIGHT / 2))
            screen.blit(win_text, win_rect)
            pygame.display.flip()
            pygame.time.wait(5000) 
            continue

        pygame.display.flip()
        clock.tick(10) 

        if not power_pellets:
            running = False
    pygame.quit()

if __name__ == "__main__":
    main()
