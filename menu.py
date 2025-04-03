import pygame
import random

GRID_SIZE = 19
STONE_WHITE = (230, 230, 230)
STONE_BLACK = (43, 43, 43)

COLOR_MENU = (115, 61, 0, 200)
COLOR_BUTTON = (64, 31, 1)
COLOR_BUTTON_HOVER = (105, 52, 2)

def updateScreenSize(width, height, isFullScreen):
    global SCREEN_WIDTH, SCREEN_HEIGHT, HPC, WPC
    SCREEN_HEIGHT = height
    SCREEN_WIDTH = width

    HPC = SCREEN_HEIGHT / 100
    WPC = SCREEN_WIDTH // 3 / 100
    if (isFullScreen):
        return pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN), pygame.font.SysFont('Comic Sans MS', int(SCREEN_WIDTH * 0.026)), pygame.font.SysFont('Comic Sans MS', int(SCREEN_WIDTH * 0.017))
    else:
        return pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)), pygame.font.SysFont('Comic Sans MS', int(SCREEN_WIDTH * 0.026)), pygame.font.SysFont('Comic Sans MS', int(SCREEN_WIDTH * 0.017))

class Game:
    def __init__(self):
        self.reset()
        
    def reset(self):
        """Réinitialise le jeu à l'état initial."""
        self.inGame = False
        self.turn = 1
        self.time = 0
        self.start_time = 0
        self.whoStart = "p1" if self.startPlayer() else "p2"
        self.whoPlay = self.whoStart if (self.turn % 2) else "p1" if (self.whoStart == "p2") else "p2"
        self.p1 = "Joueur 1"
        self.p2 = "Joueur 2"
        # self.board = [["." if _ % 3 == 0 else "1" if _ % 3 == 1 else "2" for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.board = [["." for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    
    def startGame(self):
        self.inGame = True
        self.start_time = pygame.time.get_ticks()  

    def startPlayer(self):
        """Détermine aléatoirement qui commence."""
        return bool(random.getrandbits(1))

    def dispInfoOn(self, surface, font):
        rect = placeButtonAtPercent(40, 35)
        pygame.draw.rect(surface, (0, 0, 0), rect, 7)
        # text_surface = font.render("Tour de " + playerTurn, True, (0, 0, 0))
        # text_rect = text_surface.get_rect(topleft=rect.topleft + (50, 50))
        elapsed_time = (pygame.time.get_ticks() - self.start_time) // 1000  # Temps écoulé en secondes
        heures = elapsed_time // 3600
        minutes = (elapsed_time % 3600) // 60
        secondes = elapsed_time % 60
        text_lines = [
            f"Temps écoulé : {heures:02}:{minutes:02}:{secondes:02}",
            "Tour " + str(self.turn) + ".",
            "Aux " + ("noirs" if (self.whoPlay == "p1") else "blancs") + " de jouer."
        ]
        draw_text_in_rect(surface, rect, text_lines, font)
        # surface.blit(text_surface, text_rect)

    def playAt(self, coords):
        symbol = "1" if self.whoPlay == "p1" else "2"
        if self.checkIfAutorized(coords, symbol):
            self.board[coords[0]][coords[1]] = symbol
            if self.checkAlignments(symbol, coords):
                self.inGame = False
            else:
                self.turn += 1
                self.whoPlay = self.whoStart if (self.turn % 2) else "p1" if (self.whoStart == "p2") else "p2"
        else:
            print("Coup interdit !")
    
    def checkAlignments(self, symbol, coords):
        directions = [
            (0, 1),   # Horizontal
            (1, 0),   # Vertical
            (1, 1),   # Diagonale descendante
            (1, -1),  # Diagonale montante
        ]
        for dv, dh in directions:
            count = 1
            for step in [-1, 1]:
                r, c = coords
                while True:
                    r += step * dv
                    c += step * dh
                    if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE and self.board[r][c] == symbol:
                        count += 1
                    else:
                        break
            if count >= 5:
                return True
        return False

    def checkIfAutorized(self, coords, symbol):
        ret = self.is_move_allowed(coords, symbol)
        return ret

    def is_move_allowed(self, coords, player):
        """
        Vérifie si un coup est autorisé en respectant la règle du double free-three.

        Args:
            game: Classe contenant game.board (double tableau représentant le plateau).
            coords: Tuple (row, col) indiquant la position à vérifier.
            player: Symbole du joueur ('1' ou '2').

        Returns:
            bool: True si le placement est autorisé, False sinon.
        """
        row, col = coords
        board = self.board

        # Vérifier si la case est déjà occupée
        if board[row][col] != ".":
            return False

        # Directions à vérifier pour trouver des free-threes
        directions = [
            (0, 1),   # Horizontal
            (1, 0),   # Vertical
            (1, 1),   # Diagonale descendante
            (1, -1),  # Diagonale montante
        ]

        def is_free_three(start_row, start_col, dr, dc):
            """
            Vérifie si un "free-three" existe dans une direction donnée.

            Args:
                start_row: Ligne de départ.
                start_col: Colonne de départ.
                dr: Delta ligne pour parcourir dans une direction.
                dc: Delta colonne pour parcourir dans une direction.

            Returns:
                bool: True si un free-three est détecté.
            """
            line = []
            for step in range(-4, 5):  # Vérifie jusqu'à 4 cases avant et après
                r = start_row + step * dr
                c = start_col + step * dc
                if 0 <= r < len(board) and 0 <= c < len(board[0]):
                    line.append(board[r][c])
                else:
                    line.append(None)

            # Remplace la position actuelle par le joueur simulé
            line[4] = player

            # Chercher les motifs de free-three
            patterns = [
                [".", player, player, player, "."],
                [".", player, ".", player, player, "."],
                [".", player, player, ".", player, "."],
            ]

            for pattern in patterns:
                if any(line[i:i + len(pattern)] == pattern for i in range(len(line) - len(pattern) + 1)):
                    return True

            return False

        # Compter les free-threes créés par ce mouvement
        free_three_count = 0
        for dr, dc in directions:
            if is_free_three(row, col, dr, dc):
                free_three_count += 1

            # Si deux free-threes sont détectés, le mouvement est interdit
            if free_three_count >= 2:
                return False

        # Si aucun double free-three n'est détecté, le mouvement est autorisé
        return True


def draw_text_in_rect(surface, rect, text_lines, font, color=(0, 0, 0), margin=20):
    """
    Affiche du texte dans un rectangle donné, avec une marge et des lignes séparées.
    
    :param surface: Surface sur laquelle dessiner (généralement l'écran ou une surface intermédiaire).
    :param rect: pygame.Rect définissant le rectangle où afficher le texte.
    :param text_lines: Liste de chaînes, chaque élément correspondant à une ligne de texte.
    :param font: Police pygame.Font utilisée pour dessiner le texte.
    :param color: Couleur du texte (par défaut noir).
    :param margin: Marge en pixels autour du texte (par défaut 20px).
    """
    # Ajuster la zone intérieure du rectangle en fonction des marges
    inner_rect = pygame.Rect(
        rect.left + margin, 
        rect.top + margin, 
        rect.width - 2 * margin, 
        rect.height - 2 * margin
    )
    
    # Calcul de la hauteur de chaque ligne
    line_height = font.get_linesize()
    
    # Vérifier si tout le texte peut tenir dans la hauteur du rectangle
    max_lines = inner_rect.height // line_height
    if len(text_lines) > max_lines:
        text_lines = text_lines[:max_lines]  # Tronquer les lignes qui ne tiennent pas
    
    # Dessiner chaque ligne
    for i, line in enumerate(text_lines):
        # Calculer la position en y pour chaque ligne
        text_surface = font.render(line, True, color)
        text_position = (inner_rect.left, inner_rect.top + i * line_height)
        surface.blit(text_surface, text_position)

def placeButtonAtPercent(percent, size=10):
    """Retourne un rectangle positionné en pourcentage sur l'écran."""
    return pygame.Rect(WPC * 10, HPC * percent, WPC * 80, HPC * size)

def draw_text_centered(surface, text, font, color, rect):
    """Dessine le texte centré dans un rectangle donné."""
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=rect.center)
    surface.blit(text_surface, text_rect)

def draw_end_game_screen(screen, game):
    """
    Dessine un écran de fin de partie avec un rectangle transparent contenant des informations de la partie.

    Args:
        screen: Surface Pygame sur laquelle dessiner.
        game: Objet contenant les informations de la partie (turn, p1, p2, time).
    """
    # Dimensions et position du rectangle
    rect_width = int(SCREEN_WIDTH * 0.8)
    rect_height = int(SCREEN_HEIGHT * 0.8)
    rect_x = (SCREEN_WIDTH - rect_width) // 2
    rect_y = (SCREEN_HEIGHT - rect_height) // 2

    # Création d'une surface transparente
    transparent_surface = pygame.Surface((rect_width, rect_height), pygame.SRCALPHA)
    transparent_surface.fill((102, 51, 0, 200))  # Marron foncé transparent à 20%

    # Blitter le rectangle sur l'écran
    screen.blit(transparent_surface, (rect_x, rect_y))

    # Préparer les informations
    font = pygame.font.SysFont('Comic Sans MS', 40)
    text_color = (255, 255, 255)  # Blanc

    winner = game.p1 if game.turn % 2 == 1 else game.p2
    lines = [
        f"Gagnant : {winner}",
        f"Joueur 1 : {game.p1}",
        f"Joueur 2 : {game.p2}",
        f"Temps de la partie : {game.time:.2f} secondes",
        f"Nombre de tours : {game.turn}",
    ]

    # Calcul de la position de départ pour centrer verticalement le texte
    text_margin = 20
    y_start = rect_y + text_margin

    # Afficher chaque ligne de texte
    for idx, line in enumerate(lines):
        text_surface = font.render(line, True, text_color)
        text_rect = text_surface.get_rect(midtop=(SCREEN_WIDTH // 2, y_start + idx * 60))  # 60px entre chaque ligne
        screen.blit(text_surface, text_rect)

def draw_gomoku_board(screen, game_area, game, mouse_pos, event, board_size=19, percentage=0.8, line_color=(0, 0, 0), background_color=(255, 223, 186, 0)):
    """
    Dessine un plateau de Gomoku centré sur l'écran avec une taille basée sur 80% de l'axe le plus grand.

    Args:
        game_area: Surface de Pygame sur laquelle dessiner.
        board_size: Nombre de lignes/colonnes du plateau (par défaut 19).
        percentage: Proportion de l'axe le plus grand pour définir la taille du plateau (par défaut 0.8).
        line_color: Couleur des lignes de la grille (par défaut noir).
        background_color: Couleur de fond du plateau (par défaut beige).
    """
    screen_width, screen_height = game_area.get_size()

    # Taille du plateau basée sur 80% de l'axe le plus grand
    board_pixel_size = int(min(screen_width, screen_height) * percentage)
    cell_size = board_pixel_size // (board_size - 1)  # Taille d'une cellule en pixels
    piece_size = cell_size * 0.4 # Taille d'un pion

    # Calcul des marges pour centrer le plateau
    margin_x = (screen_width - board_pixel_size) // 2
    margin_y = (screen_height - board_pixel_size) // 2

    # Remplir le fond avec la couleur de fond
    game_area.fill(background_color)

    # Dessiner un rectangle dépassant de 50px autour du plateau
    rectangle_margin = 50
    rectangle_color = (255, 223, 186)
    rectangle_rect = pygame.Rect(
        margin_x - rectangle_margin, 
        margin_y - rectangle_margin, 
        board_pixel_size + 2 * rectangle_margin, 
        board_pixel_size + 2 * rectangle_margin
    )
    pygame.draw.rect(game_area, rectangle_color, rectangle_rect)

    # Dessiner les lignes horizontales
    for i in range(board_size):
        y = margin_y + i * cell_size
        pygame.draw.line(game_area, line_color, (margin_x, y), (margin_x + board_pixel_size, y))

    # Dessiner les lignes verticales
    for j in range(board_size):
        x = margin_x + j * cell_size
        pygame.draw.line(game_area, line_color, (x, margin_y), (x, margin_y + board_pixel_size))

    # Dessiner les intersections spéciales (hoshi)
    hoshi_positions = [
        (3, 3), (3, 9), (3, 15),
        (9, 3), (9, 9), (9, 15),
        (15, 3), (15, 9), (15, 15),
    ]
    for row, col in hoshi_positions:
        center_x = margin_x + col * cell_size
        center_y = margin_y + row * cell_size
        pygame.draw.circle(game_area, line_color, (center_x, center_y), 5)

    for idx_line, line in enumerate(game.board):
        for idx_col, cross in enumerate(line):
            if (cross == "1"):
                center_x = margin_x + idx_col * cell_size
                center_y = margin_y + idx_line * cell_size
                pygame.draw.circle(game_area, STONE_BLACK, (center_x, center_y), piece_size)
            if (cross == "2"):
                center_x = margin_x + idx_col * cell_size
                center_y = margin_y + idx_line * cell_size
                pygame.draw.circle(game_area, STONE_WHITE, (center_x, center_y), piece_size)
                pygame.draw.circle(game_area, STONE_BLACK, (center_x, center_y), piece_size, 2)

    # # Vérification des collisions avec les rectangles
    if game.inGame == True:
        adjusted_mousePos = (mouse_pos[0] - SCREEN_WIDTH // 3, mouse_pos[1])
        mousePressed = False
        if event:
            mousePressed = True
        for row in range(board_size):
            for col in range(board_size):
                rect = pygame.Rect(
                    margin_x + col * cell_size - cell_size // 2,
                    margin_y + row * cell_size - cell_size // 2,
                    cell_size,
                    cell_size,
                )
                if rect.collidepoint(adjusted_mousePos) and game.board[row][col] == ".":
                    if mousePressed == True:
                        game.playAt((row, col))
                    else:
                        # Dessiner une pierre semi-transparente
                        stone_color = STONE_BLACK if game.whoPlay == "p1" else STONE_WHITE
                        alpha = 128  # Transparence (50%)
                        overlay = pygame.Surface((piece_size * 2, piece_size * 2), pygame.SRCALPHA)
                        pygame.draw.circle(overlay, (*stone_color, alpha), (piece_size, piece_size), piece_size)
                        if game.whoPlay == "p2":
                            pygame.draw.circle(overlay, (*STONE_BLACK, alpha), (piece_size, piece_size), piece_size, 2)
                        game_area.blit(overlay, (rect.centerx - piece_size, rect.centery - piece_size))
    # else:
    #     draw_end_game_screen(screen, game)

def getMenu(title_font, pos, logo, button_texts):
    button_surface = pygame.Surface((SCREEN_WIDTH // 3, SCREEN_HEIGHT), pygame.SRCALPHA)
    button_surface.fill(COLOR_MENU)

    # Boutons avec texte centré
    if len(button_texts) == 1:
        button_rects = [placeButtonAtPercent(80)]
    else:
        button_rects = [placeButtonAtPercent(40 + (15*x)) for x in range(len(button_texts))]
    mouseOn = "none"

    for rect, text in zip(button_rects, button_texts):
        button_color = COLOR_BUTTON
        if rect.collidepoint(pos):
            button_color = COLOR_BUTTON_HOVER
            mouseOn = text
            # NEED_UPDATE = True
        pygame.draw.rect(button_surface, button_color, rect)
        draw_text_centered(button_surface, text, title_font, (255, 255, 255), rect)
    image_rect = logo.get_rect(center=(WPC * 50, HPC * 20))
    button_surface.blit(logo, image_rect)

    return button_surface, mouseOn

def main():
    # init de pygame
    pygame.init()
    pygame.font.init()
    clock = pygame.time.Clock()

    # choix de font et création de la fenetre
    # title_font = pygame.font.SysFont('Comic Sans MS', 50)
    infoObject = pygame.display.Info()
    screen, title_font, little_font = updateScreenSize(infoObject.current_w, infoObject.current_h, True)
    # screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)

    # Creation du rectangle contenant la surface de jeu (partie droite de l'ecran)
    game_surface = pygame.Surface((SCREEN_WIDTH // 3 * 2, SCREEN_HEIGHT), pygame.SRCALPHA)

    # Chargement de l'arriere plan 
    background_img = pygame.image.load("./images/bois bg.jpg").convert()
    background_img = pygame.transform.scale(background_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

    # Chargement du logo, scale a la bonne taille en conservant le ratio HEIGHT/WIDTH
    logo = pygame.image.load("./images/logo gomoku.png")
    aspect_ratio = logo.get_height() / logo.get_width()
    newH = 30 * HPC
    newW =  newH / aspect_ratio
    # newH = newW * aspect_ratio
    # newW = 1/2 * WPC * 100
    logo = pygame.transform.scale(logo, (newW, newH))

    # HUD sur la gauche
    hud_left = pygame.Surface((SCREEN_WIDTH // 3, SCREEN_HEIGHT), pygame.SRCALPHA)
    hud_left.fill(COLOR_MENU)
    image_rect = logo.get_rect(center=(WPC * 50, HPC * 20))
    hud_left.blit(logo, image_rect)


    # noms des bouttons du menu
    menu_accueil = ["JOUER", "OPTIONS", "QUITTER"]
    menu_jouer = ["SOLO", "PARTIE LOCAL", "RETOUR"]
    menu_option = ["PLEIN ECRAN", "FENÊTRÉ", "RETOUR"]
    menu_fenetre = ["1280X720", "1600X900", "1920X1080", "RETOUR"]
    menu_ingame = ["RETOUR"]

    menu_actif = menu_accueil
    run = True
    
    game = Game()
    # Boucle principale du jeu
    # global NEED_UPDATE
    # NEED_UPDATE = True
    while run:
        clock.tick(60) # 60 fps max
        pos = pygame.mouse.get_pos()

        # necessaire uniquement lors d'un changement de taille de screen
        screen.blit(background_img, (0, 0))
        newH = 30 * HPC
        newW =  newH / aspect_ratio
        logo = pygame.transform.scale(logo, (newW, newH))
        game_surface = pygame.Surface((SCREEN_WIDTH // 3 * 2, SCREEN_HEIGHT), pygame.SRCALPHA)

        # creation du menu
        mouseOn = "none"

        if menu_actif != "none":
            menu_surface, mouseOn = getMenu(title_font, pos, logo, menu_actif)

        # # affiche le plateau du jeu dans la grande zone
        # if menu_actif == menu_ingame:
        #     gameState = draw_gomoku_board(screen, game_surface, game, pos, event)
        #     # if (gameState == "reset"):
        #     #     game.reset()
        #     screen.blit(game_surface, ((SCREEN_WIDTH // 3, 0)))
        #     game.dispInfoOn(menu_surface, little_font)
        #     screen.blit(menu_surface, (0, 0))
        #     if (game.inGame == False):
        #         draw_end_game_screen(screen, game)
        # if menu_actif != menu_ingame:
        #     screen.blit(menu_surface, (0, 0))


            # NEED_UPDATE = False

        # if not NEED_UPDATE:
        #         screen.blit(menu_surface, (0, 0))
        # print(mouseOn)

        # gestion des events
        clickedOutside = False
        for event in pygame.event.get():
            # if event.type in [pygame.MOUSEBUTTONDOWN, pygame.QUIT]:  
                # NEED_UPDATE = True  # On force un refresh si un bouton est cliqué ou si on quitte
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pos[0] > SCREEN_WIDTH // 3:
                    clickedOutside = True
                elif mouseOn == "JOUER":
                    menu_actif = menu_jouer
                    # NEED_UPDATE = True  # Nécessaire car on change d'écran
                elif mouseOn == "OPTIONS":
                    menu_actif = menu_option
                    # NEED_UPDATE = True
                elif mouseOn == "QUITTER":
                    run = False
                elif mouseOn == "PARTIE LOCAL":
                    menu_actif = menu_ingame
                    # NEED_UPDATE = True
                    game.startGame()
                elif mouseOn == "PLEIN ECRAN":
                    screen, title_font, little_font = updateScreenSize(infoObject.current_w, infoObject.current_h, True)
                elif mouseOn == "FENÊTRÉ":
                    menu_actif = menu_fenetre
                    # NEED_UPDATE = True
                elif mouseOn == "1280X720":
                    screen, title_font, little_font = updateScreenSize(1280, 720, False)
                    # NEED_UPDATE = True
                elif mouseOn == "1600X900":
                    screen, title_font, little_font = updateScreenSize(1600, 900, False)
                    # NEED_UPDATE = True
                elif mouseOn == "1920X1080":
                    screen, title_font, little_font = updateScreenSize(1920, 1080, False)
                    # NEED_UPDATE = True
                elif mouseOn == "RETOUR":
                    if menu_actif == menu_fenetre:
                        menu_actif = menu_option
                    else:
                        menu_actif = menu_accueil
                    # NEED_UPDATE = True
                    game.reset()
            if event.type == pygame.QUIT:
                run = False
        # affiche le plateau du jeu dans la grande zone
        if menu_actif == menu_ingame:
            gameState = draw_gomoku_board(screen, game_surface, game, pos, clickedOutside)
            # if (gameState == "reset"):
            #     game.reset()
            screen.blit(game_surface, ((SCREEN_WIDTH // 3, 0)))
            game.dispInfoOn(menu_surface, little_font)
            screen.blit(menu_surface, (0, 0))
            if (game.inGame == False):
                draw_end_game_screen(screen, game)
        if menu_actif != menu_ingame:
            screen.blit(menu_surface, (0, 0))
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
