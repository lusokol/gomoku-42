import random
import pygame
import config
from copy import deepcopy
import math
from utile import placeButtonAtPercent, draw_text_in_rect

# Deep copy game

def makeMove(self, x, y, player):
    """Record move from player"""
    self.board[x][y] = player

def undoMove(self, x, y):
    """Undo the move from AI"""
    self.board[x][y] = '.'

def isDone(self):
    """Collect info if game is done or still running"""
    if self.ingame == False:
        return False

def getPossibleMoves(self):
    """Check the empty spots on the board to signal them as possible moves for the AI"""
    return [(x, y) for y in range(len(self.board)) for x in range(len(self.board[0])) if self.board[x][y] == '.']

def checkBoard(self, player):
    """Simple heuristic checker for our board to see which placement could be more beneficial"""
    opponent = "p1" if player == "p2" else "p2"
    symbol = self.getSymbolFromPlayer(player)
    opp_symbol = self.getSymbolFromPlayer(opponent)
    
    score = 0
    
    score += self.p1_piece * 50 if player == "p1" else self.p2_piece * 50
    score -= self.p2_piece * 50 if player == "p1" else self.p1_piece * 50
    
    for y in range(len(self.board)):
        for x in range(len(self.board[0])):
            if self.board[y][x] == symbol:
                align_len = self.checkAlignments(symbol, (y, x))
                if align_len:
                    score += align_len * 100 #Congrats that's a good move :)
            elif self.board[y][x] == opp_symbol:
                align_len = self.checkAlignments(opp_symbol, (y, x))
                if align_len:
                    score -= align_len * 80 #This is not a good move so we deduct score from the play
                    
    if self.pending_win and self.pending_win["player"] == player:
        score += 5000
    elif self.pending_win and self.pending_win["player"] == opponent:
        score -= 5000
    
    return score
            
def minimax(game, depth, alpha, beta, maxim):
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
    In the second case, the game is ongoing and the algo will return the score afer evaluating the state of the game.
    
    Maximizing Player's move : the algo looks for the moves that would increase the maximizing player's chances of winning.
    Minimizing Player's move : the algo looks for the moves that would decrease those chances by returning the lowest score.
    
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
        return game.checkBoard(game.whoPlay), None
    # @top_move is declared to store the highest score guarantee
    top_move = None
    # entering the Maximizing player's turn
    if maxim:
        max_check = float('-inf') #setting the max_check score to a minimum for optimal use
        for move in game.getPossibleMoves(): 
            game_copy = deepcopy(game) #deepcopy of game so we don't destroy our beautiful game
            game_copy.playAt(move) #playAt on the deepcopy 
            eval, _ = minimax(game_copy, depth - 1, alpha, beta, False)
            if eval > max_check:
                max_check = eval
                top_move = move
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_check, top_move
    else: #opposite of maxim player except when we cut to the chase by using alpha beta pruning
        min_check = float('inf')
        for move in game.getPossibleMoves():
            game_copy = deepcopy(game)
            game_copy.playAt(move)
            eval, _ = minimax(game_copy, depth - 1, alpha, beta, True)
            if eval < min_check:
                min_check = eval
                top_move = move
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_check, top_move
    
# => deepcopy to be done once only ==> getAImove not in every recursive call
# finish getAImove
# implement getAImove in process

#def getAImove(self, ):
    #return 