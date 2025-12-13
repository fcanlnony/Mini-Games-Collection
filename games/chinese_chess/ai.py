"""中国象棋AI模块"""

import random
import threading
from typing import Optional, Tuple, List
from .logic import ChineseChessLogic, Player, GameState, BOARD_ROWS, BOARD_COLS


class ChineseChessAI:
    """中国象棋AI - Minimax + Alpha-Beta"""

    def __init__(self, difficulty: int = 2):
        self.difficulty = difficulty
        # 降低搜索深度，中国象棋分支因子大
        self._depth_map = {1: 1, 2: 2, 3: 3}

    @property
    def search_depth(self) -> int:
        return self._depth_map.get(self.difficulty, 2)

    def get_best_move(self, game: ChineseChessLogic) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """获取最佳移动"""
        moves = self._get_all_moves_fast(game)
        if not moves:
            return None

        # 难度1：随机选择
        if self.difficulty == 1:
            return random.choice(moves)

        is_maximizing = game.current_player == Player.RED
        best_move = None
        best_score = float('-inf') if is_maximizing else float('inf')

        # 移动排序：优先考虑吃子移动
        moves = self._order_moves(game, moves)

        for (from_pos, to_pos) in moves:
            # 快速执行移动（不验证）
            captured = self._make_move_fast(game, from_pos, to_pos)

            score = self._minimax(
                game,
                self.search_depth - 1,
                float('-inf'),
                float('inf'),
                not is_maximizing
            )

            # 撤销移动
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

    def _minimax(self, game: ChineseChessLogic, depth: int, alpha: float,
                 beta: float, is_maximizing: bool) -> int:
        """Minimax + Alpha-Beta"""
        if depth == 0:
            return self._evaluate_fast(game)

        moves = self._get_all_moves_fast(game)
        if not moves:
            # 无合法移动，检查是否被将死
            if game.is_in_check(game.current_player):
                return -100000 if is_maximizing else 100000
            return 0  # 和棋

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

    def _get_all_moves_fast(self, game: ChineseChessLogic) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """快速获取所有合法移动"""
        moves = []
        player = game.current_player
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                piece = game.board[row][col]
                if piece and piece.color == player:
                    for move in game.get_valid_moves(row, col):
                        moves.append(((row, col), move))
        return moves

    def _order_moves(self, game: ChineseChessLogic,
                     moves: List[Tuple[Tuple[int, int], Tuple[int, int]]]) -> List:
        """移动排序（吃子优先）"""
        def score_move(move):
            to_pos = move[1]
            target = game.board[to_pos[0]][to_pos[1]]
            if target:
                return target.value
            return 0

        return sorted(moves, key=score_move, reverse=True)

    def _make_move_fast(self, game: ChineseChessLogic,
                        from_pos: Tuple[int, int],
                        to_pos: Tuple[int, int]):
        """快速执行移动（不验证，返回被吃棋子）"""
        piece = game.board[from_pos[0]][from_pos[1]]
        captured = game.board[to_pos[0]][to_pos[1]]

        game.board[to_pos[0]][to_pos[1]] = piece
        game.board[from_pos[0]][from_pos[1]] = None
        game.current_player = game.current_player.opposite()

        return captured

    def _undo_move_fast(self, game: ChineseChessLogic,
                        from_pos: Tuple[int, int],
                        to_pos: Tuple[int, int],
                        captured):
        """撤销移动"""
        piece = game.board[to_pos[0]][to_pos[1]]
        game.board[from_pos[0]][from_pos[1]] = piece
        game.board[to_pos[0]][to_pos[1]] = captured
        game.current_player = game.current_player.opposite()

    def _evaluate_fast(self, game: ChineseChessLogic) -> int:
        """快速评估局面"""
        score = 0
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                piece = game.board[row][col]
                if piece:
                    value = piece.value
                    # 过河兵加分
                    if piece.piece_type.value == 'soldier':
                        if piece.color == Player.RED and row < 5:
                            value += 20
                        elif piece.color == Player.BLACK and row > 4:
                            value += 20

                    if piece.color == Player.RED:
                        score += value
                    else:
                        score -= value

        return score
