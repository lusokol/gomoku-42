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
                if symbol == "2":
                    self.p1_piece -= 1
                else:
                    self.p2_piece -= 1

        # Remettre le tour précédent
        self.turn -= 1
        self.whoPlay = (
            "p1" if self.whoPlay == "p2"
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
        """getPossiblemoves() will check the board only once and will add to the possible move set()
        the empty tiles found in the radius (i put it at 4 but of ocurse we can tweak that to our convenience).
        When we encoutner a tile (no matter the player color) and we check from there around the radius,
        we add it to the set as we know it won't be repeatung places in the boafrd anyways,
        and if there are repeating then they will be replaced as per the data type of the set();
        If we do not find anything, aka the board is empty, then we return the center psoition of the board"""
        radius = 4
        possible_moves = set()

        for x in range(config.GRID_SIZE):
            for y in range(config.GRID_SIZE):
                if self.board[x][y] != ".":
                    for dx in range(-radius, radius + 1):
                        for dy in range(-radius, radius + 1):
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < config.GRID_SIZE and 0 <= ny < config.GRID_SIZE:
                                if self.board[nx][ny] == ".":
                                    possible_moves.add((nx, ny))

        if not possible_moves:
            # Here if we cannot find any tile, then we just return the center
            center = config.GRID_SIZE // 2
            return [(center, center)]

        return list(possible_moves)

    
    def check_alignments(self, player, player_code) -> int:
        """
        check_alignments is a helper function for our great check_board function.
        It will study the board since the last move that was played;
        from there, it will calculate the surrounding alignments;
        thus returning the total amount of scores that will compose our comparison code;
        """
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

        total_score = 0
        symbol = self.getSymbolFromPlayer(player)
        board = self.board
        height = len(board)
        width = len(board[0])
        x0, y0 = self.last_move

        def inBounds(x, y):
            return 0 <= x < width and 0 <= y < height

        for (dx, dy) in directions.values():
            left_count = 0
            right_count = 0
            ends = 0

            # Check left direction (-dx, -dy)
            for i in range(1, 5):
                x = x0 - dx * i
                y = y0 - dy * i
                if not inBounds(x, y):
                    ends += 1
                    break
                if board[x][y] == symbol:
                    left_count += 1
                elif board[x][y] == ".":
                    break
                else:
                    ends += 1
                    break

            # Check right direction (+dx, +dy)
            for i in range(1, 5):
                x = x0 + dx * i
                y = y0 + dy * i
                if not inBounds(x, y):
                    ends += 1
                    break
                if board[x][y] == symbol:
                    right_count += 1
                elif board[x][y] == ".":
                    break
                else:
                    ends += 1
                    break

            count = 1 + left_count + right_count

            if count >= 5:
                score = codes.get(f"{player_code}_5", 999999)
            elif count == 1:
                score = 0 # codes.get(f"{player_code}_1", 0)
            else:
                closure = score_board.get(ends, "CLOSED")
                score = codes.get(f"{player_code}_{count}_{closure}", 0)

            total_score += score

        return total_score


    def check_blocks(self, player, player_code) -> int:
        """
        Calcule les points pour bloquer l'adversaire.
        On analyse depuis le dernier coup joué, et on regarde s'il bloque un alignement adverse dangereux.
        """
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

        total_score = 0
        symbol = self.getSymbolFromPlayer("p1" if player == "p2" else "p2")
        board = self.board
        height = len(board)
        width = len(board[0])
        x0, y0 = self.last_move

        def inBounds(x, y):
            return 0 <= x < width and 0 <= y < height

        for (dx, dy) in directions.values():
            left_count = 0
            right_count = 0
            ends = 1

            # Check left direction (-dx, -dy)
            for i in range(1, 5):
                x = x0 - dx * i
                y = y0 - dy * i
                if not inBounds(x, y):
                    ends += 1
                    break
                if board[x][y] == symbol:
                    left_count += 1
                elif board[x][y] == ".":
                    break
                else:
                    ends += 1
                    break

            # Check right direction (+dx, +dy)
            for i in range(1, 5):
                x = x0 + dx * i
                y = y0 + dy * i
                if not inBounds(x, y):
                    ends += 1
                    break
                if board[x][y] == symbol:
                    right_count += 1
                elif board[x][y] == ".":
                    break
                else:
                    ends += 1
                    break

            count = left_count + right_count

            if count >= 5:
                score = codes.get(f"{player_code}_BLOCK_5", 999999)
            elif count == 1:
                score = codes.get(f"{player_code}_BLOCK_1", 0)
            else:
                closure = score_board.get(ends, "CLOSED")
                score = codes.get(f"{player_code}_BLOCK_{count}_{closure}", 0)

            total_score += score

        return total_score

    def check_last_capture(self, player):
        score = 0
        nb_capture = 0
        if len(self.history) > 0:
            histo = self.history[-1]
            nb_capture = sum(1 for move in histo if move["effect"] == "remove")
            nb_piece = self.p1_piece if player == "J1" else self.p2_piece
            index_start = (nb_piece - nb_capture) // 2
            max_index = 4
            for i in range(int(nb_capture / 2)):
                score += sum(config.codes[f"{player}_C"][min(index_start + i, max_index)]for i in range(nb_capture // 2))
        return score       
    
    def evaluate_capture_risk(self, board, symbol, opponent_captures):
        opponent = "1" if symbol == "2" else "2"
        risk_score = 0

        # Table of risk scores depending on how many captures the opponent has made
        capture_risk_scores = [150, 500, 2000, 6000, 999999]

        if opponent_captures >= len(capture_risk_scores):
            score_from_table = capture_risk_scores[-1]
        else:
            score_from_table = capture_risk_scores[opponent_captures]

        directions = [
            (1, 0),
            (0, 1),
            (1, 1),
            (1, -1),
        ]

        for r in range(len(board)):
            for c in range(len(board[0])):
                if board[r][c] != symbol:
                    continue

                for dr, dc in directions:
                    try:
                        #Player - AI - AI - empty
                        r0, c0 = r - dr, c - dc
                        r1, c1 = r, c
                        r2, c2 = r + dr, c + dc
                        r3, c3 = r + 2*dr, c + 2*dc

                        if all(0 <= x < len(board) and 0 <= y < len(board[0])
                            for x, y in [(r0, c0), (r2, c2), (r3, c3)]):
                            if (board[r0][c0] == opponent and
                                board[r2][c2] == symbol and
                                board[r3][c3] == "."):
                                risk_score += score_from_table

                        # empty - AI - AI - Player
                        r0, c0 = r - 2*dr, c - 2*dc
                        r1, c1 = r - dr, c - dc
                        r2, c2 = r, c
                        r3, c3 = r + dr, c + dc

                        if all(0 <= x < len(board) and 0 <= y < len(board[0])
                            for x, y in [(r0, c0), (r1, c1), (r3, c3)]):
                            if (board[r0][c0] == "." and
                                board[r1][c1] == symbol and
                                board[r3][c3] == opponent):
                                risk_score += score_from_table
                    except IndexError:
                        continue
        return risk_score

    def get_capture_count(self, player):
        if player == "p1":
            return self.p1_piece
        else:
            return self.p2_piece
     
    def calc_placement_score(self):
        x, y = self.last_move
        center = config.GRID_SIZE // 2
        dx = abs(x - center)
        dy = abs(y - center)
        # chaque moitié (X et Y) compte pour 100 pts
        return int(((center - dx) + (center - dy)) / center * (config.codes["CENTER"] / 2))

### ADDED Capture check
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
            score_alignments = self.check_alignments(player, pToJ[player])
            score_block = self.check_blocks(player, pToJ[player])
            score_capture = self.check_last_capture(pToJ[player])
            placement_score = self.calc_placement_score()
            risk_capture = self.evaluate_capture_risk(self.board, symbol, opponent_captures=self.get_capture_count(opponent))
            
            score_total = score_alignments + score_block + score_capture + placement_score - risk_capture
            # coder le cumule du score
        return score_total

    def minimax(self, depth, maxim, current_score=0):
        if depth == 0 or self.isDone():
            return None, current_score

        best_move = None
        current_player = self.whoPlay
        opponent = "p2" if current_player == "p1" else "p1"

        possible_moves = self.getPossibleMoves()

        RED = "(p1)"   # Rouge pour joueur 1
        BLUE = "(p2)"  # Bleu pour joueur 2

        def get_colored_symbol(val):
            if val == ".":
                return " . "  # Représente un espace vide
            elif val == "1":
                return f"{RED}"  # Rouge pour joueur 1
            elif val == "2":
                return f"{BLUE}"  # Bleu pour joueur 2
            else:
                return " ? "  # Pour une valeur inconnue


        board_scores = [
            [get_colored_symbol(self.board[y][x]) for x in range(config.GRID_SIZE)]
            for y in range(config.GRID_SIZE)
        ]
        if maxim:
            best_score = float("-inf")
            for move in possible_moves:
                self.playAt(move)
                move_score = self.checkBoard(current_player)  # score du coup joué
                board_scores[move[0]][move[1]] = f"{move_score:4}"
                _, total_score = self.minimax(depth - 1, False, current_score + move_score)
                self.undoLastMove()

                if total_score > best_score:
                    best_score = total_score
                    best_move = move
            for row in board_scores:
                print(" ".join(f"{str(cell).strip():>4}" for cell in row))  # Rendre chaque cellule de 6 espaces
            print("\n")
            return best_move, best_score

        else:
            best_score = float("inf")
            for move in possible_moves:
                self.playAt(move)
                move_score = self.checkBoard(current_player)  # score du coup joué
                board_scores[move[0]][move[1]] = f"{move_score:4}"
                _, total_score = self.minimax(depth - 1, True, current_score - move_score)
                self.undoLastMove()

                if total_score < best_score:
                    best_score = total_score
                    best_move = move
            for row in board_scores:
                print(" ".join(f"{str(cell).strip():>4}" for cell in row))  # Rendre chaque cellule de 6 espaces
            print("\n")
            return best_move, best_score

    def getAImove(self):
        depth = self.getDifficulty()
        game_copy = deepcopy(self)
        game_copy.isAIgame = False
        move, _ = game_copy.minimax(depth, maxim=True)
        return move

    def startPlayer(self):
        """Détermine aléatoirement qui commence."""
        return bool(random.getrandbits(1))

    def dispInfoOn(self, surface, font):
        rect = placeButtonAtPercent(40, 35)
        pygame.draw.rect(surface, (0, 0, 0), rect, 7)

        text_lines = [
            f"Temps écoulé : {self.time.getTime()}",
            "Tour " + str(self.turn) + ".",
            "Aux " + ("noirs" if (self.whoPlay == "p1") else "blancs") + " de jouer.",
            f"Les noirs ont capturé {self.p1_piece} pions.",
            f"Les blancs ont capturé {self.p2_piece} pions.",
        ]
        draw_text_in_rect(surface, rect, text_lines, font)

    def addCapturePiece(self):
        test = self.p1_piece
        test2 = self.p2_piece
        test3 = self.whoPlay
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
                    captured_symbol = self.board[piece[0]][piece[1]]  # récupérer le symbole AVANT de vider la case

                    tmp_history.append({
                        "coords": (piece[0], piece[1]),
                        "symbol": captured_symbol,
                        "effect": "remove",
                    })

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
