"""三子棋游戏模块

解耦设计：
- logic.py: 游戏逻辑
- ai.py: AI引擎（Minimax）
- ui.py: GTK/Adwaita UI
"""

from .logic import TicTacToeLogic, Player, GameState
from .ai import TicTacToeAI
from .ui import TicTacToeUI, GameMode


class TicTacToe:
    """三子棋游戏类"""

    def __init__(self, score_manager):
        self.score_manager = score_manager
        self.logic = TicTacToeLogic()
        self.ui = TicTacToeUI(self.logic, on_game_over=self._on_game_over)

    def get_widget(self):
        return self.ui.get_widget()

    def new_game(self):
        self.ui.reset()

    def stop(self):
        pass

    def _on_game_over(self):
        winner = self.logic.get_winner()
        if winner:
            self.score_manager.record_score("tic_tac_toe", 1)


__all__ = ['TicTacToe', 'TicTacToeLogic', 'TicTacToeAI',
           'Player', 'GameState', 'GameMode']
