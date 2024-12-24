import pygame
import sys

# Configuration de base
GRID_SIZE = 15
CELL_SIZE = 40
MARGIN = 20
SCREEN_SIZE = GRID_SIZE * CELL_SIZE + 2 * MARGIN
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
RED = (255, 0, 0)

# Initialisation de Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
pygame.display.set_caption("Gomoku")
font = pygame.font.SysFont("Arial", 24)

def draw_board():
    """Dessine la grille du jeu."""
    screen.fill(WHITE)
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            rect = pygame.Rect(
                MARGIN + col * CELL_SIZE, MARGIN + row * CELL_SIZE, CELL_SIZE, CELL_SIZE
            )
            pygame.draw.rect(screen, GRAY, rect, 1)

def draw_stones(board):
    """Dessine les pierres sur le plateau."""
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            if board[row][col] == "X":
                pygame.draw.circle(
                    screen, BLACK,
                    (MARGIN + col * CELL_SIZE + CELL_SIZE // 2, MARGIN + row * CELL_SIZE + CELL_SIZE // 2),
                    CELL_SIZE // 2 - 5
                )
            elif board[row][col] == "O":
                pygame.draw.circle(
                    screen, RED,
                    (MARGIN + col * CELL_SIZE + CELL_SIZE // 2, MARGIN + row * CELL_SIZE + CELL_SIZE // 2),
                    CELL_SIZE // 2 - 5
                )

def check_winner(board, row, col, symbol):
    """Vérifie si le joueur a gagné après avoir placé une pierre."""
    directions = [
        (0, 1),   # Horizontal
        (1, 0),   # Vertical
        (1, 1),   # Diagonale descendante
        (1, -1),  # Diagonale montante
    ]
    for dr, dc in directions:
        count = 1
        for step in [-1, 1]:
            r, c = row, col
            while True:
                r += step * dr
                c += step * dc
                if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE and board[r][c] == symbol:
                    count += 1
                else:
                    break
        if count >= 5:
            return True
    return False

def main():
    board = [["." for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    running = True
    current_player = "X"


    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                col = (x - MARGIN) // CELL_SIZE
                row = (y - MARGIN) // CELL_SIZE

                if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE and board[row][col] == ".":
                    board[row][col] = current_player
                    if check_winner(board, row, col, current_player):
                        draw_board()
                        draw_stones(board)
                        pygame.display.flip()
                        print(f"Le joueur {current_player} a gagné !")
                        pygame.time.wait(2000)
                        running = False
                    current_player = "O" if current_player == "X" else "X"

        draw_board()
        draw_stones(board)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()