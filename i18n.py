"""国际化翻译模块"""

import json
from pathlib import Path

TRANSLATIONS = {
    "zh": {
        "app_name": "游戏集合",
        "welcome_title": "欢迎来到游戏集合",
        "welcome_desc": "选择一个游戏开始玩吧！",
        "frequent_games": "常玩游戏",
        "frequent_games_desc": "查看您经常玩的游戏",
        "all_games": "所有游戏",
        "all_games_desc": "浏览全部游戏",
        "no_frequent_games": "暂无常玩游戏",
        "no_frequent_games_desc": "玩几局游戏后，常玩游戏会出现在这里",
        "played_times": "已玩 {count} 次",
        "high_score": "最高分: {score}",
        "new_game": "新游戏",
        "score": "分数",
        "level": "等级",
        "lines": "行数",
        "time": "时间",
        "game_over": "游戏结束！",
        "you_win": "恭喜你赢了！",
        "your_score": "你的分数: {score}",
        "time_used": "用时: {time} 秒",
        "hit_mine": "你踩到地雷了！",
        "ok": "确定",
        "language": "语言",
        "about": "关于",
        "chinese": "中文",
        "english": "English",
        "author": "作者",
        "email": "邮箱",
        "license": "许可证",
        "website": "访问网站",
        "next": "下一个",

        # 游戏名称
        "game_2048": "2048",
        "game_minesweeper": "扫雷",
        "game_tetris": "俄罗斯方块",
        "game_snake": "贪吃蛇",
        "game_chess": "国际象棋",

        # 游戏提示
        "hint_2048": "使用 WASD/方向键 或滑动来移动方块",
        "hint_minesweeper": "左键揭开，右键标记地雷",
        "hint_tetris": "A/D/←/→ 移动\nW/↑ 旋转\nS/↓ 加速\n空格 直落",
        "hint_snake": "使用 WASD/方向键 控制蛇的移动",
        "hint_chess": "点击棋子选择，点击目标位置移动",

        # 扫雷
        "mines": "地雷",
        "flag": "旗帜",

        # 国际象棋
        "white_turn": "白方回合",
        "black_turn": "黑方回合",
        "white_wins": "白方获胜！",
        "black_wins": "黑方获胜！",
        "white_in_check": "白方被将军！",
        "black_in_check": "黑方被将军！",
        "checkmate": "将死！",
        "stalemate": "和棋（逼和）",

        # 中国象棋
        "game_chinese_chess": "中国象棋",
        "hint_xiangqi": "点击棋子选择，点击目标位置移动",
        "xiangqi_red_turn": "红方回合",
        "xiangqi_black_turn": "黑方回合",
        "xiangqi_red_wins": "红方获胜！",
        "xiangqi_black_wins": "黑方获胜！",
        "xiangqi_red_in_check": "红方被将军！",
        "xiangqi_black_in_check": "黑方被将军！",
        "xiangqi_checkmate": "将死！",
        "xiangqi_stalemate": "困毙（和棋）",

        # 三子棋
        "game_tic_tac_toe": "三子棋",
        "hint_ttt": "点击格子落子，三子连线获胜",
        "ttt_x_turn": "X 回合",
        "ttt_o_turn": "O 回合",
        "ttt_x_wins": "X 获胜！",
        "ttt_o_wins": "O 获胜！",
        "ttt_draw": "平局！",
        "ttt_x_wins_msg": "恭喜 X 玩家获胜！",
        "ttt_o_wins_msg": "恭喜 O 玩家获胜！",
        "ttt_draw_msg": "势均力敌，平局收场！",

        # 游戏模式
        "mode_pvp": "双人对战",
        "mode_pve": "人机对战",
        "difficulty": "难度",
        "easy": "简单",
        "medium": "中等",
        "hard": "困难",
        "ai_thinking": "AI思考中...",
        "undo": "悔棋",
        "no_undo": "无法悔棋",
    },
    "en": {
        "app_name": "Game Collection",
        "welcome_title": "Welcome to Game Collection",
        "welcome_desc": "Choose a game to start playing!",
        "frequent_games": "Frequently Played",
        "frequent_games_desc": "View your most played games",
        "all_games": "All Games",
        "all_games_desc": "Browse all games",
        "no_frequent_games": "No Frequent Games",
        "no_frequent_games_desc": "Play some games and they will appear here",
        "played_times": "Played {count} times",
        "high_score": "High Score: {score}",
        "new_game": "New Game",
        "score": "Score",
        "level": "Level",
        "lines": "Lines",
        "time": "Time",
        "game_over": "Game Over!",
        "you_win": "Congratulations! You Win!",
        "your_score": "Your Score: {score}",
        "time_used": "Time: {time} seconds",
        "hit_mine": "You hit a mine!",
        "ok": "OK",
        "language": "Language",
        "about": "About",
        "chinese": "中文",
        "english": "English",
        "author": "Author",
        "email": "Email",
        "license": "License",
        "website": "Visit Website",
        "next": "Next",

        # 游戏名称
        "game_2048": "2048",
        "game_minesweeper": "Minesweeper",
        "game_tetris": "Tetris",
        "game_snake": "Snake",
        "game_chess": "Chess",

        # 游戏提示
        "hint_2048": "Use WASD/Arrow keys or swipe to move tiles",
        "hint_minesweeper": "Left click to reveal, right click to flag",
        "hint_tetris": "A/D/←/→ Move\nW/↑ Rotate\nS/↓ Speed up\nSpace Hard drop",
        "hint_snake": "Use WASD/Arrow keys to control the snake",
        "hint_chess": "Click to select a piece, click destination to move",

        # 扫雷
        "mines": "Mines",
        "flag": "Flag",

        # 国际象棋
        "white_turn": "White's turn",
        "black_turn": "Black's turn",
        "white_wins": "White wins!",
        "black_wins": "Black wins!",
        "white_in_check": "White is in check!",
        "black_in_check": "Black is in check!",
        "checkmate": "Checkmate!",
        "stalemate": "Stalemate (Draw)",

        # 中国象棋
        "game_chinese_chess": "Chinese Chess",
        "hint_xiangqi": "Click to select a piece, click destination to move",
        "xiangqi_red_turn": "Red's turn",
        "xiangqi_black_turn": "Black's turn",
        "xiangqi_red_wins": "Red wins!",
        "xiangqi_black_wins": "Black wins!",
        "xiangqi_red_in_check": "Red is in check!",
        "xiangqi_black_in_check": "Black is in check!",
        "xiangqi_checkmate": "Checkmate!",
        "xiangqi_stalemate": "Stalemate (Draw)",

        # 三子棋
        "game_tic_tac_toe": "Tic Tac Toe",
        "hint_ttt": "Click a cell to place your mark, three in a row wins",
        "ttt_x_turn": "X's turn",
        "ttt_o_turn": "O's turn",
        "ttt_x_wins": "X wins!",
        "ttt_o_wins": "O wins!",
        "ttt_draw": "Draw!",
        "ttt_x_wins_msg": "Congratulations! X wins!",
        "ttt_o_wins_msg": "Congratulations! O wins!",
        "ttt_draw_msg": "It's a tie!",

        # 游戏模式
        "mode_pvp": "2 Players",
        "mode_pve": "vs AI",
        "difficulty": "Difficulty",
        "easy": "Easy",
        "medium": "Medium",
        "hard": "Hard",
        "ai_thinking": "AI thinking...",
        "undo": "Undo",
        "no_undo": "Cannot undo",
    }
}


class I18n:
    _instance = None
    _callbacks = []

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._lang = "zh"
            cls._instance._load_saved_lang()
        return cls._instance

    def _load_saved_lang(self):
        """加载保存的语言设置"""
        config_file = Path(__file__).parent / "log" / "config.json"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self._lang = config.get("language", "zh")
            except:
                pass

    def _save_lang(self):
        """保存语言设置"""
        config_file = Path(__file__).parent / "log" / "config.json"
        config_file.parent.mkdir(exist_ok=True)
        try:
            config = {}
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            config["language"] = self._lang
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except:
            pass

    @property
    def lang(self):
        return self._lang

    @lang.setter
    def lang(self, value):
        if value in TRANSLATIONS:
            self._lang = value
            self._save_lang()
            # 通知所有监听者
            for callback in self._callbacks:
                callback()

    def get(self, key, **kwargs):
        """获取翻译文本"""
        text = TRANSLATIONS.get(self._lang, {}).get(key, key)
        if kwargs:
            text = text.format(**kwargs)
        return text

    def add_callback(self, callback):
        """添加语言变更回调"""
        if callback not in self._callbacks:
            self._callbacks.append(callback)

    def remove_callback(self, callback):
        """移除语言变更回调"""
        if callback in self._callbacks:
            self._callbacks.remove(callback)


# 全局实例
i18n = I18n()


def _(key, **kwargs):
    """翻译快捷函数"""
    return i18n.get(key, **kwargs)
