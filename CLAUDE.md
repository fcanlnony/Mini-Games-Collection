# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个使用 Python 和 libadwaita (GTK4) 开发的游戏集合应用，包含：
- 2048
- 扫雷
- 俄罗斯方块
- 贪吃蛇

## 运行命令

```bash
python3 main.py
```

## 项目结构

- `main.py` - 主应用程序，包含导航和游戏页面管理
- `score_manager.py` - 分数和游戏数据管理（JSON存储在 `log/scores.json`）
- `games/` - 各游戏实现
  - `game_2048.py` - 2048游戏
  - `minesweeper.py` - 扫雷
  - `tetris.py` - 俄罗斯方块
  - `snake.py` - 贪吃蛇

## 架构说明

### 应用框架
- 使用 `Adw.Application` 作为主应用
- 使用 `Adw.NavigationView` 实现页面导航
- 每个游戏是独立的类，提供 `get_widget()` 返回游戏UI，`new_game()` 重置游戏，`stop()` 停止游戏

### 游戏基类模式
所有游戏类遵循相同接口：
- `__init__(score_manager)` - 接收分数管理器
- `get_widget()` - 返回 GTK Widget
- `new_game()` - 开始新游戏
- `stop()` - 停止游戏（清理定时器等）

### 分数系统
- `ScoreManager` 负责所有数据持久化
- 记录最高分、游戏次数、最近游玩时间
- 欢迎页面根据 `play_counts` 显示常玩游戏

## 依赖

- Python 3
- GTK4
- libadwaita
