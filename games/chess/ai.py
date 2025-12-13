"""国际象棋AI模块"""

import random
from typing import Optional, Tuple, List
from .logic import ChessLogic, Player, GameState


class ChessAI:
    """国际象棋AI - Minimax + Alpha-Beta"""

    def __init__(self, difficulty: int = 2):
        self.difficulty = difficulty
        self._depth_map = {1: 1, 2: 2, 3: 3}

    @property
    def search_depth(self) -> int:
        return self._depth_map.get(self.difficulty, 2)

    def get_best_move(self, game: ChessLogic) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """获取最佳移动"""
        moves = game.get_all_moves()
        if not moves:
            return None

        # 难度1：随机
        if self.difficulty == 1:
            return random.choice(moves)

        is_maximizing = game.current_player == Player.WHITE
        best_move = None
        best_score = float('-inf') if is_maximizing else float('inf')

        # 移动排序
        moves = self._order_moves(game, moves)

        for (from_pos, to_pos) in moves:
            captured = self._make_move_fast(game, from_pos, to_pos)

            score = self._minimax(
                game,
                self.search_depth - 1,
                float('-inf'),
                float('inf'),
                not is_maximizing
            )

            self._undo_move_fast(game, from_pos, to_pos, captured)

            if is_maximizing:
                if score > best_score:
                    best_score = score
                    best_move = (from_pos, to_pos)
            else:
                if score < best_score:
                    best_score = score
                    best_move = (from_pos, to_pos)

        return best_move

    def _minimax(self, game: ChessLogic, depth: int, alpha: float,
                 beta: float, is_maximizing: bool) -> int:
        """Minimax + Alpha-Beta"""
        if depth == 0:
            return game.evaluate()

        moves = game.get_all_moves()
        if not moves:
            if game.is_in_check(game.current_player):
                return -100000 if is_maximizing else 100000
            return 0

        if is_maximizing:
            max_eval = float('-inf')
            for (from_pos, to_pos) in moves:
                captured = self._make_move_fast(game, from_pos, to_pos)
                eval_score = self._minimax(game, depth - 1, alpha, beta, False)
                self._undo_move_fast(game, from_pos, to_pos, captured)

                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for (from_pos, to_pos) in moves:
                captured = self._make_move_fast(game, from_pos, to_pos)
                eval_score = self._minimax(game, depth - 1, alpha, beta, True)
                self._undo_move_fast(game, from_pos, to_pos, captured)

                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval

    def _order_moves(self, game: ChessLogic, moves: List) -> List:
        """移动排序"""
        def score_move(move):
            to_pos = move[1]
            target = game.board[to_pos[0]][to_pos[1]]
            if target:
                return game.PIECE_VALUES.get(target, 0)
            return 0
        return sorted(moves, key=score_move, reverse=True)

    def _make_move_fast(self, game: ChessLogic, from_pos, to_pos):
        """快速移动"""
        piece = game.board[from_pos[0]][from_pos[1]]
        captured = game.board[to_pos[0]][to_pos[1]]
        game.board[to_pos[0]][to_pos[1]] = piece
        game.board[from_pos[0]][from_pos[1]] = None
        game.current_player = game.current_player.opposite()
        return captured

    def _undo_move_fast(self, game: ChessLogic, from_pos, to_pos, captured):
        """撤销移动"""
        piece = game.board[to_pos[0]][to_pos[1]]
        game.board[from_pos[0]][from_pos[1]] = piece
        game.board[to_pos[0]][to_pos[1]] = captured
        game.current_player = game.current_player.opposite()
