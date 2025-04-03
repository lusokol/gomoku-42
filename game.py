import random
import pygame
import config
from utile import placeButtonAtPercent, draw_text_in_rect

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
        # self.board = [["." if _ % 3 == 0 else "1" if _ % 3 == 1 else "2" for _ in range(config.GRID_SIZE)] for _ in range(config.GRID_SIZE)]
        self.board = [["." for _ in range(config.GRID_SIZE)] for _ in range(config.GRID_SIZE)]
    
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
                    if 0 <= r < config.GRID_SIZE and 0 <= c < config.GRID_SIZE and self.board[r][c] == symbol:
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
