import config
import pygame


def placeButtonAtPercent(percent, size=10):
    """Retourne un rectangle positionné en pourcentage sur l'écran."""
    return pygame.Rect(
        config.WPC * 10,
        config.HPC * percent,
        config.WPC * 80,
        config.HPC * size,
    )


def draw_text_centered(surface, text, font, color, rect):
    """Dessine le texte centré dans un rectangle donné."""
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=rect.center)
    surface.blit(text_surface, text_rect)


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
        rect.height - 2 * margin,
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


# def draw_end_game_screen(screen, game):
#     """
#     Dessine un écran de fin de partie avec un rectangle transparent contenant des informations de la partie.

#     Args:
#         screen: Surface Pygame sur laquelle dessiner.
#         game: Objet contenant les informations de la partie (turn, p1, p2, time).
#     """
#     # Dimensions et position du rectangle
#     rect_width = int(config.SCREEN_WIDTH * 0.8)
#     rect_height = int(config.SCREEN_HEIGHT * 0.8)
#     rect_x = (config.SCREEN_WIDTH - rect_width) // 2
#     rect_y = (config.SCREEN_HEIGHT - rect_height) // 2

#     # Création d'une surface transparente
#     transparent_surface = pygame.Surface((rect_width, rect_height), pygame.SRCALPHA)
#     transparent_surface.fill((102, 51, 0, 200))  # Marron foncé transparent à 20%

#     # Blitter le rectangle sur l'écran
#     screen.blit(transparent_surface, (rect_x, rect_y))

#     # Préparer les informations
#     font = pygame.font.SysFont("Comic Sans MS", 40)
#     text_color = (255, 255, 255)  # Blanc

#     winner = game.p1 if game.turn % 2 == 1 else game.p2
#     lines = [
#         f"Gagnant : {game.winner} par {game.winnerBy}",
#         f"Joueur 1 : {game.p1}",
#         f"Joueur 2 : {game.p2}",
#         f"Temps de la partie : {game.time.getEndTime()}",
#         f"Nombre de tours : {game.turn}",
#     ]

#     # Calcul de la position de départ pour centrer verticalement le texte
#     text_margin = 20
#     y_start = rect_y + text_margin

#     # Afficher chaque ligne de texte
#     for idx, line in enumerate(lines):
#         text_surface = font.render(line, True, text_color)
#         text_rect = text_surface.get_rect(
#             midtop=(config.SCREEN_WIDTH // 2, y_start + idx * 60)
#         )  # 60px entre chaque ligne
#         screen.blit(text_surface, text_rect)

def draw_end_game_screen(screen, game, title_font, little_font):
    """
    Dessine un écran de fin de partie avec un rectangle transparent contenant des informations de la partie,
    ainsi que deux boutons : 'Accueil' et 'Rejouer'.

    Args:
        screen: Surface Pygame sur laquelle dessiner.
        game: Objet contenant les informations de la partie.
        title_font: Police pour les titres.
        little_font: Police pour les petits textes.
    """
    # Dimensions et position du rectangle
    rect_width = int(config.SCREEN_WIDTH * 0.8)
    rect_height = int(config.SCREEN_HEIGHT * 0.6)
    rect_x = (config.SCREEN_WIDTH - rect_width) // 2
    rect_y = (config.SCREEN_HEIGHT - rect_height) // 2

    # Surface transparente
    transparent_surface = pygame.Surface((rect_width, rect_height), pygame.SRCALPHA)
    transparent_surface.fill(config.COLOR_MENU)
    screen.blit(transparent_surface, (rect_x, rect_y))

    text_color = (255, 255, 255)
    separator_color = (255, 255, 255)

    lines = [
        f"Gagnant : {game.winner} par {game.winnerBy}",
        f"Temps de la partie : {game.time.getEndTime()}",
        f"Nombre de tours : {game.turn}",
    ]

    # Titre
    y_start = rect_y + 20
    title_surface = title_font.render("Fin de la Partie", True, text_color)
    title_rect = title_surface.get_rect(midtop=(config.SCREEN_WIDTH // 2, y_start))
    screen.blit(title_surface, title_rect)
    y_start += title_rect.height + 30

    # Infos
    for idx, line in enumerate(lines):
        text_surface = little_font.render(line, True, text_color)
        text_rect = text_surface.get_rect(
            midtop=(config.SCREEN_WIDTH // 2, y_start + idx * 60)
        )
        screen.blit(text_surface, text_rect)

    # Ligne de séparation
    separator_y = y_start + len(lines) * 60 + 40
    pygame.draw.line(screen, separator_color, (rect_x + 20, separator_y), (rect_x + rect_width - 20, separator_y), 2)

    # Dimensions des boutons
    button_height = int(rect_height * 0.1)
    button_width = int(rect_width * 0.4)
    button_spacing = int(rect_width * 0.05)

    total_buttons_width = button_width * 2 + button_spacing
    button_start_x = rect_x + (rect_width - total_buttons_width) // 2
    button_y = rect_y + rect_height - button_height - 20

    mouse_pos = pygame.mouse.get_pos()

    # Bouton "Accueil"
    accueil_rect = pygame.Rect(button_start_x, button_y, button_width, button_height)
    accueil_hover = accueil_rect.collidepoint(mouse_pos)
    accueil_color = config.COLOR_BUTTON_HOVER if accueil_hover else config.COLOR_BUTTON
    pygame.draw.rect(screen, accueil_color, accueil_rect)
    accueil_text = little_font.render("Accueil", True, text_color)
    accueil_text_rect = accueil_text.get_rect(center=accueil_rect.center)
    screen.blit(accueil_text, accueil_text_rect)

    # Bouton "Rejouer"
    rejouer_rect = pygame.Rect(button_start_x + button_width + button_spacing, button_y, button_width, button_height)
    rejouer_hover = rejouer_rect.collidepoint(mouse_pos)
    rejouer_color = config.COLOR_BUTTON_HOVER if rejouer_hover else config.COLOR_BUTTON
    pygame.draw.rect(screen, rejouer_color, rejouer_rect)
    rejouer_text = little_font.render("Rejouer", True, text_color)
    rejouer_text_rect = rejouer_text.get_rect(center=rejouer_rect.center)
    screen.blit(rejouer_text, rejouer_text_rect)

    return {
        "accueil": accueil_hover,
        "rejouer": rejouer_hover,
    }




def draw_gomoku_board(
    screen,
    game_area,
    game,
    mouse_pos,
    event,
    board_size=19,
    percentage=0.8,
    line_color=(0, 0, 0),
    background_color=(255, 223, 186, 0),
):
    """
    Dessine un plateau de Gomoku centré sur l'écran avec une taille basée sur 80% de l'axe le plus grand.

    Args:
        game_area: Surface de Pygame sur laquelle dessiner.
        board_size: Nombre de lignes/colonnes du plateau (par défaut 19).
        percentage: Proportion de l'axe le plus grand pour définir la taille du plateau (par défaut 0.8).
        line_color: Couleur des lignes de la grille (par défaut noir).
        background_color: Couleur de fond du plateau (par défaut beige).
    """
    config.screen_width, config.screen_height = game_area.get_size()

    # Taille du plateau basée sur 80% de l'axe le plus grand
    board_pixel_size = int(min(config.screen_width, config.screen_height) * percentage)
    cell_size = board_pixel_size // (board_size - 1)  # Taille d'une cellule en pixels
    piece_size = cell_size * 0.4  # Taille d'un pion

    # Calcul des marges pour centrer le plateau
    margin_x = (config.screen_width - board_pixel_size) // 2
    margin_y = (config.screen_height - board_pixel_size) // 2

    # Remplir le fond avec la couleur de fond
    game_area.fill(background_color)

    # Dessiner un rectangle dépassant de 50px autour du plateau
    rectangle_margin = 50
    rectangle_color = (255, 223, 186)
    rectangle_rect = pygame.Rect(
        margin_x - rectangle_margin,
        margin_y - rectangle_margin,
        board_pixel_size + 2 * rectangle_margin,
        board_pixel_size + 2 * rectangle_margin,
    )
    pygame.draw.rect(game_area, rectangle_color, rectangle_rect)

    # Dessiner les lignes horizontales
    for i in range(board_size):
        y = margin_y + i * cell_size
        pygame.draw.line(
            game_area,
            line_color,
            (margin_x, y),
            (margin_x + board_pixel_size, y),
        )

    # Dessiner les lignes verticales
    for j in range(board_size):
        x = margin_x + j * cell_size
        pygame.draw.line(
            game_area,
            line_color,
            (x, margin_y),
            (x, margin_y + board_pixel_size),
        )

    # Dessiner les intersections spéciales (hoshi)
    hoshi_positions = [
        (3, 3),
        (3, 9),
        (3, 15),
        (9, 3),
        (9, 9),
        (9, 15),
        (15, 3),
        (15, 9),
        (15, 15),
    ]
    for row, col in hoshi_positions:
        center_x = margin_x + col * cell_size
        center_y = margin_y + row * cell_size
        pygame.draw.circle(game_area, line_color, (center_x, center_y), 5)

    for idx_line, line in enumerate(game.board):
        for idx_col, cross in enumerate(line):
            if cross == "1":
                center_x = margin_x + idx_col * cell_size
                center_y = margin_y + idx_line * cell_size
                pygame.draw.circle(
                    game_area,
                    config.STONE_BLACK,
                    (center_x, center_y),
                    piece_size,
                )
            if cross == "2":
                center_x = margin_x + idx_col * cell_size
                center_y = margin_y + idx_line * cell_size
                pygame.draw.circle(
                    game_area,
                    config.STONE_WHITE,
                    (center_x, center_y),
                    piece_size,
                )
                pygame.draw.circle(
                    game_area,
                    config.STONE_BLACK,
                    (center_x, center_y),
                    piece_size,
                    2,
                )

    # # Vérification des collisions avec les rectangles
    if game.inGame is True:
        adjusted_mousePos = (
            mouse_pos[0] - config.SCREEN_WIDTH // 3,
            mouse_pos[1],
        )
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
                    if mousePressed is True:
                        game.playAt((row, col))
                    else:
                        # Dessiner une pierre semi-transparente
                        stone_color = (
                            config.STONE_BLACK
                            if game.whoPlay == "p1"
                            else config.STONE_WHITE
                        )
                        alpha = 128  # Transparence (50%)
                        overlay = pygame.Surface(
                            (piece_size * 2, piece_size * 2), pygame.SRCALPHA
                        )
                        pygame.draw.circle(
                            overlay,
                            (*stone_color, alpha),
                            (piece_size, piece_size),
                            piece_size,
                        )
                        if game.whoPlay == "p2":
                            pygame.draw.circle(
                                overlay,
                                (*config.STONE_BLACK, alpha),
                                (piece_size, piece_size),
                                piece_size,
                                2,
                            )
                        game_area.blit(
                            overlay,
                            (
                                rect.centerx - piece_size,
                                rect.centery - piece_size,
                            ),
                        )
