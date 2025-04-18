import random
import pygame
import config
from config import codes
from copy import deepcopy
from utile import placeButtonAtPercent, draw_text_in_rect, show_notification


class Game:
    def __init__(self):
        self.reset()

    class Time:
        def __init__(self):
            self.startTime = 0
            self.seconde = 0
            self.minute = 0
            self.heure = 0
            self.endSeconde = 0
            self.endMinute = 0
            self.endHeure = 0

        def start(self):
            self.startTime = pygame.time.get_ticks()

        def stop(self):
            self.endSeconde = self.seconde
            self.endMinute = self.minute
            self.endHeure = self.heure

        def updateTime(self):
            elapsed_time = (
                pygame.time.get_ticks() - self.startTime
            ) // 1000  # Temps écoulé en secondes
            self.heure = elapsed_time // 3600
            self.minute = (elapsed_time % 3600) // 60
            self.seconde = elapsed_time % 60

        def getTime(self):
            self.updateTime()
            return f"{self.heure:02}h{self.minute:02}m{self.seconde:02}s"

        def getEndTime(self):
            return f"{self.endHeure:02}h{self.endMinute:02}m{self.endSeconde:02}s"

    def reset(self):
        """Réinitialise le jeu à l'état initial."""
        self.inGame = False
        self.turn = 1
        self.time = self.Time()
        self.start_time = 0
        self.last_move = None
        self.p1_piece = 0
        self.p2_piece = 0
        self.winner = ""
        self.winnerBy = ""
        self.isAIgame = False
        self.AIdifficulty = "FACILE"
        self.whoStart = "p1" if self.startPlayer() else "p2"
        self.IAplayer = "p1" if self.whoStart == "p2" else "p2"
        self.whoPlay = (
            self.whoStart
            if (self.turn % 2)
            else "p1"
            if (self.whoStart == "p2")
            else "p2"
        )
        self.p1 = "Joueur 1"
        self.p2 = "Joueur 2"
        self.board = [
            ["." for _ in range(config.GRID_SIZE)] for _ in range(config.GRID_SIZE)
        ]
        self.pending_win = None
        self.history = []

    def startGame(self):
        self.inGame = True
        self.time.start()

    def startAIgame(self):
        self.isAIgame = True
        self.inGame = True
        self.startMusic()
        self.time.start()

    def startMusic(self):
        if self.AIdifficulty == "FACILE":
            config.sound_manager.load_music("sounds/facile.ogg")
        elif self.AIdifficulty == "MOYEN":
            config.sound_manager.load_music("sounds/moyen.ogg")
        else:
            config.sound_manager.load_music("sounds/impossible.ogg")
        config.sound_manager.play_music()

    def setAIdifficulty(self, difficulty):
        self.AIdifficulty = difficulty

    def getDifficulty(self):
        return {
            "FACILE": 1,
            "MOYEN": 2,
            "IMPOSSIBLE": 3,
        }.get(self.AIdifficulty, 1)

    def makeMove(self, x, y, player):
        """Record move from player"""
        self.board[x][y] = player

    def undoLastMove(self):
        """Undo the last move played by simulation."""
        if not self.history:
            print("Aucun coup à annuler.")
            return

        last_move = self.history.pop()  # On récupère et retire le dernier move

        for action in reversed(last_move):  # On annule les actions dans l’ordre inverse
            x, y = action["coords"]
            symbol = action["symbol"]
            effect = action["effect"]

            if effect == "add":
                self.board[x][y] = "."  # On enlève le pion ajouté
            elif effect == "remove":
                self.board[x][y] = symbol  # On remet le pion retiré

                # Remettre le nombre de pion capturés
                if symbol == "1":
                    self.p1_piece -= 1
                else:
                    self.p2_piece -= 1

        # Remettre le tour précédent
        self.turn -= 1
        self.whoPlay = (
            self.whoStart
            if self.turn % 2 == 0
            else "p1"
            if self.whoStart == "p2"
            else "p2"
        )

    def isDone(self):
        """Collect info if game is done or still running"""
        if self.inGame is False:
            return True
        return False

    def printBoard(self):
        for i in range(19):
            print(self.board[i])

    def getPossibleMoves(self):
        return [
            (x, y)
            for y in range(config.GRID_SIZE)
            for x in range(config.GRID_SIZE)
            if self.board[x][y] == "."
        ]
        radius = 2
        moves = []

        if self.last_move is None:
            # First move: return center
            size_x, size_y = len(self.board), len(self.board[0])
            return [(size_x // 2, size_y // 2)]

        x0, y0 = self.last_move
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                x, y = x0 + dx, y0 + dy
                if 0 <= x < len(self.board) and 0 <= y < len(self.board[0]):
                    if self.board[x][y] == ".":
                        moves.append((x, y))
        return moves
    
    def check_alignments(self, player) -> int:
        """check_alignments is a helper function for our great check_board function.
        It will study the board since the last move that was played;
        from there, it will calculate the surrounding alignments;
        thus returning the total amount of scores that will compose our comparison code;"""
        if self.last_move is None:
            return 0

        directions = {
            "horizon": (1, 0),
            "vertical": (0, 1),
            "diago_down": (1, 1),
            "diago_up": (1, -1)
        }
        
        score_board = {
            0: "OPEN",
            1: "SEMI",
            2: "CLOSED"
        }
        
        scores = {}

        total_score = 0
        symbol = self.getSymbolFromPlayer(player)
        board = self.board
        height = len(board)
        width = len(board[0])
        coord_x, coord_y = self.last_move
        
        def inBounds(x, y):
            """We simply check if the current element we are working on is indeed inside of the grid"""
            return 0 <= x < width and 0 <= y < height

        for direction_name, (dx, dy) in directions.items(): #we start the counter at one since we have placed a tile
            count = 1
            ends = 0
            score = 0
            
            for dir in [-1, 1]:  #check both sides 
                for i in range(1, 5):
                    x = coord_x + dir * dx * i
                    y = coord_y + dir * dy * i
                    if not inBounds(x, y, width, height):
                        ends += 1
                        break
                    if board[y][x] == symbol: #if symbol is met then add 1 to count => alignment
                        count += 1
                    elif board[y][x] == ".": #break => the alignment is broken
                        break
                    else:
                        ends += 1
                        break
                    
            if count >= 5:
                score += codes.get(f"{player}_5", 999999)
            elif count == 1:
                score += codes.get(f"{player}_1", 0)        
            else:
                score += codes.get(f"{player}_{count}_{score_board[ends]}", 0)

            total_score += score
        
        return total_score
        

    def check_last_capture(self, player):
        score = 0
        nb_capture = 0
        if len(self.history) > 0:
            nb_capture = sum(1 for move in self.history[-1] if move["effect"] == "remove")
            nb_piece = self.p1_piece if player == "J1" else self.p2_piece
            index_start = (nb_piece - nb_capture) / 2
            max_index = 4 #len(config.codes[f"{player}_C"]) - 1
            score += sum(config.codes[f"{player}_C"][min(index_start + i, max_index)] for i in range(nb_capture / 2))
        return score            

    def checkBoard(self, player):
        pToJ = {
            "p1": "J1",
            "p2": "J2"
        }
        opponent = "p1" if player == "p2" else "p2"
        symbol = self.getSymbolFromPlayer(player)
        opp_symbol = self.getSymbolFromPlayer(opponent)

        score_total = 0

        if (self.last_move is not None):
            # appelle des fonctions de check par rapport aux coords "self.last_move"
            score_alignments = self.check_alignments() # doit return [{"H": 4}, {"DM": 3}] arg1 :("H", "V", "DM", "DD") arg2: nb piece aligned
            score_block = self.check_blocks()
            score_capture = self.check_last_capture(pToJ[player]) # doit return le score du total des captures par rapport au last move
            score_total = score_alignments + score_block + score_capture
            # coder le cumule du score
        return score_total


        # else:
            # jouer le plus au centre possible ET voir score en fonction du coup adverse s'il a joué
    



    
        # opponent = "p1" if player == "p2" else "p2"
        # symbol = self.getSymbolFromPlayer(player)
        # opp_symbol = self.getSymbolFromPlayer(opponent)

        # score = 0
        # center_x, center_y = len(self.board[0]) // 2, len(self.board) // 2

        # # Center priority (higher score for playing closer to the center)
        # for y in range(len(self.board)):
        #     for x in range(len(self.board[0])):
        #         dist = abs(center_x - x) + abs(center_y - y)
        #         cell = self.board[y][x]
        #         if cell == symbol:
        #             score += max(0, 10 - dist)
        #         elif cell == opp_symbol:
        #             score -= max(0, 10 - dist)

        # # Pattern evaluation (alignments and blocking)
        # for y in range(len(self.board)):
        #     for x in range(len(self.board[0])):
        #         for current_symbol, is_player in [(symbol, True), (opp_symbol, False)]:
        #             align_len, open_ends = self.checkLines(current_symbol, (y, x))
        #             # Win Condition
        #             if align_len >= 5:
        #                 return 10000 if is_player else -10000
        #             # Evaluate alignments
        #             pattern_score = 0
        #             if align_len == 4 and open_ends >= 1:
        #                 pattern_score = 8000  # Strong alignment for player
        #             elif align_len == 3 and open_ends >= 1:
        #                 pattern_score = 5000  # Potential win
        #             elif align_len == 2:
        #                 pattern_score = 2000  # Build-up toward winning

        #             # Slightly stronger defense if opponent
        #             if not is_player:
        #                 pattern_score *= -1.3

        #             score += pattern_score

        # # Add pending win bonus (this gives extra weight to winning moves)
        # if self.pending_win and self.pending_win["player"] == player:
        #     score += 10000
        # elif self.pending_win and self.pending_win["player"] == opponent:
        #     score -= 10000

        # return score

    def minimax(self, game, depth, alpha, beta, maxim):
        """The minimax algorithm works as follows: A Game Tree
        On one side, we have the root situation (the current game state we are in);
        Then, the study of the next moves that could be seen as nodes from that tree.
        At each depth, we iterate bewteen maximizing (maxim) and minimizing player.

        The 2 players are against each other:
        Maximizing Player => Aims to maximize their advantage;
        Minimizing Player => Aims to minimize the maximizing player's advantage

        We store the evident advantage in a score variable.

        We have 2 states : game is finished vs game is not finished.
        In the first case, the game was either won, tied or lost;
        In the second case, the game is ongoing and the algo will return the score afer
        evaluating the state of the game.

        Maximizing Player's move : the algo looks for the moves that would increase
        the maximizing player's chances of winning.
        Minimizing Player's move : the algo looks for the moves that would decrease
        those chances by returning the lowest score.

        This is done in a recursive fashion => when depth == 0 => evaluation is over and game state has been evaluated.

        Depth == 0
        When Depth reaches zero, the evaluation is done. The game state is ready. The scores have been given.
        A positive score will be given for the Maximizing,
        A negative score will be given for the Minimizing,
        A zero score if it is a tie.

        The algo returns the top_move variable that has been found in the tree.

        We use the Alpha-Beta pruning method.
        Alpha-Beta => ignoring the branches that do not give an interesting score whatsoever.
        Alpha = best value for Maximizing Player;
        Beta = best value for Minimizing Player;

        In our case, if Beta <= Alpha,
        We break and stop the evaluation on this branch because we will not find anything better.
        """
        # If given depth is Zero we return the current game state and None as nothing will be evaluated
        if depth == 0 or game.isDone():
            return (
                game.checkBoard(game.whoPlay),
                None,
            )  # Always evaluate from the AI's original perspective

        top_move = None
        current_player = game.whoPlay
        next_player = "p2" if current_player == "p1" else "p1"

        if maxim:
            max_check = float("-inf")
            for move in game.getPossibleMoves():
                x, y = move
                game.playAt((x, y))
                game.whoPlay = next_player  # switch turn
                eval, _ = game.minimax(game, depth - 1, alpha, beta, False)
                game.undoLastMove()
                game.whoPlay = current_player  # revert

                if eval > max_check:
                    max_check = eval
                    top_move = move
                alpha = max(alpha, eval)

                if beta <= alpha:
                    break

            return max_check, top_move

        else:
            min_check = float("inf")
            for move in game.getPossibleMoves():
                x, y = move
                game.playAt((x, y))
                game.whoPlay = next_player  # switch turn
                eval, _ = game.minimax(game, depth - 1, alpha, beta, True)
                game.undoLastMove()
                game.whoPlay = current_player  # revert

                if eval < min_check:
                    min_check = eval
                    top_move = move
                beta = min(beta, eval)

                if beta <= alpha:
                    break

            return min_check, top_move

    def getAImove(self):
        depth = self.getDifficulty()
        game_copy = deepcopy(self)
        game_copy.isAIgame = False
        _, move = self.minimax(
            game_copy, depth, alpha=float("-inf"), beta=float("inf"), maxim=True
        )
        return move

    def startPlayer(self):
        """Détermine aléatoirement qui commence."""
        return bool(random.getrandbits(1))

    def dispInfoOn(self, surface, font):
        rect = placeButtonAtPercent(40, 35)
        pygame.draw.rect(surface, (0, 0, 0), rect, 7)
        # text_surface = font.render("Tour de " + playerTurn, True, (0, 0, 0))
        # text_rect = text_surface.get_rect(topleft=rect.topleft + (50, 50))

        text_lines = [
            f"Temps écoulé : {self.time.getTime()}",
            "Tour " + str(self.turn) + ".",
            "Aux " + ("noirs" if (self.whoPlay == "p1") else "blancs") + " de jouer.",
            f"Les noirs ont capturé {self.p1_piece} pions.",
            f"Les blancs ont capturé {self.p2_piece} pions.",
        ]
        draw_text_in_rect(surface, rect, text_lines, font)
        # surface.blit(text_surface, text_rect)

    def addCapturePiece(self):
        if self.whoPlay == "p1":
            self.p1_piece += 1
        else:
            self.p2_piece += 1

    def setWinner(self, winner=None):
        if winner is None:
            self.winner = "Noirs" if self.whoPlay == "p1" else "Blancs"
        elif self.p1_piece >= 10:
            self.winner = "Noirs"
            self.winnerBy = "capture"
        elif self.p2_piece >= 10:
            self.winner = "Blancs"
            self.winnerBy = "capture"
        elif self.whoPlay == "p1":
            self.winner = "Noirs"
            self.winnerBy = "alignement"
        elif self.whoPlay == "p2":
            self.winner = "Blancs"
            self.winnerBy = "alignement"

    def setDraw(self):
        self.winner = "draw"
        print("Égalité !")

    def getSymbolFromPlayer(self, player):
        return "1" if player == "p1" else "2"

    def nextTurn(self):
        self.turn += 1

        self.whoPlay = (
            self.whoStart
            if (self.turn % 2)
            else "p1"
            if (self.whoStart == "p2")
            else "p2"
        )

    def playAt(self, coords, IAmoved=False):
        tmp_history = []
        symbol = "1" if self.whoPlay == "p1" else "2"
        isCapture, pieceCaptured = self.check_if_capture(coords, symbol)

        if isCapture or self.checkIfAutorized(coords, symbol):
            self.board[coords[0]][coords[1]] = symbol
            tmp_history.append(
                {"coords": (coords[0], coords[1]), "symbol": symbol, "effect": "add"}
            )
            self.last_move = coords

            if isCapture:
                for piece in pieceCaptured:
                    tmp_history.append(
                        {
                            "coords": (piece[0], piece[1]),
                            "symbol": self.board[piece[0]][piece[1]],
                            "effect": "remove",
                        }
                    )
                    self.board[piece[0]][piece[1]] = "."
                    self.addCapturePiece()

            # Si une victoire est en attente, on vérifie maintenant si elle est toujours valide
            if self.pending_win:
                still_winning = self.checkAlignments(
                    self.getSymbolFromPlayer(self.pending_win["player"]),
                    self.pending_win["coords"],
                )
                if still_winning:
                    current_align = self.checkAlignments(symbol, coords)
                    if current_align and self.pending_win["player"] != self.whoPlay:
                        # les deux joueurs font un alignement en même temps -> égalité
                        self.time.stop()
                        self.setDraw()
                    else:
                        # l'adversaire n'a pas cassé la ligne → victoire du joueur initial
                        self.time.stop()
                        self.setWinner(self.pending_win["player"])
                    self.inGame = False
                    self.pending_win = None
                    return
                else:
                    # ligne cassée → la partie continue
                    self.pending_win = None

            # Vérifie s'il y a une nouvelle ligne gagnante
            if self.checkAlignments(symbol, coords):
                if self.checkIfLineIsBreakable(symbol, coords):
                    self.pending_win = {"player": self.whoPlay, "coords": coords}
                    self.nextTurn()
                else:
                    self.time.stop()
                    self.setWinner()
                    self.inGame = False
            elif max(self.p1_piece, self.p2_piece) >= 10:
                self.time.stop()
                self.setWinner()
                self.inGame = False
            else:
                self.nextTurn()

            if self.isAIgame is True:
                if self.whoPlay == self.IAplayer and self.inGame:
                    self.getDifficulty()
                    ai_move = self.getAImove()
                    if IAmoved is not True:
                        self.playAt(ai_move, True)
                    else:
                        self.nextTurn()
        else:
            show_notification("Double free three interdit !")
        self.history.append(tmp_history)

    def check_if_capture(self, coords, symbol):
        row, col = coords
        board = self.board

        # Vérifier si la case est déjà occupée
        if board[row][col] != ".":
            return False, []

        # Directions à vérifier pour trouver des captures
        directions = [
            (0, 1),  # Droite
            (0, -1),  # Gauche
            (1, 0),  # Bas
            (-1, 0),  # Haut
            (1, 1),  # Diagonale descendante droite
            (-1, -1),  # Diagonale montante gauche
            (1, -1),  # Diagonale descendante gauche
            (-1, 1),  # Diagonale montante droite
        ]

        actual_player = symbol
        opponent = "1" if symbol == "2" else "2"
        captured_pawns = []

        for dr, dc in directions:
            # Vérifier la présence de deux pions adverses consécutifs
            first_opponent = (row + dr, col + dc)
            second_opponent = (row + 2 * dr, col + 2 * dc)
            end_cell = (row + 3 * dr, col + 3 * dc)

            if (
                self.is_within_bounds(first_opponent)
                and board[first_opponent[0]][first_opponent[1]] == opponent
                and self.is_within_bounds(second_opponent)
                and board[second_opponent[0]][second_opponent[1]] == opponent
                and self.is_within_bounds(end_cell)
                and board[end_cell[0]][end_cell[1]] == actual_player
            ):
                captured_pawns.extend([first_opponent, second_opponent])

        return (len(captured_pawns) > 0), captured_pawns

    def is_within_bounds(self, coords):
        row, col = coords
        return 0 <= row < len(self.board) and 0 <= col < len(self.board[0])

    def checkIfLineIsBreakable(self, symbol, coords):
        directions = [
            (0, 1),  # Horizontal
            (1, 0),  # Vertical
            (1, 1),  # Diagonale descendante
            (1, -1),  # Diagonale montante
        ]
        each_piece = []
        each_piece.append({"r": coords[0], "c": coords[1]})
        for dv, dh in directions:
            for step in [-1, 1]:
                r, c = coords
                while True:
                    r += step * dv
                    c += step * dh
                    if (
                        0 <= r < config.GRID_SIZE
                        and 0 <= c < config.GRID_SIZE
                        and self.board[r][c] == symbol
                    ):
                        each_piece.append({"r": r, "c": c})
                    else:
                        break
        board = self.board
        row, col = coords

        def is_capturable(start_row, start_col, dr, dc):
            """
            Vérifie si une "capture" existe dans une direction donnée.

            Args:
                start_row: Ligne de départ.
                start_col: Colonne de départ.
                dr: Delta ligne pour parcourir dans une direction.
                dc: Delta colonne pour parcourir dans une direction.

            Returns:
                bool: True si une capture est possible.
            """
            line = []
            for step in range(-3, 4):  # Vérifie jusqu'à 3 cases avant et après
                r = start_row + step * dr
                c = start_col + step * dc
                if 0 <= r < len(board) and 0 <= c < len(board[0]):
                    line.append(board[r][c])
                else:
                    line.append(None)

            # Chercher les motifs de capture possible
            opponent = "1" if symbol == "2" else "2"
            patterns = [
                [".", symbol, symbol, opponent],
                [opponent, symbol, symbol, "."],
            ]
            for pattern in patterns:
                if any(
                    line[i : i + len(pattern)] == pattern
                    for i in range(len(line) - len(pattern) + 1)
                ):
                    return True

            return False

        for coord in each_piece:
            for dr, dc in directions:
                if is_capturable(coord["r"], coord["c"], dr, dc):
                    return True  # si une capture est possible, la ligne est cassable

        # Si aucune capture n'est possible, la ligne n'est pas cassable
        return False

    def checkLines(self, symbol, start_pos):
        """
        Check all directions (horizontal, vertical, and both diagonals) for the longest alignment of the given symbol.
        """
        directions = [
            (1, 0),  # Horizontal
            (0, 1),  # Vertical
            (1, 1),  # Diagonal down-right
            (1, -1),  # Diagonal up-right
        ]

        max_len = 0
        open_spots = 0

        for dx, dy in directions:
            length = 1  # Start with the current position
            open_count = 0  # Track open spots
            # Check in both directions
            for direction in [-1, 1]:
                x, y = start_pos
                while True:
                    x += direction * dx
                    y += direction * dy
                    if 0 <= x < len(self.board[0]) and 0 <= y < len(self.board):
                        if self.board[y][x] == symbol:
                            length += 1
                        elif self.board[y][x] == ".":
                            open_count += 1
                        else:
                            break
                    else:
                        break
            max_len = max(max_len, length)
            open_spots += open_count

        return max_len, open_spots

    def checkAlignments(self, symbol, coords):
        directions = [
            (0, 1),  # Horizontal
            (1, 0),  # Vertical
            (1, 1),  # Diagonale descendante
            (1, -1),  # Diagonale montante
        ]
        for dv, dh in directions:
            count = 1
            for step in [-1, 1]:
                r, c = coords
                while True:
                    r += step * dv
                    c += step * dh
                    if (
                        0 <= r < config.GRID_SIZE
                        and 0 <= c < config.GRID_SIZE
                        and self.board[r][c] == symbol
                    ):
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
            (0, 1),  # Horizontal
            (1, 0),  # Vertical
            (1, 1),  # Diagonale descendante
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
                if any(
                    line[i : i + len(pattern)] == pattern
                    for i in range(len(line) - len(pattern) + 1)
                ):
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
