"""国际象棋游戏模块

解耦设计：
- logic.py: 游戏逻辑
- ai.py: AI引擎（Minimax + Alpha-Beta）
- ui.py: GTK/Adwaita UI
"""

from .logic import ChessLogic, Player, GameState
from .ai import ChessAI
from .ui import ChessUI, GameMode


class Chess:
    """国际象棋游戏类"""

    def __init__(self, score_manager):
        self.score_manager = score_manager
        self.logic = ChessLogic()
        self.ui = ChessUI(self.logic, on_game_over=self._on_game_over)

    def get_widget(self):
        return self.ui.get_widget()

    def new_game(self):
        self.ui.reset()

    def stop(self):
        pass

    def _on_game_over(self):
        winner = self.logic.get_winner()
        if winner:
            self.score_manager.record_score("chess", self.logic.move_count)


__all__ = ['Chess', 'ChessLogic', 'ChessAI', 'Player', 'GameState', 'GameMode']
