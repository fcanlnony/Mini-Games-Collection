# Mini Games Collection / 迷你游戏集合

A collection of classic mini games built with Python and Libadwaita (GTK4).

使用 Python 和 Libadwaita (GTK4) 构建的经典迷你游戏集合。

![License](https://img.shields.io/badge/license-GPL--3.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.x-green.svg)
![GTK](https://img.shields.io/badge/GTK-4.0-orange.svg)

## Screenshots / 截图

<details>
<summary>Show screenshots / 展开截图</summary>

Coming soon...

</details>

## Games Included / 包含游戏

| Game | 游戏 | Description |
|------|------|-------------|
| 2048 | 2048 | Slide tiles to combine and reach 2048 |
| Minesweeper | 扫雷 | Classic mine-finding puzzle game |
| Tetris | 俄罗斯方块 | Stack falling blocks to clear lines |
| Snake | 贪吃蛇 | Guide the snake to eat and grow |
| Chess | 国际象棋 | Classic chess game with AI opponent (3 difficulty levels) |
| Chinese Chess | 中国象棋 | Traditional Chinese chess (Xiangqi) with AI opponent |
| Tic-Tac-Toe | 井字棋 | Simple three-in-a-row game with AI opponent |

## Features / 功能特点

- Modern GNOME/Libadwaita UI design / 现代 GNOME/Libadwaita 界面设计
- Bilingual support (English/Chinese) / 双语支持（中文/英文）
- Score tracking and history / 分数记录和历史
- Frequently played games section / 常玩游戏显示
- Keyboard and gesture controls / 键盘和手势控制
- AI opponents with multiple difficulty levels / 多难度AI对手
- Smooth piece movement animations (Chess games) / 流畅的棋子移动动画（象棋游戏）
- Undo functionality / 悔棋功能

## Requirements / 依赖要求

- Python 3.x
- GTK 4.0
- Libadwaita 1.x
- PyGObject

### Install dependencies on Fedora / 在 Fedora 上安装依赖

```bash
sudo dnf install python3 python3-gobject gtk4 libadwaita
```

### Install dependencies on Ubuntu/Debian / 在 Ubuntu/Debian 上安装依赖

```bash
sudo apt install python3 python3-gi gir1.2-gtk-4.0 gir1.2-adw-1
```

### Install dependencies on Arch Linux / 在 Arch Linux 上安装依赖

```bash
sudo pacman -S python python-gobject gtk4 libadwaita
```

## Installation & Running / 安装和运行

```bash
# Clone the repository / 克隆仓库
git clone https://github.com/fcanlnony/Mini-Games-Collection.git
cd Mini-Games-Collection

# Run the application / 运行程序
python3 main.py
```

## Controls / 操作说明

### 2048
- **WASD / Arrow keys**: Move tiles / 移动方块
- **Swipe**: Move tiles (touch) / 滑动移动方块

### Minesweeper / 扫雷
- **Left click**: Reveal cell / 揭开格子
- **Right click**: Flag mine / 标记地雷

### Tetris / 俄罗斯方块
- **A/D or ←/→**: Move left/right / 左右移动
- **W or ↑**: Rotate / 旋转
- **S or ↓**: Soft drop / 加速下落
- **Space**: Hard drop / 直接落下

### Snake / 贪吃蛇
- **WASD / Arrow keys**: Change direction / 改变方向

### Chess / 国际象棋
- **Mouse click**: Select and move pieces / 点击选择和移动棋子
- **PvP / PvE modes**: Play against friend or AI / 双人对战或人机对战
- **Undo button**: Take back moves / 悔棋按钮

### Chinese Chess / 中国象棋
- **Mouse click**: Select and move pieces / 点击选择和移动棋子
- **PvP / PvE modes**: Play against friend or AI / 双人对战或人机对战
- **Undo button**: Take back moves / 悔棋按钮

### Tic-Tac-Toe / 井字棋
- **Mouse click**: Place X or O / 点击放置X或O
- **PvP / PvE modes**: Play against friend or AI / 双人对战或人机对战

## Project Structure / 项目结构

```
Mini-Games-Collection/
├── main.py              # Main application / 主程序
├── score_manager.py     # Score management / 分数管理
├── i18n.py             # Internationalization / 国际化
├── CLAUDE.md           # AI assistant guidance / AI助手指导文档
├── games/              # Game modules / 游戏模块
│   ├── game_2048.py    # 2048 game
│   ├── minesweeper.py  # Minesweeper
│   ├── tetris.py       # Tetris
│   ├── snake.py        # Snake
│   ├── chess/          # Chess (modular) / 国际象棋（模块化）
│   │   ├── __init__.py
│   │   ├── logic.py    # Game logic / 游戏逻辑
│   │   ├── ai.py       # AI engine (Minimax + Alpha-Beta) / AI引擎
│   │   └── ui.py       # GTK UI with animations / GTK界面带动画
│   ├── chinese_chess/  # Chinese Chess (modular) / 中国象棋（模块化）
│   │   ├── __init__.py
│   │   ├── logic.py
│   │   ├── ai.py
│   │   └── ui.py
│   └── tic_tac_toe/    # Tic-Tac-Toe / 井字棋
│       ├── __init__.py
│       ├── logic.py
│       ├── ai.py
│       └── ui.py
├── log/                # Score data storage / 分数数据存储
└── LICENSE             # GPL-3.0 License
```

## License / 许可证

This project is licensed under the GPL-3.0 License - see the [LICENSE](LICENSE) file for details.

本项目采用 GPL-3.0 许可证 - 详见 [LICENSE](LICENSE) 文件。

## Author / 作者

**Shus Mo** - [fcanlnony@outlook.com](mailto:fcanlnony@outlook.com)

## Contributing / 贡献

Contributions, issues and feature requests are welcome!

欢迎提交贡献、问题和功能请求！

1. Fork the project / 复刻项目
2. Create your feature branch / 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. Commit your changes / 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch / 推送到分支 (`git push origin feature/AmazingFeature`)
5. Open a Pull Request / 提交拉取请求
