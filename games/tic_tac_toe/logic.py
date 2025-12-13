"""三子棋游戏逻辑模块"""

from enum import Enum
from typing import Optional, List, Tuple


class Player(Enum):
    """玩家枚举"""
    NONE = 0
    X = 1
    O = 2

    def opposite(self) -> 'Player':
        """获取对手"""
        if self == Player.X:
            return Player.O
        elif self == Player.O:
            return Player.X
        return Player.NONE


class GameState(Enum):
    """游戏状态枚举"""
    PLAYING = 0
    X_WINS = 1
    O_WINS = 2
    DRAW = 3


class TicTacToeLogic:
    """三子棋游戏逻辑类"""

    # 获胜的所有可能组合
    WIN_COMBINATIONS = [
        # 横向
        [(0, 0), (0, 1), (0, 2)],
        [(1, 0), (1, 1), (1, 2)],
        [(2, 0), (2, 1), (2, 2)],
        # 纵向
        [(0, 0), (1, 0), (2, 0)],
        [(0, 1), (1, 1), (2, 1)],
        [(0, 2), (1, 2), (2, 2)],
        # 对角线
        [(0, 0), (1, 1), (2, 2)],
        [(0, 2), (1, 1), (2, 0)],
    ]

    def __init__(self):
        self.reset()

    def reset(self):
        """重置游戏"""
        self.board: List[List[Player]] = [
            [Player.NONE for _ in range(3)] for _ in range(3)
        ]
        self.current_player = Player.X
        self.state = GameState.PLAYING
        self.winning_line: Optional[List[Tuple[int, int]]] = None
        self.move_history: List[Tuple[int, int]] = []  # 移动历史记录

    def get_cell(self, row: int, col: int) -> Player:
        """获取格子状态"""
        return self.board[row][col]

    def is_valid_move(self, row: int, col: int) -> bool:
        """检查移动是否有效"""
        if self.state != GameState.PLAYING:
            return False
        if row < 0 or row > 2 or col < 0 or col > 2:
            return False
        return self.board[row][col] == Player.NONE

    def make_move(self, row: int, col: int) -> bool:
        """下棋

        Args:
            row: 行索引 (0-2)
            col: 列索引 (0-2)

        Returns:
            是否成功下棋
        """
        if not self.is_valid_move(row, col):
            return False

        self.board[row][col] = self.current_player
        self.move_history.append((row, col))
        self._check_game_state()

        if self.state == GameState.PLAYING:
            self.current_player = self.current_player.opposite()

        return True

    def undo(self) -> bool:
        """悔棋，返回是否成功"""
        if not self.move_history:
            return False

        row, col = self.move_history.pop()
        self.board[row][col] = Player.NONE

        # 恢复状态
        self.state = GameState.PLAYING
        self.winning_line = None

        # 如果游戏还在进行中，切换回上一个玩家
        self.current_player = self.current_player.opposite()

        return True

    def can_undo(self) -> bool:
        """是否可以悔棋"""
        return len(self.move_history) > 0

    def _check_game_state(self):
        """检查游戏状态"""
        # 检查是否有玩家获胜
        for combo in self.WIN_COMBINATIONS:
            cells = [self.board[r][c] for r, c in combo]
            if cells[0] != Player.NONE and cells[0] == cells[1] == cells[2]:
                self.winning_line = combo
                if cells[0] == Player.X:
                    self.state = GameState.X_WINS
                else:
                    self.state = GameState.O_WINS
                return

        # 检查是否平局
        is_full = all(
            self.board[r][c] != Player.NONE
            for r in range(3) for c in range(3)
        )
        if is_full:
            self.state = GameState.DRAW

    def is_game_over(self) -> bool:
        """游戏是否结束"""
        return self.state != GameState.PLAYING

    def get_winner(self) -> Optional[Player]:
        """获取获胜者"""
        if self.state == GameState.X_WINS:
            return Player.X
        elif self.state == GameState.O_WINS:
            return Player.O
        return None
