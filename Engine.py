import pygame as game

game.init()
sound_castle = game.mixer.Sound('sounds/castle.wav')
sound_capture = game.mixer.Sound('sounds/capture.wav')
class GameState():
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.moving = {'p' : self.pawn_move, 'R' : self.rook_move,
                  'N' : self.knight_move, 'B' : self.bishop_move,
                  'K' : self.king_move, 'Q' : self.queen_move}

        self.white_move = True
        self.checkmate = False
        self.stalemate = False
        self.sound = True
        self.wking_location = (7, 4)
        self.bking_location = (0, 4)
        self.move_log = []
        self.enpassant_possible = ()
        self.current_castling = Castle_Rights(True, True, True, True)
        self.castling_log = [Castle_Rights(self.current_castling.wks, self.current_castling.bks,
                             self.current_castling.wqs, self.current_castling.bqs)]
    def make_move(self, move):
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.figure_moved
        self.move_log.append(move)
        self.white_move = not self.white_move
        if move.figure_moved == 'wK':
            self.wking_location = (move.end_row, move.end_col)
        elif move.figure_moved == 'bK':
            self.bking_location = (move.end_row, move.end_col)

        if move.pawn_promotion:
            self.board[move.end_row][move.end_col] = move.figure_moved[0] + 'Q'
        if move.enpassant:
            self.board[move.start_row][move.end_col] = '--'
        if move.figure_moved[1] == 'p' and abs(move.start_row - move.end_row) == 2:
            self.enpassant_possible = ((move.start_row + move.end_row) // 2, move.start_col)
        else:
            self.enpassant_possible = ()

        if move.castle_move:
            if move.end_col - move.start_col == 2:
                self.board[move.end_row][move.end_col - 1] = self.board[move.end_row][move.end_col + 1]
                self.board[move.end_row][move.end_col + 1] = '--'
            else:
                self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 2]
                self.board[move.end_row][move.end_col - 2] = '--'

        self.update_castling_rights(move)
        self.castling_log.append(Castle_Rights(self.current_castling.wks, self.current_castling.bks,
                                           self.current_castling.wqs, self.current_castling.bqs))

    def cancel_move(self):
        if len(self.move_log) != 0:
            move = self.move_log.pop()
            self.board[move.start_row][move.start_col] = move.figure_moved
            self.board[move.end_row][move.end_col] = move.figure_captured
            self.white_move = not self.white_move
            if move.figure_moved == 'wK':
                self.wking_location = (move.start_row, move.start_col)
            elif move.figure_moved == 'bK':
                self.bking_location = (move.start_row, move.start_col)
            if move.enpassant:
                self.board[move.end_row][move.end_col] = '--'
                self.board[move.start_row][move.end_col] = move.figure_captured
                self.enpassant_possible = (move.end_row, move.end_col)
            if move.figure_moved[1] == 'p' and abs(move.start_row - move.end_row) == 2:
                self.enpassant_possible = ()

            self.castling_log.pop()
            new_castling = self.castling_log[-1]
            self.current_castling = Castle_Rights(new_castling.wks, new_castling.bks,
                                           new_castling.wqs, new_castling.bqs)
            if move.castle_move:
                if move.end_col - move.start_col == 2:
                    self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 1]
                    self.board[move.end_row][move.end_col - 1] = '--'
                else:
                    self.board[move.end_row][move.end_col - 2] = self.board[move.end_row][move.end_col + 1]
                    self.board[move.end_row][move.end_col + 1] = '--'

    def update_castling_rights(self, move):
        if move.figure_moved == 'wK':
            self.current_castling.wks = False
            self.current_castling.wqs = False
        elif move.figure_moved == 'bK':
            self.current_castling.bks = False
            self.current_castling.bqs = False
        elif move.figure_moved == 'wR':
            if move.start_row == 7:
                if move.start_col == 0:
                    self.current_castling.wqs = False
                elif move.start_col == 7:
                    self.current_castling.wks = False
        elif move.figure_moved == 'bR':
            if move.start_row == 0:
                if move.start_col == 0:
                    self.current_castling.bqs = False
                elif move.start_col == 7:
                    self.current_castling.bks = False

    def validation_move(self):
        temp_enpassant = self.enpassant_possible
        temp_castle = Castle_Rights(self.current_castling.wks, self.current_castling.bks,
                             self.current_castling.wqs, self.current_castling.bqs)
        moves = self.possible_moves()
        if self.white_move:
            self.castle_move(self.wking_location[0], self.wking_location[1], moves)
        else:
            self.castle_move(self.bking_location[0], self.bking_location[1], moves)
        for i in range(len(moves) - 1, -1, -1):
            self.make_move(moves[i])
            self.white_move = not self.white_move
            if self.check():
                moves.remove(moves[i])
            self.white_move = not self.white_move
            self.cancel_move()
        if len(moves) == 0:
            if self.check():
                self.checkmate = True
            else:
                self.stalemate = True
        self.enpassant_possible = temp_enpassant
        self.current_castling = temp_castle
        return moves

    def under_attack(self, row, col):
        self.white_move = not self.white_move
        opp_moves = self.possible_moves() #opponents move
        self.white_move = not self.white_move

        for move in opp_moves:
            if move.end_row == row and move.end_col == col:
                return True
        return False

    def check(self):
        if self.white_move:
            return self.under_attack(self.wking_location[0], self.wking_location[1])
        else:
            return self.under_attack(self.bking_location[0], self.bking_location[1])

    def possible_moves(self):
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                turn = self.board[row][col][0]
                if (turn == 'w' and self.white_move) or (turn == 'b' and not self.white_move):
                    figure = self.board[row][col][1]
                    self.moving[figure](row, col, moves)
        return moves

    def basic_move(self, directions, length, row, col, moves):
        enemy_color = 'b' if self.white_move else 'w'
        for d in directions:
            for i in range(1, length):
                end_row = row + d[0] * i
                end_col = col + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_sq = self.board[end_row][end_col]
                    if end_sq == "--":
                        moves.append(Move((row, col), (end_row, end_col), self.board))
                    elif end_sq[0] == enemy_color:
                        moves.append(Move((row, col), (end_row, end_col), self.board))
                        break
                    else:
                        break
                else:
                    break
    def pawn_move(self, row, col, moves):
        if self.white_move:
            if self.board[row - 1][col] == "--":
                moves.append(Move((row, col), (row - 1, col), self.board))
                if row == 6 and self.board[row - 2][col] == "--":
                    moves.append(Move((row, col), (row - 2, col), self.board))
            if col - 1 >= 0:
                if self.board[row - 1][col - 1][0] == 'b':
                    moves.append(Move((row, col), (row - 1, col - 1), self.board))
                elif (row - 1, col - 1) == self.enpassant_possible:
                    moves.append(Move((row, col), (row - 1, col - 1), self.board, enpassant = True))
            if col + 1 <= 7:
                if self.board[row - 1][col + 1][0] == 'b':
                    moves.append(Move((row, col), (row - 1, col + 1), self.board))
                elif (row - 1, col + 1) == self.enpassant_possible:
                    moves.append(Move((row, col), (row - 1, col + 1), self.board, enpassant = True))
        else:
            if self.board[row + 1][col] == "--":
                moves.append(Move((row, col), (row + 1, col), self.board))
                if row == 1 and self.board[row + 2][col] == "--":
                    moves.append(Move((row, col), (row + 2, col), self.board))
            if col - 1 >= 0:
                if self.board[row + 1][col - 1][0] == 'w':
                    moves.append(Move((row, col), (row + 1, col - 1), self.board))
                elif (row + 1, col - 1) == self.enpassant_possible:
                    moves.append(Move((row, col), (row + 1, col - 1), self.board, enpassant = True))
            if col + 1 <= 7:
                if self.board[row + 1][col + 1][0] == 'w':
                    moves.append(Move((row, col), (row + 1, col + 1), self.board))
                elif (row + 1, col + 1) == self.enpassant_possible:
                    moves.append(Move((row, col), (row + 1, col + 1), self.board, enpassant = True))

    def rook_move(self, row, col, moves):
        self.basic_move(((-1, 0), (0, -1), (1, 0), (0, 1)), 8, row, col, moves)

    def knight_move(self, row, col, moves):
        directions = ((1, 2), (1, -2), (-1, 2), (-1, -2), (2, 1), (2, -1), (-2, 1), (-2, -1))
        enemy_color = 'b' if self.white_move else 'w'
        for d in directions:
            end_row = row + d[0]
            end_col = col + d[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_sq = self.board[end_row][end_col]
                if end_sq[0] == enemy_color or end_sq == "--":
                    moves.append(Move((row, col), (end_row, end_col), self.board))

    def bishop_move(self, row, col, moves):
        self.basic_move(((-1, -1), (1, -1), (-1, 1), (1, 1)), 8, row, col, moves)

    def king_move(self, row, col, moves):
        directions = ((-1, -1), (1, -1), (-1, 1), (1, 1), (-1, 0), (0, -1), (1, 0), (0, 1))
        ally_color = 'w' if self.white_move else 'b'
        for i in range(8):
            end_row = row + directions[i][0]
            end_col = col + directions[i][1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                figure = self.board[end_row][end_col]
                if figure[0] != ally_color:
                    moves.append(Move((row, col), (end_row, end_col), self.board))

    def queen_move(self, row, col, moves):
        self.rook_move(row, col, moves)
        self.bishop_move(row, col, moves)

    def castle_move(self, row, col, moves):
        if self.under_attack(row, col):
            return
        if (self.white_move and self.current_castling.wks) or (not self.white_move and self.current_castling.bks):
            self.king_side_castle(row, col, moves)
        if (self.white_move and self.current_castling.wqs) or (not self.white_move and self.current_castling.bqs):
            self.queen_side_castle(row, col, moves)


    def king_side_castle(self, row, col, moves):
        if self.board[row][col+1] == '--' and self.board[row][col+2] == '--':
            if not self.under_attack(row, col+1) and not self.under_attack(row, col+2):
                moves.append(Move((row, col), (row, col+2), self.board, castle_move = True))

    def queen_side_castle(self, row, col, moves):
        if self.board[row][col-1] == '--' and self.board[row][col-2] == '--' and self.board[row][col-3] == '--':
            if not self.under_attack(row, col-1) and not self.under_attack(row, col-2) and not self.under_attack(row, col-3):
                moves.append(Move((row, col), (row, col-2), self.board, castle_move = True))

class Castle_Rights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs
class Move():
    ranks_rows = {"1" : 7, "2" : 6, "3" : 5, "4" :4,
                  "5" : 3, "6" : 2, "7" : 1, "8" : 0}
    ranks_cols = {"a" : 0, "b" : 1, "c" : 2, "d" : 3,
                  "e" : 4, "f" : 5, "g" : 6, "h" : 7}
    rows_to_ranks = {v: key for key, v in ranks_rows.items()}
    cols_to_ranks = {v: key for key, v in ranks_cols.items()}

    def __init__(self, start_square, end_square, board, enpassant = False, castle_move = False):
        self.start_row = start_square[0]
        self.start_col = start_square[1]
        self.end_row = end_square[0]
        self.end_col = end_square[1]
        self.figure_moved = board[self.start_row][self.start_col]
        self.figure_captured = board[self.end_row][self.end_col]
        self.move_id = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col
        self.pawn_promotion = (self.figure_moved == 'wp' and self.end_row == 0) or (self.figure_moved == 'bp' and self.end_row == 7)
        self.castle_move = castle_move
        self.enpassant = enpassant
        if enpassant:
            self.figure_captured = 'wp' if self.figure_moved == 'bp' else 'bp'

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_id == other.move_id
        return False
    def get_notation(self):
        return self.get_rank(self.start_row, self.start_col) + self.get_rank(self.end_row, self.end_col)
    def get_rank(self, row, col):
        return self.cols_to_ranks[col] + self.rows_to_ranks[row]

class Checkers(GameState):
    def __init__(self):
        self.board = [
            ["--", "bc", "--", "bc", "--", "bc", "--", "bc"],
            ["bc", "--", "bc", "--", "bc", "--", "bc", "--"],
            ["--", "bc", "--", "bc", "--", "bc", "--", "bc"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wc", "--", "wc", "--", "wc", "--", "wc", "--"],
            ["--", "wc", "--", "wc", "--", "wc", "--", "wc"],
            ["wc", "--", "wc", "--", "wc", "--", "wc", "--"]
        ]
        self.game_over = False
        self.white_move = True
        self.move_log = []

    def make_move(self, move):
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.figure_moved
        self.move_log.append(move)
        self.white_move = not self.white_move

    def validation_move(self):
        moves = self.possible_moves()
        for i in range(len(moves) - 1, -1, -1):
            self.make_move(moves[i])
            self.cancel_move()
        if len(moves) == 0:
            self.game_over = True
        return moves

    def possible_moves(self):
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                turn = self.board[row][col][0]
                if (turn == 'w' and self.white_move) or (turn == 'b' and not self.white_move):
                    figure = self.board[row][col][1]
                    self.moving[figure](row, col, moves)
        return moves
