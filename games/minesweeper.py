"""扫雷游戏"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Gdk, GLib, Adw
import random
import time
import sys
sys.path.insert(0, str(__file__).rsplit('/', 2)[0])
from i18n import _


class Minesweeper:
    def __init__(self, score_manager):
        self.score_manager = score_manager
        self.rows = 9
        self.cols = 9
        self.mines = 10

        self.board = []
        self.revealed = []
        self.flagged = []
        self.game_over = False
        self.game_won = False
        self.first_click = True
        self.start_time = None

        self.widget = self.create_widget()
        self.new_game()

    def create_widget(self):
        """创建游戏界面"""
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        main_box.set_margin_top(16)
        main_box.set_margin_bottom(16)
        main_box.set_margin_start(16)
        main_box.set_margin_end(16)
        main_box.set_halign(Gtk.Align.CENTER)
        main_box.set_valign(Gtk.Align.CENTER)

        # 信息栏
        info_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=24)
        info_box.set_halign(Gtk.Align.CENTER)
        main_box.append(info_box)

        # 剩余地雷数
        self.mines_label = Gtk.Label(label=f"💣 {self.mines}")
        self.mines_label.add_css_class("title-3")
        info_box.append(self.mines_label)

        # 计时器
        self.time_label = Gtk.Label(label="⏱ 0")
        self.time_label.add_css_class("title-3")
        info_box.append(self.time_label)

        # 游戏网格
        grid_frame = Gtk.Frame()
        grid_frame.add_css_class("card")
        main_box.append(grid_frame)

        self.grid_widget = Gtk.Grid()
        self.grid_widget.set_row_spacing(2)
        self.grid_widget.set_column_spacing(2)
        self.grid_widget.set_margin_top(8)
        self.grid_widget.set_margin_bottom(8)
        self.grid_widget.set_margin_start(8)
        self.grid_widget.set_margin_end(8)
        grid_frame.set_child(self.grid_widget)

        # 创建按钮
        self.buttons = []
        for i in range(self.rows):
            row = []
            for j in range(self.cols):
                btn = Gtk.Button(label="")
                btn.set_size_request(36, 36)
                btn.add_css_class("flat")

                # 左键点击
                click_gesture = Gtk.GestureClick()
                click_gesture.set_button(1)
                click_gesture.connect("pressed", self.on_cell_clicked, i, j)
                btn.add_controller(click_gesture)

                # 右键点击（标记）
                right_click = Gtk.GestureClick()
                right_click.set_button(3)
                right_click.connect("pressed", self.on_cell_right_clicked, i, j)
                btn.add_controller(right_click)

                self.grid_widget.attach(btn, j, i, 1, 1)
                row.append(btn)
            self.buttons.append(row)

        # 提示
        hint_label = Gtk.Label(label=_("hint_minesweeper"))
        hint_label.add_css_class("dim-label")
        main_box.append(hint_label)

        return main_box

    def get_widget(self):
        return self.widget

    def new_game(self):
        """开始新游戏"""
        self.board = [[0] * self.cols for _ in range(self.rows)]
        self.revealed = [[False] * self.cols for _ in range(self.rows)]
        self.flagged = [[False] * self.cols for _ in range(self.rows)]
        self.game_over = False
        self.game_won = False
        self.first_click = True
        self.start_time = None

        self.mines_label.set_label(f"💣 {self.mines}")
        self.time_label.set_label("⏱ 0")

        # 重置按钮
        for i in range(self.rows):
            for j in range(self.cols):
                btn = self.buttons[i][j]
                btn.set_label("")
                btn.set_sensitive(True)
                btn.remove_css_class("revealed")
                btn.remove_css_class("mine")
                btn.remove_css_class("flagged")

    def place_mines(self, exclude_row, exclude_col):
        """放置地雷（排除第一次点击的位置）"""
        positions = []
        for i in range(self.rows):
            for j in range(self.cols):
                # 排除点击位置及其周围
                if abs(i - exclude_row) <= 1 and abs(j - exclude_col) <= 1:
                    continue
                positions.append((i, j))

        mine_positions = random.sample(positions, min(self.mines, len(positions)))

        for i, j in mine_positions:
            self.board[i][j] = -1  # -1 表示地雷

        # 计算数字
        for i in range(self.rows):
            for j in range(self.cols):
                if self.board[i][j] == -1:
                    continue
                count = 0
                for di in [-1, 0, 1]:
                    for dj in [-1, 0, 1]:
                        ni, nj = i + di, j + dj
                        if 0 <= ni < self.rows and 0 <= nj < self.cols:
                            if self.board[ni][nj] == -1:
                                count += 1
                self.board[i][j] = count

    def on_cell_clicked(self, gesture, n_press, x, y, row, col):
        """处理单元格点击"""
        if self.game_over or self.game_won:
            return

        if self.flagged[row][col]:
            return

        if self.first_click:
            self.first_click = False
            self.place_mines(row, col)
            self.start_time = time.time()
            self.start_timer()

        self.reveal_cell(row, col)
        self.check_win()

    def on_cell_right_clicked(self, gesture, n_press, x, y, row, col):
        """处理右键点击（标记）"""
        if self.game_over or self.game_won:
            return

        if self.revealed[row][col]:
            return

        self.flagged[row][col] = not self.flagged[row][col]
        btn = self.buttons[row][col]

        if self.flagged[row][col]:
            btn.set_label("🚩")
            btn.add_css_class("flagged")
        else:
            btn.set_label("")
            btn.remove_css_class("flagged")

        # 更新地雷计数
        flag_count = sum(sum(row) for row in self.flagged)
        self.mines_label.set_label(f"💣 {self.mines - flag_count}")

    def reveal_cell(self, row, col):
        """揭开单元格"""
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            return
        if self.revealed[row][col] or self.flagged[row][col]:
            return

        self.revealed[row][col] = True
        btn = self.buttons[row][col]
        btn.add_css_class("revealed")

        value = self.board[row][col]

        if value == -1:
            # 踩到地雷
            btn.set_label("💥")
            btn.add_css_class("mine")
            self.game_over = True
            self.reveal_all_mines()
            self.show_game_over(False)
            return

        if value == 0:
            btn.set_label("")
            # 递归揭开周围的格子
            for di in [-1, 0, 1]:
                for dj in [-1, 0, 1]:
                    if di == 0 and dj == 0:
                        continue
                    self.reveal_cell(row + di, col + dj)
        else:
            btn.set_label(str(value))
            # 根据数字设置颜色
            colors = {
                1: "blue", 2: "green", 3: "red",
                4: "purple", 5: "brown", 6: "cyan",
                7: "black", 8: "gray"
            }
            if value in colors:
                css = f"label {{ color: {colors[value]}; font-weight: bold; }}"
                provider = Gtk.CssProvider()
                provider.load_from_string(css)
                btn.get_style_context().add_provider(
                    provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
                )

    def reveal_all_mines(self):
        """揭示所有地雷"""
        for i in range(self.rows):
            for j in range(self.cols):
                if self.board[i][j] == -1:
                    btn = self.buttons[i][j]
                    if not self.flagged[i][j]:
                        btn.set_label("💣")
                    btn.add_css_class("mine")
                    btn.set_sensitive(False)

    def check_win(self):
        """检查是否获胜"""
        for i in range(self.rows):
            for j in range(self.cols):
                if self.board[i][j] != -1 and not self.revealed[i][j]:
                    return

        self.game_won = True
        elapsed = int(time.time() - self.start_time) if self.start_time else 0
        self.score_manager.record_score("minesweeper", max(0, 999 - elapsed))
        self.show_game_over(True)

    def show_game_over(self, won):
        """显示游戏结束对话框"""
        if won:
            title = _("you_win")
            elapsed = int(time.time() - self.start_time) if self.start_time else 0
            message = _("time_used", time=elapsed)
        else:
            title = _("game_over")
            message = _("hit_mine")

        dialog = Adw.AlertDialog(
            heading=title,
            body=message
        )
        dialog.add_response("ok", _("ok"))
        dialog.set_default_response("ok")
        dialog.present(self.widget.get_root())

    def start_timer(self):
        """启动计时器"""
        def update_timer():
            if self.game_over or self.game_won or self.start_time is None:
                return False
            elapsed = int(time.time() - self.start_time)
            self.time_label.set_label(f"⏱ {elapsed}")
            return True

        GLib.timeout_add(1000, update_timer)

    def stop(self):
        """停止游戏"""
        self.game_over = True
