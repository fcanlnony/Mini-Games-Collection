"""中国象棋游戏模块

解耦设计：
- logic.py: 游戏逻辑
- ai.py: AI引擎
- ui.py: GTK/Adwaita UI
"""

from .logic import ChineseChessLogic, Player, PieceType, GameState, Piece
from .ai import ChineseChessAI
from .ui import ChineseChessUI, GameMode


class ChineseChess:
    """中国象棋游戏类"""

    def __init__(self, score_manager):
        self.score_manager = score_manager
        self.logic = ChineseChessLogic()
        self.ui = ChineseChessUI(self.logic, on_game_over=self._on_game_over)

    def get_widget(self):
        return self.ui.get_widget()

    def new_game(self):
        self.ui.reset()

    def stop(self):
        pass

    def _on_game_over(self):
        winner = self.logic.get_winner()
        if winner:
            self.score_manager.record_score("chinese_chess", self.logic.move_count)


__all__ = ['ChineseChess', 'ChineseChessLogic', 'ChineseChessAI',
           'Player', 'PieceType', 'GameState', 'Piece', 'GameMode']
