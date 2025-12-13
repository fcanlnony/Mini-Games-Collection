"""三子棋AI模块"""

import random
from typing import Optional, Tuple, List
from .logic import TicTacToeLogic, Player, GameState


class TicTacToeAI:
    """三子棋AI - 使用完美Minimax（状态空间小）"""

    def __init__(self, difficulty: int = 2):
        """
        Args:
            difficulty: 难度 (1=随机, 2=普通, 3=完美)
        """
        self.difficulty = difficulty

    def get_best_move(self, game: TicTacToeLogic) -> Optional[Tuple[int, int]]:
        """获取最佳移动"""
        empty_cells = [
            (r, c) for r in range(3) for c in range(3)
            if game.get_cell(r, c) == Player.NONE
        ]

        if not empty_cells:
            return None

        # 难度1：随机
        if self.difficulty == 1:
            return random.choice(empty_cells)

        # 难度2：70%最优，30%随机
        if self.difficulty == 2 and random.random() < 0.3:
            return random.choice(empty_cells)

        # 使用Minimax找最佳移动
        is_maximizing = game.current_player == Player.X
        best_move = None
        best_score = float('-inf') if is_maximizing else float('inf')

        random.shuffle(empty_cells)

        for (row, col) in empty_cells:
            # 模拟移动
            game.board[row][col] = game.current_player
            original_player = game.current_player
            game.current_player = game.current_player.opposite()

            score = self._minimax(game, not is_maximizing)

            # 恢复
            game.board[row][col] = Player.NONE
            game.current_player = original_player

            if is_maximizing:
                if score > best_score:
                    best_score = score
                    best_move = (row, col)
            else:
                if score < best_score:
                    best_score = score
                    best_move = (row, col)

        return best_move

    def _minimax(self, game: TicTacToeLogic, is_maximizing: bool) -> int:
        """Minimax算法"""
        # 检查终局
        winner = self._check_winner(game)
        if winner == Player.X:
            return 10
        elif winner == Player.O:
            return -10
        elif self._is_full(game):
            return 0

        empty_cells = [
            (r, c) for r in range(3) for c in range(3)
            if game.get_cell(r, c) == Player.NONE
        ]

        if is_maximizing:
            max_eval = float('-inf')
            for (row, col) in empty_cells:
                game.board[row][col] = Player.X
                eval_score = self._minimax(game, False)
                game.board[row][col] = Player.NONE
                max_eval = max(max_eval, eval_score)
            return max_eval
        else:
            min_eval = float('inf')
            for (row, col) in empty_cells:
                game.board[row][col] = Player.O
                eval_score = self._minimax(game, True)
                game.board[row][col] = Player.NONE
                min_eval = min(min_eval, eval_score)
            return min_eval

    def _check_winner(self, game: TicTacToeLogic) -> Player:
        """检查获胜者"""
        lines = [
            [(0, 0), (0, 1), (0, 2)],
            [(1, 0), (1, 1), (1, 2)],
            [(2, 0), (2, 1), (2, 2)],
            [(0, 0), (1, 0), (2, 0)],
            [(0, 1), (1, 1), (2, 1)],
            [(0, 2), (1, 2), (2, 2)],
            [(0, 0), (1, 1), (2, 2)],
            [(0, 2), (1, 1), (2, 0)],
        ]

        for line in lines:
            cells = [game.board[r][c] for r, c in line]
            if cells[0] != Player.NONE and cells[0] == cells[1] == cells[2]:
                return cells[0]

        return Player.NONE

    def _is_full(self, game: TicTacToeLogic) -> bool:
        """检查棋盘是否满"""
        for r in range(3):
            for c in range(3):
                if game.board[r][c] == Player.NONE:
                    return False
        return True
