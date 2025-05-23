import pygame
import sys
import math
import random

# --- 設定 ---
WIDTH, HEIGHT = 800, 600
TOWER_WIDTH = 10
TOWER_HEIGHT = 300
BASE_HEIGHT = 20
DISK_HEIGHT = 20

TOWER_X = [200, 400, 600]
TOWER_Y = HEIGHT - BASE_HEIGHT - TOWER_HEIGHT

# 色定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
RED = (255, 100, 100)
GREEN = (100, 255, 100)
BLUE = (100, 100, 255)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tower of Hanoi")
font = pygame.font.SysFont(None, 36)
clock = pygame.time.Clock()

# ディスクとタワー構造
class Disk:
    def __init__(self, size, tower_index, color):
        self.size = size
        self.tower_index = tower_index
        self.color = color
        self.x = 0
        self.y = 0
        self.dragging = False
        self.offset_x = 0
        self.offset_y = 0
        self.rect = pygame.Rect(0, 0, 0, 0)

    def draw(self):
        width = 40 + self.size * 20
        if not self.dragging:
            self.x = TOWER_X[self.tower_index] - width // 2
            tower_disks = towers[self.tower_index]
            index = tower_disks.index(self)
            self.y = TOWER_Y + TOWER_HEIGHT - (index + 1) * DISK_HEIGHT
        self.rect = pygame.Rect(self.x, self.y, width, DISK_HEIGHT)
        pygame.draw.rect(screen, self.color, self.rect)

# 初期化関数
def initialize_game(n):
    global disks, towers, selected_disk, move_count, completed
    disks = [Disk(i, 0, disk_colors[i]) for i in reversed(range(n))]
    towers = [disks.copy(), [], []]
    selected_disk = None
    move_count = 0
    completed = False

# 描画関数
def draw_scene():
    screen.fill(WHITE)
    for x in TOWER_X:
        pygame.draw.rect(screen, BLACK, (x - TOWER_WIDTH // 2, TOWER_Y, TOWER_WIDTH, TOWER_HEIGHT))
    pygame.draw.rect(screen, GRAY, (0, HEIGHT - BASE_HEIGHT, WIDTH, BASE_HEIGHT))
    for tower in towers:
        for disk in tower:
            disk.draw()
    if selected_disk and selected_disk.dragging:
        selected_disk.draw()

    move_text = font.render(f"Moves: {move_count}", True, BLACK)
    screen.blit(move_text, (10, 10))

    min_moves = 2 ** len(disks) - 1
    min_text = font.render(f"Minimum moves: {min_moves}", True, BLACK)
    screen.blit(min_text, (10, 50))

    if completed:
        comp_text = font.render("Completed!", True, GREEN)
        screen.blit(comp_text, (WIDTH // 2 - 100, 10))

    # デモボタン
    pygame.draw.rect(screen, RED, (WIDTH - 150, 10, 120, 40))
    demo_text = font.render("Demo", True, WHITE)
    screen.blit(demo_text, (WIDTH - 135, 15))

    # 「Back to Setup」ボタン（幅を190に調整）
    pygame.draw.rect(screen, BLUE, (WIDTH - 190, 60, 180, 40))
    restart_text = font.render("Back to Setup", True, WHITE)
    screen.blit(restart_text, (WIDTH - 185, 65))

# ディスク数入力画面
def ask_disk_count_graphically():
    selecting = True
    while selecting:
        screen.fill(WHITE)
        title = font.render("Select number of disks (1-10)", True, BLACK)
        screen.blit(title, (WIDTH // 2 - 150, 100))
        for i in range(1, 11):
            pygame.draw.rect(screen, GRAY, (100 + (i - 1) * 60, 200, 50, 50))
            num_text = font.render(str(i), True, BLACK)
            screen.blit(num_text, (115 + (i - 1) * 60, 210))

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                for i in range(1, 11):
                    rect = pygame.Rect(100 + (i - 1) * 60, 200, 50, 50)
                    if rect.collidepoint(x, y):
                        return i

# ドラッグ処理関連
selected_disk = None
def handle_mouse_down(pos):
    global selected_disk
    for tower in towers:
        if tower:
            disk = tower[-1]
            if disk.rect.collidepoint(pos):
                selected_disk = disk
                selected_disk.dragging = True
                selected_disk.offset_x = pos[0] - disk.x
                selected_disk.offset_y = pos[1] - disk.y
                break

def handle_mouse_up(pos):
    global move_count, completed, selected_disk
    if not selected_disk:
        return
    for i, x in enumerate(TOWER_X):
        if abs(pos[0] - x) < 50:
            from_tower = selected_disk.tower_index
            to_tower = i
            if towers[to_tower] and towers[to_tower][-1].size < selected_disk.size:
                break
            towers[from_tower].remove(selected_disk)
            towers[to_tower].append(selected_disk)
            selected_disk.tower_index = to_tower
            move_count += 1
            break
    selected_disk.dragging = False
    selected_disk = None
    if len(towers[2]) == len(disks):
        completed = True

def handle_mouse_motion(pos):
    if selected_disk and selected_disk.dragging:
        selected_disk.x = pos[0] - selected_disk.offset_x
        selected_disk.y = pos[1] - selected_disk.offset_y

# 自動デモ用再帰関数
def auto_solve(n, source, target, auxiliary):
    total_moves = 2 ** n - 1
    if n >= 7:
        total_duration = 30000  # 30秒
        delay = total_duration // total_moves
    else:
        delay = 300

    def move(n, source, target, auxiliary):
        if n > 0:
            move(n-1, source, auxiliary, target)
            pygame.time.wait(delay)
            disk = towers[source].pop()
            towers[target].append(disk)
            disk.tower_index = target
            draw_scene()
            pygame.display.flip()
            global move_count
            move_count += 1
            move(n-1, auxiliary, target, source)

    move(n, source, target, auxiliary)

def check_demo_button(pos):
    return pygame.Rect(WIDTH - 150, 10, 120, 40).collidepoint(pos)

def check_restart_button(pos):
    return pygame.Rect(WIDTH - 190, 60, 180, 40).collidepoint(pos)

# メイン処理
def main():
    global disk_colors
    n = ask_disk_count_graphically()
    disk_colors = [pygame.Color(random.randint(0,255), random.randint(0,255), random.randint(0,255)) for _ in range(n)]
    initialize_game(n)
    running = True
    while running:
        draw_scene()
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if check_demo_button(event.pos):
                    initialize_game(n)
                    auto_solve(n, 0, 2, 1)
                elif check_restart_button(event.pos):
                    n = ask_disk_count_graphically()
                    disk_colors = [pygame.Color(random.randint(0,255), random.randint(0,255), random.randint(0,255)) for _ in range(n)]
                    initialize_game(n)
                else:
                    handle_mouse_down(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                handle_mouse_up(event.pos)
            elif event.type == pygame.MOUSEMOTION:
                handle_mouse_motion(event.pos)

        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
