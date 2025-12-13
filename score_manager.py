"""分数管理器 - 使用JSON存储游戏数据"""

import json
import os
from datetime import datetime
from pathlib import Path


class ScoreManager:
    def __init__(self):
        self.log_dir = Path(__file__).parent / "log"
        self.log_dir.mkdir(exist_ok=True)
        self.scores_file = self.log_dir / "scores.json"
        self.data = self.load_data()

    def load_data(self):
        """加载数据"""
        if self.scores_file.exists():
            try:
                with open(self.scores_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return self.default_data()
        return self.default_data()

    def default_data(self):
        """默认数据结构"""
        return {
            "high_scores": {},
            "play_counts": {},
            "last_played": {},
            "game_history": []
        }

    def save_data(self):
        """保存数据"""
        try:
            with open(self.scores_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"保存数据失败: {e}")

    def record_score(self, game_id, score):
        """记录分数"""
        # 更新最高分
        current_high = self.data["high_scores"].get(game_id, 0)
        if score > current_high:
            self.data["high_scores"][game_id] = score

        # 记录历史
        self.data["game_history"].append({
            "game": game_id,
            "score": score,
            "timestamp": datetime.now().isoformat()
        })

        # 只保留最近100条记录
        if len(self.data["game_history"]) > 100:
            self.data["game_history"] = self.data["game_history"][-100:]

        self.save_data()

    def record_play(self, game_id):
        """记录游戏次数"""
        self.data["play_counts"][game_id] = self.data["play_counts"].get(game_id, 0) + 1
        self.data["last_played"][game_id] = datetime.now().isoformat()
        self.save_data()

    def get_high_score(self, game_id):
        """获取最高分"""
        return self.data["high_scores"].get(game_id, 0)

    def get_play_count(self, game_id):
        """获取游戏次数"""
        return self.data["play_counts"].get(game_id, 0)

    def get_frequent_games(self, limit=3):
        """获取常玩游戏列表（按次数排序）"""
        play_counts = self.data["play_counts"]
        if not play_counts:
            return []
        sorted_games = sorted(play_counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_games[:limit]

    def get_recent_scores(self, game_id, limit=10):
        """获取最近的分数记录"""
        history = self.data["game_history"]
        game_history = [h for h in history if h["game"] == game_id]
        return game_history[-limit:]
